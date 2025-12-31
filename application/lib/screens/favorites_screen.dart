import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'dart:convert';
import 'dart:typed_data';
import 'package:geolocator/geolocator.dart';
import 'package:geocoding/geocoding.dart';
import '../widgets/custom_app_bar.dart';
import '../navigation/bottom_nav_scaffold.dart';
import '../services/api_service.dart';
import '../widgets/location_picker.dart';
import '../utils/location_helper_stub.dart'
    if (dart.library.html) '../utils/location_helper_web.dart';

class FavoritesScreen extends StatefulWidget {
  final List<String>? selectedImages;
  
  const FavoritesScreen({super.key, this.selectedImages});

  @override
  State<FavoritesScreen> createState() => _FavoritesScreenState();
}

class _FavoritesScreenState extends State<FavoritesScreen> {
  final TextEditingController _locationController = TextEditingController();
  final TextEditingController _descriptionController = TextEditingController();
  final ApiService _api = ApiService();

  String? _selectedIssueType; // Road or Garbage
  String? _selectedRoadType; // Only for Road issues
  String? _detectedGarbageType; // Auto-filled for Garbage issues
  bool _isClassifyingGarbage = false; // Loading state for garbage classification
  List<String> _images = [];
  bool _isSubmitting = false;
  bool _isLoadingLocation = true;
  
  // Location variables
  Position? _currentPosition;
  double? _latitude;
  double? _longitude;

  @override
  void initState() {
    super.initState();
    // Initialize with selected images
    if (widget.selectedImages != null) {
      _images = List.from(widget.selectedImages!);
    }
    // Auto-get current location
    _getCurrentLocation();
  }

  @override
  void dispose() {
    _locationController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  // ================== LOCATION METHODS ==================
  Future<void> _getCurrentLocation() async {
    setState(() => _isLoadingLocation = true);
    
    if (kIsWeb) {
      // Web: Use web location helper
      _getLocationWeb();
    } else {
      // Mobile: Use Geolocator
      _getLocationMobile();
    }
  }

  Future<void> _getLocationWeb() async {
    try {
      LocationHelperWeb.requestLocation(
        (lat, lng) async {
          setState(() {
            _latitude = lat;
            _longitude = lng;
          });
          
          if (lat == 6.9147 && lng == 79.9729) {
            setState(() {
              _locationController.text = 'SLIIT, New Kandy Road, Malabe';
              _isLoadingLocation = false;
            });
          } else {
            // Real location - try geocoding
            try {
              final placemarks = await placemarkFromCoordinates(lat, lng);
              if (placemarks.isNotEmpty) {
                final place = placemarks.first;
                final address = '${place.street}, ${place.locality}, ${place.administrativeArea}';
                setState(() {
                  _locationController.text = address;
                });
              } else {
                setState(() {
                  _locationController.text = 'Lat: ${lat.toStringAsFixed(6)}, Lng: ${lng.toStringAsFixed(6)}';
                });
              }
            } catch (e) {
              setState(() {
                _locationController.text = 'Lat: ${lat.toStringAsFixed(6)}, Lng: ${lng.toStringAsFixed(6)}';
              });
            }
            
            setState(() => _isLoadingLocation = false);
          }
        },
        (error) {
          print('Web location error: $error');
          setState(() {
            _locationController.text = 'Could not get location. Please enter manually.';
            _isLoadingLocation = false;
          });
        },
      );
    } catch (e) {
      print('Web location exception: $e');
      setState(() {
        _locationController.text = 'Could not get location. Please enter manually.';
        _isLoadingLocation = false;
      });
    }
  }

  Future<void> _getLocationMobile() async {
    try {
      LocationPermission permission = await Geolocator.requestPermission();
      
      if (permission == LocationPermission.denied || 
          permission == LocationPermission.deniedForever) {
        setState(() {
          _isLoadingLocation = false;
          _locationController.text = 'Location permission denied. Please enter manually.';
        });
        return;
      }
      
      final position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      );
      
      setState(() {
        _currentPosition = position;
        _latitude = position.latitude;
        _longitude = position.longitude;
      });
      
      final placemarks = await placemarkFromCoordinates(
        position.latitude,
        position.longitude,
      );
      
      if (placemarks.isNotEmpty) {
        final place = placemarks.first;
        final address = '${place.street}, ${place.locality}, ${place.administrativeArea}';
        setState(() {
          _locationController.text = address;
        });
      }
    } catch (e) {
      print('Mobile location error: $e');
      setState(() {
        _locationController.text = 'Could not get location. Please enter manually.';
      });
    } finally {
      setState(() => _isLoadingLocation = false);
    }
  }

