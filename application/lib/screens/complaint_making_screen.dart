import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'dart:convert';
import 'package:geolocator/geolocator.dart';
import 'package:geocoding/geocoding.dart';
import '../services/api_service.dart';
import '../utils/location_helper_stub.dart'
    if (dart.library.html) '../utils/location_helper_web.dart';
import './map_picker_screen_sa.dart';

class ComplaintMakingScreen extends StatefulWidget {
  const ComplaintMakingScreen({super.key});

  @override
  State<ComplaintMakingScreen> createState() => _ComplaintMakingScreenState();
}

class _ComplaintMakingScreenState extends State<ComplaintMakingScreen> {
  static const Color darkBlue = Color(0xFF004C89);
  final ApiService _api = ApiService();

  int selectedType = 0; // 0 = Road, 1 = Garbage

  final issueCtrl = TextEditingController();
  final locationCtrl = TextEditingController();

  // Expanded text variables
  final TextEditingController expandedCtrl = TextEditingController();
  bool useExpandedText = false; 
  bool isExpanding = false; 

  // GPS variables
  Position? _currentPosition;
  double? _latitude;
  double? _longitude;
  bool _isSubmitting = false;

  @override
  void initState() {
    super.initState();
    // Don't auto-fetch location - let user tap location button
    // This ensures: 1) Page loads instantly, 2) Fresh permission prompts each time
  }

  @override
  void dispose() {
    issueCtrl.dispose();
    locationCtrl.dispose();
    super.dispose();
  }

  // Get current GPS location - Web-specific implementation
  Future<void> _getCurrentLocation() async {
    if (kIsWeb) {
      // Use browser's native Geolocation API for web
      _getLocationWeb();
    } else {
      // Use Geolocator for mobile
      _getLocationMobile();
    }
  }

