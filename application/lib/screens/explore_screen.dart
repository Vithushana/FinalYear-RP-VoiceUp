import 'package:flutter/material.dart';
import 'dart:convert';
import 'dart:typed_data';
import 'package:image_picker/image_picker.dart';
import '../screens/favorites_screen.dart';
import '../screens/complaint_making_screen.dart';
import '../widgets/custom_app_bar.dart';

class ExploreScreen extends StatefulWidget {
  final VoidCallback? onCancel;

  const ExploreScreen({super.key, this.onCancel});

  @override
  State<ExploreScreen> createState() => _ExploreScreenState();
}

class _ExploreScreenState extends State<ExploreScreen> {
  bool isPostSelected = true; // true = POST, false = COMPLAINT

  static const Color darkBlue = Color(0xFF004C89);
  static const Color yellow = Color(0xFFFFD600);
  final ImagePicker _picker = ImagePicker();

  // Camera capture for Live Report
  Future<void> _captureFromCamera() async {
    try {
      final XFile? photo = await _picker.pickImage(
        source: ImageSource.camera,
        imageQuality: 80,
        preferredCameraDevice: CameraDevice.rear,
      );

      if (photo != null) {
        // Show preview with OK/Redo dialog
        final confirmed = await _showImagePreview(photo);
        
        if (confirmed == true) {
          // Convert to base64 and navigate to form
          final bytes = await photo.readAsBytes();
          final base64Image = base64Encode(bytes);
          
          if (mounted) {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => FavoritesScreen(
                  selectedImages: [base64Image],
                ),
              ),
            );
          }
        } else if (confirmed == false) {
          // User clicked Redo - capture again
          _captureFromCamera();
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error capturing image: $e')),
        );
      }
    }
  }

  // Show image preview with OK/Redo buttons
  Future<bool?> _showImagePreview(XFile photo) async {
    return showDialog<bool>(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return Dialog(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // Image preview
              Container(
                constraints: const BoxConstraints(maxHeight: 400),
                child: Image.network(
                  photo.path,
                  fit: BoxFit.contain,
                  errorBuilder: (context, error, stackTrace) {
                    return FutureBuilder<Uint8List>(
                      future: photo.readAsBytes(),
                      builder: (context, snapshot) {
                        if (snapshot.hasData) {
                          return Image.memory(snapshot.data!);
                        }
                        return const CircularProgressIndicator();
                      },
                    );
                  },
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
                          backgroundColor: darkBlue,
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

  // File picker for Upload File
  Future<void> _pickFromGallery() async {
    try {
      final List<XFile> images = await _picker.pickMultiImage(
        imageQuality: 80,
      );

      if (images.isNotEmpty) {
        // Convert all images to base64
        List<String> base64Images = [];
        for (var image in images) {
          final bytes = await image.readAsBytes();
          base64Images.add(base64Encode(bytes));
        }

        if (mounted) {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => FavoritesScreen(
                selectedImages: base64Images,
              ),
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error selecting images: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[200],
      appBar: const CustomAppBar(title: 'Voice Up'),
      body: SafeArea(
        child: SingleChildScrollView(
          child: Column(
            children: [
              const SizedBox(height: 40),

              // ================= POST / COMPLAINT TOGGLE (TOP) =================
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 18),
                child: Container(
                  padding: const EdgeInsets.all(4),
                  decoration: BoxDecoration(
                    color: Colors.grey[300],
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Row(
                    children: [
                      // POST
                      Expanded(
                        child: GestureDetector(
                          onTap: () {
                            setState(() => isPostSelected = true);
                          },
                          child: Container(
                            padding: const EdgeInsets.symmetric(vertical: 10),
                            decoration: BoxDecoration(
                              color: isPostSelected
                                  ? darkBlue
                                  : Colors.transparent,
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Center(
                              child: Text(
                                "POST",
                                style: TextStyle(
                                  fontWeight: FontWeight.w700,
                                  color: isPostSelected
                                      ? Colors.white
                                      : Colors.grey[600],
                                ),
                              ),
                            ),
                          ),
                        ),
                      ),

                      // COMPLAINT
                      Expanded(
                        child: GestureDetector(
                          onTap: () {
                            setState(() => isPostSelected = false);
                          },
                          child: Container(
                            padding: const EdgeInsets.symmetric(vertical: 10),
                            decoration: BoxDecoration(
                              color: !isPostSelected
                                  ? darkBlue
                                  : Colors.transparent,
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Center(
                              child: Text(
                                "COMPLAINT",
                                style: TextStyle(
                                  fontWeight: FontWeight.w700,
                                  color: !isPostSelected
                                      ? Colors.white
                                      : Colors.grey[600],
                                ),
                              ),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 80),

              // ================= MAIN CARD (CHANGES BASED ON TOGGLE) =================
              Center(
                child: Container(
                  width: 320,
                  padding: const EdgeInsets.fromLTRB(20, 24, 20, 16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(18),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.12),
                        blurRadius: 12,
                        offset: const Offset(0, 6),
                      ),
                    ],
                  ),
                  child: isPostSelected ? _buildPostContent() : _buildComplaintContent(),
                ),
              ),
              const SizedBox(height: 40),
            ],
          ),
        ),
      ),
    );
  }

  // POST Content
  Widget _buildPostContent() {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        const Icon(Icons.mic, size: 36, color: darkBlue),
        const SizedBox(height: 12),

        const Text(
          'Voice Up Confidently',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.w700,
            color: darkBlue,
          ),
          textAlign: TextAlign.center,
        ),

        const SizedBox(height: 8),

        const Text(
          'Choose how you want to\ncreate your post.',
          style: TextStyle(
            fontSize: 14,
            color: Colors.black54,
            height: 1.3,
          ),
          textAlign: TextAlign.center,
        ),

        const SizedBox(height: 40),

        // Live Report Button (Camera)
        SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: _captureFromCamera,
            style: ElevatedButton.styleFrom(
              backgroundColor: yellow,
              foregroundColor: Colors.black,
              padding: const EdgeInsets.symmetric(vertical: 12),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(10),
              ),
            ),
            icon: const Icon(Icons.camera_alt),
            label: const Text(
              'Live Report',
              style: TextStyle(
                fontWeight: FontWeight.w600,
                fontSize: 16,
              ),
            ),
          ),
        ),

        const SizedBox(height: 15),

        // Upload File Button (Gallery)
        SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: _pickFromGallery,
            style: ElevatedButton.styleFrom(
              backgroundColor: darkBlue,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 12),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(10),
              ),
            ),
            icon: const Icon(Icons.upload_file),
            label: const Text(
              'Upload File',
              style: TextStyle(
                fontWeight: FontWeight.w600,
                fontSize: 16,
              ),
            ),
          ),
        ),

        const SizedBox(height: 14),

        // Cancel Button
        GestureDetector(
          onTap: widget.onCancel,
          child: Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(vertical: 12),
            decoration: BoxDecoration(
              color: Colors.grey[300],
              borderRadius: BorderRadius.circular(10),
            ),
            child: const Center(
              child: Text(
                'Cancel',
                style: TextStyle(
                  color: Colors.black54,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }

  // COMPLAINT Content
  Widget _buildComplaintContent() {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        const Icon(Icons.report_problem, size: 36, color: darkBlue),
        const SizedBox(height: 12),

        const Text(
          'Report a Complaint',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.w700,
            color: darkBlue,
          ),
          textAlign: TextAlign.center,
        ),

        const SizedBox(height: 8),

        const Text(
          'Report issues that need\nofficial attention.',
          style: TextStyle(
            fontSize: 14,
            color: Colors.black54,
            height: 1.3,
          ),
          textAlign: TextAlign.center,
        ),

        const SizedBox(height: 40),

        // Make Complaint Button
        SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => const ComplaintMakingScreen(),
                ),
              );
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: yellow,
              foregroundColor: Colors.black,
              padding: const EdgeInsets.symmetric(vertical: 12),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(10),
              ),
            ),
            icon: const Icon(Icons.edit),
            label: const Text(
              'Make Complaint',
              style: TextStyle(
                fontWeight: FontWeight.w600,
                fontSize: 16,
              ),
            ),
          ),
        ),

        const SizedBox(height: 14),

        // Cancel Button
        GestureDetector(
          onTap: widget.onCancel,
          child: Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(vertical: 12),
            decoration: BoxDecoration(
              color: Colors.grey[300],
              borderRadius: BorderRadius.circular(10),
            ),
            child: const Center(
              child: Text(
                'Cancel',
                style: TextStyle(
                  color: Colors.black54,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}