  Future<void> _showMapPicker() async {
    final result = await showDialog(
      context: context,
      builder: (context) => LocationPickerDialog(
        initialPosition: _currentPosition,
      ),
    );
    
    if (result != null) {
      setState(() {
        _locationController.text = result['address'];
        _latitude = result['lat'];
        _longitude = result['lng'];
      });
    }
  }


  // ================== POST HANDLER ==================
  Future<void> _onPostPressed() async {
    // Validate inputs
    if (_images.isEmpty) {
      _showError('Please select at least one image');
      return;
    }
    
    if (_locationController.text.trim().isEmpty) {
      _showError('Please enter a location');
      return;
    }
    
    // Validate GPS coordinates
    if (_latitude == null || _longitude == null) {
      _showError('Please enable location services and try again');
      return;
    }
    
    if (_selectedIssueType == null) {
      _showError('Please select an issue type (Road or Garbage)');
      return;
    }
    
    // If Road is selected, road type is required
    if (_selectedIssueType == 'Road' && _selectedRoadType == null) {
      _showError('Please select a road issue type');
      return;
    }
    
    if (_descriptionController.text.trim().isEmpty) {
      _showError('Please enter a description');
      return;
    }

    setState(() => _isSubmitting = true);

    try {
      // Extract province and district from location
      String? province;
      String? district;
      
      if (_currentPosition != null) {
        try {
          final placemarks = await placemarkFromCoordinates(
            _currentPosition!.latitude,
            _currentPosition!.longitude,
          );
          if (placemarks.isNotEmpty) {
            final place = placemarks.first;
            province = place.administrativeArea; // Province
            district = place.locality; // District/City
          }
        } catch (e) {
          print('Error getting province/district: $e');
        }
      }
      
      // Submit post to backend with GPS coordinates
    final response = await _api.submitPost(
      title: _selectedIssueType == 'Road' 
          ? '${_selectedRoadType ?? "Road"} - Road Issue'
          : 'Garbage Issue',
      description: _descriptionController.text.trim(),
      location: _locationController.text.trim(),
      latitude: _latitude,
      longitude: _longitude,
      province: province,
      district: district,
      issueType: _selectedIssueType!,
      roadType: _selectedRoadType, // Only set if Road issue
      images: _images,
    );

    print("📦 Response received: ${response.toString()}");

    // CRITICAL FIX: Check for validation failure properly
    if (response['validation_failed'] == true) {
      // Validation failed - show the popup with details
      print("✅ Handling validation failure in UI");
      if (mounted && response['flutter_response'] != null) {
        _showFinalResultPopup(
          response['flutter_response'],
          strikeWarning: response['strike_warning'],
        );
        
        // Send dual notifications if strike was issued
        if (response['strike_notification'] != null && 
            response['strike_notification']['should_send'] == true) {
          _sendStrikeNotifications(
            response['flutter_response'],
            response['strike_notification'],
          );
        }
      }
      setState(() => _isSubmitting = false);
      return;
    }

    // Check if post was approved or rejected (server side logic)
    if (response['data'] == null) {
      print("❌ No data field in response");
      _showError('Invalid response from server');
      setState(() => _isSubmitting = false);
      return;
    }

    final status = response['data']['post']['status'];
      final componentResults = response['data']['component_results'];
      
      if (status == 'submitted') {
        _showSuccessToast('Posted successfully! Awaiting review by officers.');
      } else if (status == 'rejected') {
        // Show flutter_response popup if available
        final flutterResponse = componentResults['flutter_response'];
        if (flutterResponse != null && mounted) {
          _showFinalResultPopup(flutterResponse);
          setState(() => _isSubmitting = false);
          return;
        }
        
        // Fallback to simple error if no flutter_response
        final reason = response['data']['post']['rejection_reason'] ?? 'Post rejected';
        _showError('Post rejected: $reason');
        setState(() => _isSubmitting = false);
        return;
      }

      // Navigate to home after success
      Future.delayed(const Duration(seconds: 2), () {
        if (mounted) {
          Navigator.of(context).pushAndRemoveUntil(
            MaterialPageRoute(builder: (_) => const BottomNavScaffold()),
            (route) => false,
          );
        }
      });

    } catch (e) {
      _showError('Failed to submit post: $e');
      setState(() => _isSubmitting = false);
    }
  }