  // Web-specific location using browser's Geolocation API
  Future<void> _getLocationWeb() async {
    try {
      print('🌍 [Web Location] Starting browser geolocation request');
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Requesting location permission...'),
            duration: Duration(seconds: 2),
          ),
        );
      }

      // Use the web helper
      LocationHelperWeb.requestLocation(
        (lat, lng) async {
          setState(() {
            _latitude = lat;
            _longitude = lng;
          });
        
          if (lat == 6.9147 && lng == 79.9729) {
            locationCtrl.text = 'SLIIT, New Kandy Road, Malabe';
          } else {
            // Real location - try geocoding
            try {
              final placemarks = await placemarkFromCoordinates(lat, lng);
              
              if (placemarks.isNotEmpty) {
                final place = placemarks.first;
                final address = '${place.street ?? ''}, ${place.locality ?? ''}, ${place.administrativeArea ?? ''}';
                locationCtrl.text = address.trim();
                print('✅ [Web Location] Address: ${address.trim()}');
              } else {
                locationCtrl.text = 'Lat: ${lat.toStringAsFixed(6)}, Lng: ${lng.toStringAsFixed(6)}';
              }
            } catch (e) {
              locationCtrl.text = 'Lat: ${lat.toStringAsFixed(6)}, Lng: ${lng.toStringAsFixed(6)}';
              print('⚠️ [Web Location] Geocoding error: $e');
            }
          }
          
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('✓ Location obtained successfully'),
                duration: Duration(seconds: 2),
                backgroundColor: Colors.green,
              ),
            );
          }
        },
        (errorMsg) {
          print('❌ [Web Location] Error: $errorMsg');
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(errorMsg),
                duration: const Duration(seconds: 4),
                backgroundColor: Colors.red,
              ),
            );
          }
        },
      );
    } catch (e) {
      print('❌ [Web Location] Exception: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Location error: ${e.toString()}'),
            duration: const Duration(seconds: 4),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  // Mobile-specific location using Geolocator
  Future<void> _getLocationMobile() async {
    try {
      print('🌍 [Mobile Location] Starting location request');
      
      // Check if location services are enabled
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Location services are disabled.'),
              duration: Duration(seconds: 3),
            ),
          );
        }
        return;
      }

      // Request permission
      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Location permission denied.'),
                duration: Duration(seconds: 3),
              ),
            );
          }
          return;
        }
      }
      
      if (permission == LocationPermission.deniedForever) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Location permission permanently denied.'),
              duration: Duration(seconds: 3),
            ),
          );
        }
        return;
      }
      
      // Get position
      final position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      );
      
      setState(() {
        _currentPosition = position;
        _latitude = position.latitude;
        _longitude = position.longitude;
      });
      
      // Get address
      try {
        final placemarks = await placemarkFromCoordinates(
          position.latitude,
          position.longitude,
        );
        
        if (placemarks.isNotEmpty) {
          final place = placemarks.first;
          final address = '${place.street ?? ''}, ${place.locality ?? ''}, ${place.administrativeArea ?? ''}';
          locationCtrl.text = address.trim();
        } else {
          locationCtrl.text = 'Lat: ${position.latitude.toStringAsFixed(6)}, Lng: ${position.longitude.toStringAsFixed(6)}';
        }
        
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('✓ Location obtained'),
              duration: Duration(seconds: 2),
              backgroundColor: Colors.green,
            ),
          );
        }
      } catch (e) {
        locationCtrl.text = 'Lat: ${position.latitude.toStringAsFixed(6)}, Lng: ${position.longitude.toStringAsFixed(6)}';
      }
    } catch (e) {
      print('❌ [Mobile Location] Error: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Could not get location: ${e.toString()}'),
            duration: const Duration(seconds: 3),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  void _reset() {
    setState(() => selectedType = 0);
    issueCtrl.clear();
    locationCtrl.clear();
    // Don't auto-fetch location - user can tap location button if needed
  }

  // AI Expansion function 
  Future<void> _expandWithAI() async {
    if (issueCtrl.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Please describe the issue first")),
      );
      return;
    }

    setState(() => isExpanding = true); // Show loader
    try {
      final result = await _api.expandText(issueCtrl.text.trim()); 
      if (result['status'] == 'success') {
        setState(() {
          expandedCtrl.text = result['expanded_text'];
        });
      }
    } catch (e) {
      print("Expansion error: $e");
    } finally {
      setState(() => isExpanding = false);
    }
  }

  Future<void> _submit() async {
    if ( issueCtrl.text.trim().isEmpty || 
        locationCtrl.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please fill all fields')),
      );
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

      // Submit to backend with GPS coordinates
      final response = await _api.submitComplaintPost(
        text: useExpandedText && expandedCtrl.text.isNotEmpty 
              ? expandedCtrl.text 
              : issueCtrl.text.trim(), 
        isExpanded: useExpandedText, 
        location: locationCtrl.text.trim(),
        category: selectedType == 0 ? 'road' : 'garbage',
        latitude: _latitude,
        longitude: _longitude,
      );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Complaint submitted successfully!')),
        );
        Navigator.pop(context);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isSubmitting = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[200],
      body: SafeArea(
        child: SingleChildScrollView(
          child: Center(
            child: Container(
              width: 360,
              margin: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
              padding: const EdgeInsets.fromLTRB(14, 12, 14, 14),
              decoration: BoxDecoration(
                color: Colors.grey[200],
                borderRadius: BorderRadius.circular(14),
                boxShadow: const [
                  BoxShadow(
                    color: Colors.black12,
                    blurRadius: 10,
                    offset: Offset(0, 4),
                  ),
                ],
                border: Border.all(color: Colors.black12),
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  // ====== TOP ROW: "Report an issue" + Road/Garbage toggle
                  Row(
                    children: [
                      const Expanded(
                        child: Text(
                          "Report an issue:",
                          style: TextStyle(
                            fontWeight: FontWeight.w700,
                            color: Colors.black87,
                          ),
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.all(3),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(10),
                          border: Border.all(color: Colors.black12),
                        ),
                        child: Row(
                          children: [
                            _segBtn("Road", selectedType == 0, () {
                              setState(() => selectedType = 0);
                            }),
                            _segBtn("Garbage", selectedType == 1, () {
                              setState(() => selectedType = 1);
                            }),
                          ],
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 12),
/*
=                  ================================ 
=                         Report the issue
=                  ==============================
*/
                  const Align(
                    alignment: Alignment.centerLeft,
                    child: Text(
                      "Report the issue",
                      style: TextStyle(
                        fontWeight: FontWeight.w700,
                        color: Colors.black87,
                      ),
                    ),
                  ),
                  const SizedBox(height: 4),
                  const Align(
                    alignment: Alignment.centerLeft,
                    child: Text(
                      "Describe the issue in detail",
                      style: TextStyle(color: Colors.black54, fontSize: 12),
                    ),
                  ),
                  const SizedBox(height: 6),
                  SizedBox(
                    height: 120,
                    child: TextField(
                      controller: issueCtrl,
                      maxLines: null,
                      expands: true,
                      textAlignVertical: TextAlignVertical.top,
                      decoration: InputDecoration(
                        hintText: "Describe the issue...",
                        filled: true,
                        fillColor: Colors.white,
                        contentPadding: const EdgeInsets.all(12),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(6),
                        ),
                      ),
                    ),
                  ),

                  const SizedBox(height: 6),

/*
=                         =============================================
=                                      Expanded text controls 
=                         ============================================
*/

                  Container(
                    padding: const EdgeInsets.all(8),
                    color: Colors.grey[200],
                    child: Row(
                      children: [
                        ElevatedButton.icon(
                          onPressed: isExpanding ? null : _expandWithAI, // Backend function call
                          icon: isExpanding 
                              ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2))
                              : const Icon(Icons.auto_awesome),
                          label: const Text("Expand with AI"),
                        ),
                        const Spacer(),
                        IconButton(
                          onPressed: () => expandedCtrl.clear(), // Top Re-set logic
                          icon: const Icon(Icons.refresh),
                        ),
                        Checkbox(
                          value: useExpandedText, 
                          onChanged: (val) => setState(() => useExpandedText = val!),
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 10),

                // Expanded text controls preview box  
                  if (expandedCtrl.text.isNotEmpty) 
                    Container(
                      margin: const EdgeInsets.symmetric(vertical: 10),
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.blue[50], 
                        border: Border.all(color: Colors.blue.withOpacity(0.5)),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: const [
                              Icon(Icons.auto_awesome, size: 18, color: Colors.blue),
                              SizedBox(width: 8),
                              Text("AI Refined Evidence Preview:", 
                                  style: TextStyle(fontWeight: FontWeight.bold, color: Colors.blue)),
                            ],
                          ),
                          const SizedBox(height: 8),
                          TextField(
                            controller: expandedCtrl,
                            maxLines: null,
                            readOnly: true, 
                            decoration: const InputDecoration(
                              border: InputBorder.none,
                              isDense: true,
                            ),
                            style: const TextStyle(fontSize: 14, color: Colors.black87),
                          ),
                        ],
                      ),
                    ),

                  const SizedBox(height: 12),

                  // 3. AI EXPANDED TEXT BOX
                  SizedBox(
                    height: 100,
                    child: TextField(
                      controller: expandedCtrl, // AI text inge dhaan fill aagum
                      maxLines: null,
                      expands: true,
                      decoration: InputDecoration(
                        hintText: "Expanded with AI.......",
                        filled: true,
                        fillColor: Colors.grey[100],
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(6)),
                      ),
                    ),
                  ),

                  const SizedBox(height: 12),

/*
=                       =============================================
=                                        Location
=                       =================================================
*/
                  const Align(
                    alignment: Alignment.centerLeft,
                    child: Text(
                      "Pin your Location",
                      style: TextStyle(
                        fontWeight: FontWeight.w700,
                        color: Colors.black87,
                      ),
                    ),
                  ),
                  const SizedBox(height: 6),
                  TextField(
                    controller: locationCtrl,
                    decoration: InputDecoration(
                      hintText: "your location",
                      filled: true,
                      fillColor: Colors.white,
                      contentPadding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 12,
                      ),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(6),
                      ),
                    suffixIcon: IconButton(
                      icon: const Icon(Icons.my_location),
                      onPressed: () async {
                        // 1) First get GPS (so map opens near you)
                        await _getCurrentLocation();

                        if (_latitude == null || _longitude == null) return;

                        // 2) Open map picker
                        final picked = await Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (_) => MapPickerScreenSA(
                              initialLat: _latitude!,
                              initialLng: _longitude!,
                            ),
                          ),
                        );

                        if (picked != null) {
                          // latlong2 LatLng has double latitude/longitude
                          final double lat = picked.latitude;
                          final double lng = picked.longitude;

                          setState(() {
                            _latitude = lat;
                            _longitude = lng;
                            String mapsLink = "https://www.google.com/maps?q=$lat,$lng";
                            locationCtrl.text = mapsLink;
                          });

                          //ONLY Google Maps link (no numeric display)
                          locationCtrl.text =
                              "https://www.google.com/maps?q=${lat.toStringAsFixed(6)},${lng.toStringAsFixed(6)}";
                        }
                      },
                    ),

                    ),
                  ),

                  const SizedBox(height: 14),


