import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:geolocator/geolocator.dart';
import 'package:geocoding/geocoding.dart';
import '../services/api_service.dart';

class ComplaintMakingScreen extends StatefulWidget {
  const ComplaintMakingScreen({super.key});

  @override
  State<ComplaintMakingScreen> createState() => _ComplaintMakingScreenState();
}

class _ComplaintMakingScreenState extends State<ComplaintMakingScreen> {
  static const Color darkBlue = Color(0xFF004C89);
  final ApiService _api = ApiService();

  int selectedType = 0; // 0 = Road, 1 = Garbage

  final titleCtrl = TextEditingController();
  final issueCtrl = TextEditingController();
  final locationCtrl = TextEditingController();

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
    titleCtrl.dispose();
    issueCtrl.dispose();
    locationCtrl.dispose();
    super.dispose();
  }

  // Get current GPS location - ALWAYS request fresh permission
  Future<void> _getCurrentLocation() async {
    try {
      // ALWAYS request permission (don't check first)
      // This ensures user gets prompted every time they tap location button
      LocationPermission permission = await Geolocator.requestPermission();
      
      if (permission == LocationPermission.denied || 
          permission == LocationPermission.deniedForever) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Location permission denied')),
          );
        }
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
      
      // Get address from coordinates
      final placemarks = await placemarkFromCoordinates(
        position.latitude,
        position.longitude,
      );
      
      if (placemarks.isNotEmpty) {
        final place = placemarks.first;
        final address = '${place.street ?? ''}, ${place.locality ?? ''}, ${place.administrativeArea ?? ''}';
        locationCtrl.text = address.trim();
      }
    } catch (e) {
      print('Error getting location: $e');
    }
  }

  void _reset() {
    setState(() => selectedType = 0);
    titleCtrl.clear();
    issueCtrl.clear();
    locationCtrl.clear();
    // Don't auto-fetch location - user can tap location button if needed
  }

  Future<void> _submit() async {
    if (titleCtrl.text.trim().isEmpty || 
        issueCtrl.text.trim().isEmpty || 
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
      final response = await _api.submitPost(
        title: titleCtrl.text.trim(),
        description: issueCtrl.text.trim(),
        location: locationCtrl.text.trim(),
        latitude: _latitude,
        longitude: _longitude,
        province: province,
        district: district,
        issueType: selectedType == 0 ? 'Road' : 'Garbage',
        images: [], // No images for complaint form
        priority: 'high', // Complaints are high priority
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

                  // ====== Short title
                  const Align(
                    alignment: Alignment.centerLeft,
                    child: Text(
                      "Short title",
                      style: TextStyle(
                        fontWeight: FontWeight.w700,
                        color: Colors.black87,
                      ),
                    ),
                  ),
                  const SizedBox(height: 6),
                  TextField(
                    controller: titleCtrl,
                    decoration: InputDecoration(
                      hintText: "e.g: Broken road near hospital",
                      filled: true,
                      fillColor: Colors.white,
                      contentPadding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 12,
                      ),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(6),
                      ),
                    ),
                  ),

                  const SizedBox(height: 12),

                  // ====== Report the issue
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

                  const SizedBox(height: 12),

                  // ====== Location
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
                        onPressed: _getCurrentLocation,
                      ),
                    ),
                  ),

                  const SizedBox(height: 14),

                  // ====== Bottom buttons
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

  Widget _segBtn(String text, bool selected, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 90,
        padding: const EdgeInsets.symmetric(vertical: 8),
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