  void _showSuccessToast(String message) {
    final overlay = Overlay.of(context);
    if (overlay == null) return;

    final overlayEntry = OverlayEntry(
      builder: (context) => Positioned(
        top: 50,
        right: 16,
        child: Material(
          elevation: 4,
          borderRadius: BorderRadius.circular(8),
          color: Colors.transparent,
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(
              color: Colors.green[600],
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.check_circle, color: Colors.white, size: 20),
                const SizedBox(width: 8),
                Text(
                  message,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );

    overlay.insert(overlayEntry);
    Future.delayed(const Duration(seconds: 4), () {
      overlayEntry.remove();
    });
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red[600],
      ),
    );
  }
  
  void _showFinalResultPopup(
    Map<String, dynamic> flutterResponse, {
    Map<String, dynamic>? strikeWarning,
  }) {
    final title = flutterResponse['title'] ?? 'Content Check Result';
    final message = flutterResponse['message'] ?? '';
    final detailedExplanation = flutterResponse['detailed_explanation'] ?? '';
    final whatToDoNext = flutterResponse['what_to_do_next'] ?? '';
    final canProceed = flutterResponse['can_proceed'] ?? false;
    final isStrikeSimulation = flutterResponse['is_strike_simulation'] ?? false;
    
    // Extract strike warning data
    final hasStrike = strikeWarning != null;
    final strikeTitle = strikeWarning?['title'] ?? '';
    final strikeMessage = strikeWarning?['message'] ?? '';
    final strikeDetail = strikeWarning?['detailed_explanation'] ?? '';
    final strikeCount = strikeWarning?['strike_count'] ?? 0;
    final totalViolations = strikeWarning?['total_violations'] ?? 0;
    final blockStatus = strikeWarning?['block_status'] ?? '';
    final violationReason = strikeWarning?['violation_reason'] ?? message;
    
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Icon(
              canProceed ? Icons.check_circle : Icons.cancel_outlined,
              color: canProceed ? Colors.green : Colors.red[700],
              size: 30,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                title,
                style: TextStyle(
                  fontSize: 19,
                  fontWeight: FontWeight.bold,
                  color: canProceed ? Colors.green[700] : Colors.red[800],
                ),
              ),
            ),
          ],
        ),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              // Main rejection reason - prominent display
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: Colors.red[50],
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: Colors.red[200]!, width: 1.5),
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(Icons.error_outline, color: Colors.red[700], size: 24),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Reason for Rejection',
                            style: TextStyle(
                              fontSize: 13,
                              fontWeight: FontWeight.bold,
                              color: Colors.red[900],
                            ),
                          ),
                          const SizedBox(height: 6),
                          Text(
                            violationReason,
                            style: TextStyle(
                              fontSize: 15,
                              fontWeight: FontWeight.w500,
                              color: Colors.grey[800],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              
              if (whatToDoNext.isNotEmpty) ...[
                const SizedBox(height: 14),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.blue[50],
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.blue[300]!, width: 1.5),
                  ),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Icon(Icons.lightbulb_outline, color: Colors.blue[700], size: 22),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'What to do next',
                              style: TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.bold,
                                color: Colors.blue[900],
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              whatToDoNext,
                              style: TextStyle(fontSize: 13, color: Colors.blue[800]),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ],
              
              // STRIKE WARNING DISPLAY - Improved UX
              if (hasStrike) ...[
                const SizedBox(height: 16),
                Divider(color: Colors.grey[300], thickness: 1),
                const SizedBox(height: 14),
                Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: strikeCount == 0 
                          ? [Colors.orange[50]!, Colors.orange[100]!]
                          : strikeCount == 1
                              ? [Colors.red[50]!, Colors.red[100]!]
                              : strikeCount == 2
                                  ? [Colors.red[100]!, Colors.red[200]!]
                                  : [Colors.red[200]!, Colors.red[300]!],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(
                      color: strikeCount == 0 ? Colors.orange[600]! : Colors.red[600]!,
                      width: 2.5,
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: (strikeCount == 0 ? Colors.orange : Colors.red).withOpacity(0.2),
                        blurRadius: 8,
                        offset: const Offset(0, 3),
                      ),
                    ],
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.all(8),
                            decoration: BoxDecoration(
                              color: Colors.white,
                              shape: BoxShape.circle,
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.black.withOpacity(0.1),
                                  blurRadius: 4,
                                ),
                              ],
                            ),
                            child: Icon(
                              strikeCount == 0 ? Icons.warning_amber_rounded : Icons.error_rounded,
                              color: strikeCount == 0 ? Colors.orange[700] : Colors.red[700],
                              size: 26,
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              strikeTitle,
                              style: TextStyle(
                                fontSize: 17,
                                fontWeight: FontWeight.bold,
                                color: strikeCount == 0 ? Colors.orange[900] : Colors.red[900],
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      Container(
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.9),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          strikeDetail,
                          style: TextStyle(
                            fontSize: 13,
                            height: 1.4,
                            color: Colors.grey[800],
                          ),
                        ),
                      ),
                      const SizedBox(height: 12),
                      Row(
                        children: [
                          Expanded(
                            child: Container(
                              padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 10),
                              decoration: BoxDecoration(
                                color: Colors.white.withOpacity(0.8),
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: Column(
                                children: [
                                  Text(
                                    'Current Strikes',
                                    style: TextStyle(
                                      fontSize: 11,
                                      color: Colors.grey[600],
                                      fontWeight: FontWeight.w500,
                                    ),
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    '$strikeCount / 3',
                                    style: TextStyle(
                                      fontSize: 18,
                                      fontWeight: FontWeight.bold,
                                      color: strikeCount == 0 ? Colors.orange[800] : Colors.red[800],
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Container(
                              padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 10),
                              decoration: BoxDecoration(
                                color: Colors.white.withOpacity(0.8),
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: Column(
                                children: [
                                  Text(
                                    'Total Violations',
                                    style: TextStyle(
                                      fontSize: 11,
                                      color: Colors.grey[600],
                                      fontWeight: FontWeight.w500,
                                    ),
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    '$totalViolations',
                                    style: TextStyle(
                                      fontSize: 18,
                                      fontWeight: FontWeight.bold,
                                      color: Colors.grey[800],
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
              
              if (isStrikeSimulation) ...[
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: Colors.amber[50],
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.amber[300]!),
                  ),
                  child: Row(
                    children: [
                      Icon(Icons.science, color: Colors.amber[700], size: 18),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          '⚠️ Testing Mode: No actual restrictions applied',
                          style: TextStyle(fontSize: 12, color: Colors.amber[900], fontWeight: FontWeight.w500),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ],
          ),
        ),
        actions: [
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () => Navigator.of(context).pop(),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue[700],
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
                elevation: 2,
              ),
              child: const Text(
                'I Understand',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
            ),
          ),
        ],
      ),
    );
  }

  // Send dual notifications for strikes - Enhanced UX
  void _sendStrikeNotifications(
    Map<String, dynamic> flutterResponse,
    Map<String, dynamic> strikeNotification,
  ) {
    final strikeCount = strikeNotification['strike_count'] ?? 0;
    final strikeLevel = strikeNotification['strike_level'] ?? '';
    
    // Notification 1: Post rejection with icon
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            const Icon(Icons.cancel, color: Colors.white, size: 24),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Post Rejected',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    flutterResponse['message'] ?? 'Please review and try again',
                    style: const TextStyle(fontSize: 13),
                  ),
                ],
              ),
            ),
          ],
        ),
        backgroundColor: Colors.red[700],
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        duration: const Duration(seconds: 3),
        margin: const EdgeInsets.all(16),
      ),
    );
    
    // Notification 2: Strike warning with enhanced styling
    Future.delayed(const Duration(milliseconds: 600), () {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Row(
              children: [
                Icon(
                  strikeCount == 0 ? Icons.warning_amber_rounded : Icons.error_rounded,
                  color: Colors.white,
                  size: 26,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        strikeNotification['title'] ?? 'Strike Issued',
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 15,
                        ),
                      ),
                      const SizedBox(height: 3),
                      Text(
                        strikeNotification['message'] ?? '',
                        style: const TextStyle(fontSize: 13),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ),
                ),
              ],
            ),
            backgroundColor: strikeCount == 0 ? Colors.orange[700] : Colors.red[800],
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            duration: const Duration(seconds: 5),
            margin: const EdgeInsets.all(16),
            action: SnackBarAction(
              label: 'View',
              textColor: Colors.white,
              onPressed: () {},
            ),
          ),
        );
      }
    });
  }

  // Helper to convert base64 to bytes
  Uint8List _getImageBytes(String base64String) {
    // Remove data:image/jpeg;base64, prefix if present
    final base64Data = base64String.split(',').last;
    return base64Decode(base64Data);
  }

  // Improved image preview dialog
  Future<bool?> _showImagePreview(Uint8List imageBytes) async {
    return showDialog<bool>(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return Dialog(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // Image preview - directly use memory
              Container(
                constraints: const BoxConstraints(maxHeight: 400),
                child: Image.memory(
                  imageBytes,
                  fit: BoxFit.contain,
                ),
              ),
              
              const SizedBox(height: 16),
              
              // OK and Redo buttons
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: Row(
                  children: [
                    Expanded(
                      child: ElevatedButton.icon(
                        onPressed: () => Navigator.pop(context, false),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.grey[300],
                          foregroundColor: Colors.black,
                          padding: const EdgeInsets.symmetric(vertical: 12),
                        ),
                        icon: const Icon(Icons.refresh),
                        label: const Text('Redo'),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: ElevatedButton.icon(
                        onPressed: () => Navigator.pop(context, true),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF004C89),
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 12),
                        ),
                        icon: const Icon(Icons.check),
                        label: const Text('OK'),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    const Color borderColor = Color(0xFFCBD5E1);
    const Color darkBlue = Color(0xFF004C89);

    return Scaffold(
      backgroundColor: Colors.grey[200],
      appBar: const CustomAppBar(title: 'Voice Up'),
      body: SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // ================= UPLOADED PHOTOS TITLE =================
                  const Text(
                    'Uploaded Photos',
                    style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600),
                  ),
                  const SizedBox(height: 8),

                  // ================= BIG PHOTO PREVIEW =================
                  ClipRRect(
                    borderRadius: BorderRadius.circular(14),
                    child: Container(
                      height: 150,
                      width: double.infinity,
                      color: Colors.grey[300],
                      child: _images.isNotEmpty
                          ? Image.memory(
                              _getImageBytes(_images[0]),
                              fit: BoxFit.cover,
                            )
                          : const Icon(Icons.image, size: 40, color: Colors.grey),
                    ),
                  ),

                  const SizedBox(height: 8),

                  // ================= SMALL PHOTOS + ADD MORE =================
                  Row(
                    children: [
                      if (_images.length > 1)
                        _buildSmallPhoto(_images[1]),
                      if (_images.length > 1)
                        const SizedBox(width: 8),
                      if (_images.length > 2)
                        _buildSmallPhoto(_images[2]),
                      if (_images.length > 2)
                        const SizedBox(width: 8),

                      // + Add more button
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: () {
                            // TODO: Add more images
                            _showError('Add more images feature coming soon!');
                          },
                          style: OutlinedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(vertical: 16),
                            side: const BorderSide(color: borderColor),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(10),
                            ),
                          ),
                          icon: const Icon(Icons.add),
                          label: Text('Add more (${_images.length})'),
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 20),

                  // ================= LOCATION FIELD =================
                  _buildLabelWithDot('Location'),
                  const SizedBox(height: 6),
                  TextField(
                    controller: _locationController,
                    decoration: InputDecoration(
                      hintText: _isLoadingLocation ? 'Getting your location...' : 'Location',
                      filled: true,
                      fillColor: Colors.white,
                      prefixIcon: _isLoadingLocation 
                          ? const Padding(
                              padding: EdgeInsets.all(12.0),
                              child: SizedBox(
                                width: 20,
                                height: 20,
                                child: CircularProgressIndicator(strokeWidth: 2),
                              ),
                            )
                          : null,
                      suffixIcon: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          // GPS button
                          IconButton(
                            icon: const Icon(Icons.my_location, color: Colors.blue),
                            onPressed: _isLoadingLocation ? null : _getCurrentLocation,
                            tooltip: 'Use current location',
                          ),
                          // Map picker button
                          IconButton(
                            icon: const Icon(Icons.map, color: Colors.green),
                            onPressed: _showMapPicker,
                            tooltip: 'Pick from map',
                          ),
                        ],
                      ),
                      contentPadding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 12,
                      ),
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(10),
                        borderSide: const BorderSide(color: borderColor),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(10),
                        borderSide: const BorderSide(color: darkBlue, width: 1.5),
                      ),
                    ),
                  ),

                  const SizedBox(height: 16),

                  // ================= ISSUE TYPE DROPDOWN (Road/Garbage) =================
                  const Text(
                    'Issue type',
                    style: TextStyle(fontSize: 14, fontWeight: FontWeight.w500),
                  ),
                  const SizedBox(height: 6),
                  DropdownButtonFormField<String>(
                    value: _selectedIssueType,
                    decoration: InputDecoration(
                      hintText: 'Select issue type...',
                      filled: true,
                      fillColor: Colors.white,
                      contentPadding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 12,
                      ),
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(10),
                        borderSide: const BorderSide(color: borderColor),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(10),
                        borderSide: const BorderSide(color: darkBlue, width: 1.5),
                      ),
                    ),
                    items: const [
                      DropdownMenuItem(value: 'Road', child: Text('Road')),
                      DropdownMenuItem(value: 'Garbage', child: Text('Garbage')),
                    ],
                    onChanged: (value) async {
                      setState(() {
                        _selectedIssueType = value;
                        // Clear road type if switching away from Road
                        if (value != 'Road') {
                          _selectedRoadType = null;
                        }
                        // Clear garbage type if switching away from Garbage
                        if (value != 'Garbage') {
                          _detectedGarbageType = null;
                        }
                      });
                      
                      // Auto-classify garbage type when Garbage is selected
                      if (value == 'Garbage' && _images.isNotEmpty) {
                        setState(() => _isClassifyingGarbage = true);
                        try {
                          final result = await _api.classifyGarbage(_images.first);
                          if (mounted && result['success']) {
                            setState(() {
                              _detectedGarbageType = result['data']['garbage_type'];
                              _isClassifyingGarbage = false;
                            });
                            
                            // Show success message
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(
                                content: Text('Detected: ${result['data']['garbage_type']}'),
                                backgroundColor: Colors.green[600],
                                duration: const Duration(seconds: 2),
                              ),
                            );
                          }
                        } catch (e) {
                          print('Garbage classification failed: $e');
                          if (mounted) {
                            setState(() => _isClassifyingGarbage = false);
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(
                                content: Text('Could not detect garbage type automatically'),
                                backgroundColor: Colors.orange[600],
                              ),
                            );
                          }
                        }
                      }
                    },
                  ),

                  // ================= ROAD TYPE DROPDOWN (Only if Road selected) =================
                  if (_selectedIssueType == 'Road') ...[
                    const SizedBox(height: 16),
                    const Text(
                      'Road issue type',
                      style: TextStyle(fontSize: 14, fontWeight: FontWeight.w500),
                    ),
                    const SizedBox(height: 6),
                    DropdownButtonFormField<String>(
                      value: _selectedRoadType,
                      decoration: InputDecoration(
                        hintText: 'Select road issue type...',
                        filled: true,
                        fillColor: Colors.white,
                        contentPadding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 12,
                        ),
                        enabledBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(10),
                          borderSide: const BorderSide(color: borderColor),
                        ),
                        focusedBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(10),
                          borderSide: const BorderSide(color: darkBlue, width: 1.5),
                        ),
                      ),
                      items: const [
                        DropdownMenuItem(value: 'Potholes', child: Text('Potholes')),
                        DropdownMenuItem(value: 'Cracks', child: Text('Cracks')),
                        DropdownMenuItem(
                          value: 'Erosion Damage',
                          child: Text('Erosion Damage'),
                        ),
                        DropdownMenuItem(
                          value: 'Alligator Cracks',
                          child: Text('Alligator Cracks'),
                        ),
                        DropdownMenuItem(
                          value: 'Transverse Cracks',
                          child: Text('Transverse Cracks'),
                        ),
                      ],
                      onChanged: (value) {
                        setState(() {
                          _selectedRoadType = value;
                        });
                      },
                    ),
                  ],

                  // ================= GARBAGE TYPE FIELD (Only if Garbage selected) =================
                  if (_selectedIssueType == 'Garbage') ...[
                    const SizedBox(height: 16),
                    const Text(
                      'Detected Garbage Type',
                      style: TextStyle(fontSize: 14, fontWeight: FontWeight.w500),
                    ),
                    const SizedBox(height: 6),
                    TextField(
                      readOnly: true,
                      decoration: InputDecoration(
                        hintText: _isClassifyingGarbage 
                            ? 'Detecting garbage type...' 
                            : (_detectedGarbageType ?? 'Select Garbage issue type to detect'),
                        filled: true,
                        fillColor: _detectedGarbageType != null ? Colors.green[50] : Colors.grey[100],
                        prefixIcon: _isClassifyingGarbage
                            ? const Padding(
                                padding: EdgeInsets.all(12.0),
                                child: SizedBox(
                                  width: 20,
                                  height: 20,
                                  child: CircularProgressIndicator(strokeWidth: 2),
                                ),
                              )
                            : Icon(
                                _detectedGarbageType != null ? Icons.check_circle : Icons.recycling,
                                color: _detectedGarbageType != null ? Colors.green : Colors.grey,
                              ),
                        contentPadding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 12,
                        ),
                        enabledBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(10),
                          borderSide: BorderSide(
                            color: _detectedGarbageType != null ? Colors.green : borderColor,
                          ),
                        ),
                        focusedBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(10),
                          borderSide: const BorderSide(color: darkBlue, width: 1.5),
                        ),
                      ),
                      controller: TextEditingController(
                        text: _detectedGarbageType ?? '',
                      ),
                    ),
                  ],

                  const SizedBox(height: 18),

                  // ================= DESCRIPTION FIELD =================
                  const Text(
                    'Description:',
                    style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
                  ),
                  const SizedBox(height: 6),
                  TextField(
                    controller: _descriptionController,
                    maxLines: 4,
                    decoration: InputDecoration(
                      hintText:
                          "broken and needs repair. It's a safety concern for...",
                      filled: true,
                      fillColor: Colors.white,
                      contentPadding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 12,
                      ),
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(10),
                        borderSide: const BorderSide(color: borderColor),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(10),
                        borderSide: const BorderSide(color: darkBlue, width: 1.5),
                      ),
                    ),
                  ),

                  const SizedBox(height: 24),

                  // ================= BUTTONS ROW =================
                  Row(
                    children: [
                      // ---- DRAFT BUTTON ----
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: _isSubmitting ? null : () {
                            _showError('Draft feature coming soon!');
                          },
                          icon: const Icon(
                            Icons.save_outlined,
                            color: Colors.black87,
                          ),
                          label: const Text(
                            "Draft",
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                              color: Colors.black87,
                            ),
                          ),
                          style: OutlinedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(vertical: 14),
                            side: const BorderSide(color: Colors.grey),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                            backgroundColor: Colors.white,
                          ),
                        ),
                      ),

                      const SizedBox(width: 12),

                      // ---- POST BUTTON ----
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: _isSubmitting ? null : _onPostPressed,
                          icon: _isSubmitting
                              ? const SizedBox(
                                  width: 20,
                                  height: 20,
                                  child: CircularProgressIndicator(
                                    color: Colors.white,
                                    strokeWidth: 2,
                                  ),
                                )
                              : const Icon(Icons.send, color: Colors.white),
                          label: Text(
                            _isSubmitting ? "Posting..." : "Post",
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                              color: Colors.white,
                            ),
                          ),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: darkBlue,
                            padding: const EdgeInsets.symmetric(vertical: 14),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
    );
  }

  Widget _buildSmallPhoto(String base64Image) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(10),
      child: Container(
        height: 70,
        width: 70,
        color: Colors.grey[300],
        child: Image.memory(
          _getImageBytes(base64Image),
          fit: BoxFit.cover,
        ),
      ),
    );
  }

  Widget _buildLabelWithDot(String text) {
    return Row(
      children: [
        Text(
          text,
          style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w500),
        ),
        const SizedBox(width: 4),
        const Text('*', style: TextStyle(color: Colors.red, fontSize: 14)),
      ],
    );
  }
}