/* 
=             ============================ 
=                     Bottom buttons
=             ============================
*/
                  Row(
                    children: [
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: _isSubmitting ? null : _reset,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: darkBlue,
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 12),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(10),
                            ),
                          ),
                          icon: const Icon(Icons.refresh),
                          label: const Text("Re-set"),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: _isSubmitting ? null : _submit,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: darkBlue,
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 12),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(10),
                            ),
                          ),
                          icon: _isSubmitting
                              ? const SizedBox(
                                  width: 16,
                                  height: 16,
                                  child: CircularProgressIndicator(
                                    color: Colors.white,
                                    strokeWidth: 2,
                                  ),
                                )
                              : const Icon(Icons.receipt_long),
                          label: Text(_isSubmitting ? "Submitting..." : "Submit"),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

/*
=                         ==============================================
=                                      Segmented Button Widget 
=                         ============================================== 
*/


  Widget _segBtn(String text, bool selected, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        // width: MediaQuery.of(context).size.width * 0.92,
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
        decoration: BoxDecoration(
          color: selected ? darkBlue : Colors.transparent,
          borderRadius: BorderRadius.circular(8),
        ),
        child: Center(
          child: Text(
            text,
            style: TextStyle(
              fontWeight: FontWeight.w700,
              color: selected ? Colors.white : Colors.grey[600],
            ),
          ),
        ),
      ),
    );
  }

}
