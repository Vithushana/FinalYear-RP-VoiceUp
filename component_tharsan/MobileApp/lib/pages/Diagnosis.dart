import 'dart:io';
import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';

class AddRoadDamagePage extends StatefulWidget {
  @override
  _AddRoadDamagePageState createState() => _AddRoadDamagePageState();
}

class _AddRoadDamagePageState extends State<AddRoadDamagePage> {
  String _errorText = "";
  File? _imageFile;
  String _predictedClass = "";
  List<dynamic> _detections = [];
  Map<String, dynamic> _summary = {};
  String _annotatedImageBase64 = "";
  bool _predictionCompleted = false;
  bool _isLoading = false;

  // Variables for ML predictions
  double _totalHours = 0;
  int _totalBudget = 0;
  String _repairTimeSummary = "";
  String _budgetSummary = "";

  // Road damage theme colors
  final Color primaryColor = Color(0xFF2C3E50);  // Dark blue-gray
  final Color secondaryColor = Color(0xFFE67E22); // Orange (construction/road work)
  final Color accentColor = Color(0xFF3498DB);    // Light blue
  final Color backgroundColor = Color(0xFFF5F6FA); // Light gray
  final Color dangerColor = Color(0xFFE74C3C);    // Red for damages
  final Color successColor = Color(0xFF27AE60);   // Green for good condition
  final Color warningColor = Color(0xFFF1C40F);   // Yellow for warnings

  Future<void> _pickImage() async {
    try {
      final pickedFile = await ImagePicker().pickImage(source: ImageSource.gallery);

      if (pickedFile != null) {
        setState(() {
          _imageFile = File(pickedFile.path);
          _predictionCompleted = false;
          _detections = [];
          _summary = {};
          _annotatedImageBase64 = "";
          _errorText = "";
        });

        // Automatically start prediction after image is picked
        await _makePredictionRequest();
      }
    } catch (e) {
      print('Error picking image: $e');
      setState(() {
        _errorText = 'Error picking image: $e';
      });
    }
  }

  Future<void> _makePredictionRequest() async {
    try {
      if (_imageFile == null) {
        print('No image file selected');
        return;
      }

      setState(() {
        _isLoading = true;
        _errorText = "";
        _detections = [];
        _summary = {};
        _annotatedImageBase64 = "";
        _totalHours = 0;
        _totalBudget = 0;
      });

      // Create multipart request for file upload
      var request = http.MultipartRequest(
        'POST',
        Uri.parse('http://10.0.2.2:5000/predict-file'), // Android emulator
        // Uri.parse('http://localhost:5000/predict-file'), // iOS simulator
        // Uri.parse('http://YOUR_ACTUAL_IP:5000/predict-file'), // Physical device
      );

      // Attach the image file
      request.files.add(
        await http.MultipartFile.fromPath(
          'image',
          _imageFile!.path,
          contentType: MediaType('image', 'jpeg'),
        ),
      );

      // Send the request
      var streamedResponse = await request.send();
      var response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        // Parse the response JSON
        final Map<String, dynamic> data = json.decode(response.body);

        setState(() {
          _detections = data['detections'] ?? [];
          _summary = data['summary'] ?? {};
          _annotatedImageBase64 = data['annotated_image'] ?? '';

          // Extract totals from summary
          _totalHours = _summary['total_hours']?.toDouble() ?? 0;
          _totalBudget = _summary['total_budget']?.toInt() ?? 0;

          // Determine overall status
          if (_detections.isNotEmpty) {
            _predictedClass = 'Damage Detected';
          } else {
            _predictedClass = 'No Damage Detected';
          }

          // Generate summary text
          _generateSummaryText();

          _predictionCompleted = true;
          _isLoading = false;
        });

        print('Detections: $_detections');
        print('Summary: $_summary');
      } else {
        setState(() {
          _isLoading = false;
          _errorText = 'Prediction failed with status: ${response.statusCode}';
        });
        print('Prediction request failed with status code: ${response.statusCode}');
      }

    } catch (e) {
      setState(() {
        _isLoading = false;
        _errorText = 'Error making prediction: $e.\nMake sure the API server is running.';
      });
      print('Error making prediction request: $e');
    }
  }

  void _generateSummaryText() {
    if (_detections.isEmpty) {
      _repairTimeSummary = "No repair time estimated";
      _budgetSummary = "No budget estimated";
      return;
    }

    _repairTimeSummary = "Estimated repair time: ${_totalHours.toStringAsFixed(1)} hours";
    _budgetSummary = "Estimated budget: Rs. ${_totalBudget.toStringAsFixed(0)}";
  }

  Future<void> _saveDetection() async {
    try {
      setState(() {
        _errorText = "";
      });

      // Ensure prediction is completed before adding data to Firestore
      if (!_predictionCompleted) {
        setState(() {
          _errorText = 'Please wait for the prediction to complete.';
        });
        return;
      }

      // Check if user is logged in
      User? currentUser = FirebaseAuth.instance.currentUser;
      if (currentUser == null) {
        setState(() {
          _errorText = 'Please log in to save history.';
        });
        return;
      }

      String userId = currentUser.uid;
      DateTime currentDateTime = DateTime.now();

      // Group detections by damage type
      Map<String, int> damageTypeCount = {};
      for (var detection in _detections) {
        String className = detection['class_name'] ?? 'Unknown';
        damageTypeCount[className] = (damageTypeCount[className] ?? 0) + 1;
      }

      // Convert image file to base64 for storage (optional)
      String imageBase64 = '';
      if (_imageFile != null) {
        List<int> imageBytes = await _imageFile!.readAsBytes();
        imageBase64 = base64Encode(imageBytes);
      }

      Map<String, dynamic> roadDamageData = {
        'user_id': userId,
        'overall_status': _predictedClass,
        'detection_count': _detections.length,
        'damage_count': _detections.length,
        'has_damage': _detections.isNotEmpty,
        'damage_type_counts': damageTypeCount,
        'detections': _detections,
        'summary': _summary,
        'total_repair_hours': _totalHours,
        'total_budget': _totalBudget,
        'image_base64': imageBase64, // Store image as base64
        'annotated_image_base64': _annotatedImageBase64,
        'date_time': currentDateTime,
        'timestamp': FieldValue.serverTimestamp(),
      };

      await FirebaseFirestore.instance.collection('road_damage_detections').add(roadDamageData);

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Row(
            children: [
              Icon(Icons.check_circle, color: Colors.white, size: 20),
              SizedBox(width: 8),
              Expanded(child: Text('Damage detection saved to history successfully!')),
            ],
          ),
          backgroundColor: successColor,
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          duration: Duration(seconds: 3),
        ),
      );

      // Reset state after saving
      setState(() {
        _imageFile = null;
        _predictionCompleted = false;
        _detections = [];
        _summary = {};
        _annotatedImageBase64 = "";
        _totalHours = 0;
        _totalBudget = 0;
      });

    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Row(
            children: [
              Icon(Icons.error_outline, color: Colors.white, size: 20),
              SizedBox(width: 8),
              Expanded(child: Text('Error saving detection: $e')),
            ],
          ),
          backgroundColor: dangerColor,
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          duration: Duration(seconds: 3),
        ),
      );
    }
  }

  Widget _buildImageWidget() {
    if (_imageFile != null) {
      return Container(
        height: 180,
        width: double.infinity,
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: secondaryColor.withOpacity(0.3), width: 2),
          boxShadow: [
            BoxShadow(
              color: primaryColor.withOpacity(0.2),
              blurRadius: 8,
              offset: Offset(0, 3),
            ),
          ],
          image: DecorationImage(
            image: FileImage(_imageFile!),
            fit: BoxFit.cover,
          ),
        ),
      );
    } else {
      return Container(
        height: 180,
        width: double.infinity,
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: secondaryColor.withOpacity(0.3), width: 2),
          color: backgroundColor,
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.map, size: 40, color: primaryColor.withOpacity(0.5)),
            SizedBox(height: 8),
            Text(
              'No image selected',
              style: TextStyle(color: primaryColor, fontSize: 14),
            ),
          ],
        ),
      );
    }
  }

  Widget _buildAnnotatedImage() {
    if (_annotatedImageBase64.isNotEmpty) {
      try {
        Uint8List imageBytes = base64Decode(_annotatedImageBase64);
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Annotated Image:',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: primaryColor,
              ),
            ),
            SizedBox(height: 8),
            Container(
              height: 200,
              width: double.infinity,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: secondaryColor.withOpacity(0.3), width: 2),
                boxShadow: [
                  BoxShadow(
                    color: primaryColor.withOpacity(0.2),
                    blurRadius: 8,
                    offset: Offset(0, 3),
                  ),
                ],
                image: DecorationImage(
                  image: MemoryImage(imageBytes),
                  fit: BoxFit.cover,
                ),
              ),
            ),
          ],
        );
      } catch (e) {
        return SizedBox.shrink();
      }
    }
    return SizedBox.shrink();
  }

  Widget _buildRepairSummary() {
    if (_detections.isEmpty) return SizedBox.shrink();

    return Container(
      margin: EdgeInsets.only(top: 16),
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [secondaryColor.withOpacity(0.1), accentColor.withOpacity(0.1)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: secondaryColor.withOpacity(0.3), width: 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.construction, color: secondaryColor, size: 24),
              SizedBox(width: 8),
              Text(
                'Repair Estimate',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: primaryColor,
                ),
              ),
            ],
          ),
          SizedBox(height: 12),
          _buildEstimateRow(
            icon: Icons.timer,
            label: 'Total Time:',
            value: '${_totalHours.toStringAsFixed(1)} hours',
            color: secondaryColor,
          ),
          SizedBox(height: 8),
          _buildEstimateRow(
            icon: Icons.attach_money,
            label: 'Total Budget:',
            value: 'Rs. ${_totalBudget.toStringAsFixed(0)}',
            color: successColor,
          ),
          SizedBox(height: 8),
          Container(
            padding: EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: backgroundColor,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              children: [
                Icon(Icons.info_outline, size: 16, color: primaryColor),
                SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Estimates are based on damage severity and historical repair data',
                    style: TextStyle(
                      fontSize: 11,
                      color: primaryColor,
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEstimateRow({
    required IconData icon,
    required String label,
    required String value,
    required Color color,
  }) {
    return Row(
      children: [
        Container(
          width: 30,
          height: 30,
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(icon, size: 16, color: color),
        ),
        SizedBox(width: 12),
        Text(
          label,
          style: TextStyle(
            fontSize: 14,
            color: Colors.grey.shade700,
          ),
        ),
        Spacer(),
        Text(
          value,
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
      ],
    );
  }

  Color _getDamageTypeColor(String className) {
    if (className.toLowerCase().contains('pothole')) {
      return dangerColor;
    } else if (className.toLowerCase().contains('crack')) {
      return warningColor;
    } else if (className.toLowerCase().contains('rut') ||
        className.toLowerCase().contains('depression')) {
      return Colors.orange;
    } else {
      return accentColor;
    }
  }

  Color _getStatusColor() {
    if (_detections.isEmpty) return successColor;
    return dangerColor;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Icon(Icons.map, color: Colors.white, size: 22),
            SizedBox(width: 8),
            Text(
              'Road Damage Detection',
              style: TextStyle(
                fontWeight: FontWeight.w500,
                fontSize: 18,
              ),
            ),
          ],
        ),
        backgroundColor: primaryColor,
        foregroundColor: Colors.white,
        elevation: 2,
      ),
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              backgroundColor,
              Colors.white,
            ],
          ),
        ),
        child: SingleChildScrollView(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Upload Section
                Container(
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: [
                      BoxShadow(
                        color: primaryColor.withOpacity(0.15),
                        blurRadius: 12,
                        offset: Offset(0, 5),
                      ),
                    ],
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      children: [
                        Container(
                          width: 70,
                          height: 70,
                          decoration: BoxDecoration(
                            gradient: RadialGradient(
                              colors: [
                                secondaryColor.withOpacity(0.3),
                                primaryColor.withOpacity(0.1),
                              ],
                            ),
                            shape: BoxShape.circle,
                          ),
                          child: Icon(
                            Icons.cloud_upload,
                            size: 35,
                            color: secondaryColor,
                          ),
                        ),
                        SizedBox(height: 12),
                        Text(
                          'Upload Road Image',
                          style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                            color: primaryColor,
                          ),
                        ),
                        SizedBox(height: 6),
                        Text(
                          'Select an image to detect road damage and estimate repair costs',
                          textAlign: TextAlign.center,
                          style: TextStyle(color: Colors.grey.shade600, fontSize: 14),
                        ),
                        SizedBox(height: 16),
                        Container(
                          width: double.infinity,
                          height: 48,
                          decoration: BoxDecoration(
                            gradient: LinearGradient(
                              colors: [secondaryColor, primaryColor],
                            ),
                            borderRadius: BorderRadius.circular(12),
                            boxShadow: [
                              BoxShadow(
                                color: primaryColor.withOpacity(0.3),
                                blurRadius: 8,
                                offset: Offset(0, 3),
                              ),
                            ],
                          ),
                          child: ElevatedButton(
                            onPressed: _isLoading ? null : _pickImage,
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.transparent,
                              shadowColor: Colors.transparent,
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                            ),
                            child: _isLoading
                                ? Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                SizedBox(
                                  width: 18,
                                  height: 18,
                                  child: CircularProgressIndicator(
                                    color: Colors.white,
                                    strokeWidth: 2,
                                  ),
                                ),
                                SizedBox(width: 8),
                                Text(
                                  'Processing...',
                                  style: TextStyle(fontSize: 15),
                                ),
                              ],
                            )
                                : Text(
                              'Select & Detect Damage',
                              style: TextStyle(
                                fontSize: 15,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),

                SizedBox(height: 16),

                // Display uploaded image
                if (_imageFile != null) ...[
                  _buildImageWidget(),
                  SizedBox(height: 16),
                ],

                // Display error if any
                if (_errorText.isNotEmpty)
                  Container(
                    padding: EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: dangerColor.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: dangerColor.withOpacity(0.3)),
                    ),
                    child: Row(
                      children: [
                        Icon(Icons.error_outline, color: dangerColor, size: 20),
                        SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            _errorText,
                            style: TextStyle(color: dangerColor, fontSize: 13),
                          ),
                        ),
                      ],
                    ),
                  ),

                // Display prediction results
                if (_predictionCompleted && _detections.isNotEmpty)
                  Container(
                    margin: EdgeInsets.only(top: 8),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      boxShadow: [
                        BoxShadow(
                          color: primaryColor.withOpacity(0.1),
                          blurRadius: 10,
                          offset: Offset(0, 3),
                        ),
                      ],
                    ),
                    child: Padding(
                      padding: EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          // Status Header
                          Container(
                            padding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                            decoration: BoxDecoration(
                              color: _getStatusColor().withOpacity(0.1),
                              borderRadius: BorderRadius.circular(10),
                              border: Border.all(color: _getStatusColor(), width: 1),
                            ),
                            child: Row(
                              children: [
                                Icon(
                                  Icons.warning_amber,
                                  color: _getStatusColor(),
                                  size: 22,
                                ),
                                SizedBox(width: 8),
                                Expanded(
                                  child: Text(
                                    _predictedClass,
                                    style: TextStyle(
                                      fontSize: 16,
                                      fontWeight: FontWeight.bold,
                                      color: _getStatusColor(),
                                    ),
                                  ),
                                ),
                                Container(
                                  padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                  decoration: BoxDecoration(
                                    color: _getStatusColor(),
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                  child: Text(
                                    '${_detections.length} damage${_detections.length > 1 ? 's' : ''}',
                                    style: TextStyle(
                                      color: Colors.white,
                                      fontSize: 12,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),

                          SizedBox(height: 16),

                          // Summary Stats
                          if (_summary.isNotEmpty) ...[
                            Text(
                              'Detection Summary',
                              style: TextStyle(
                                fontSize: 15,
                                fontWeight: FontWeight.bold,
                                color: primaryColor,
                              ),
                            ),
                            SizedBox(height: 10),
                            Wrap(
                              spacing: 8,
                              runSpacing: 8,
                              children: [
                                _buildStatChip(
                                  'Total Damages',
                                  '${_summary['total_count'] ?? 0}',
                                  primaryColor,
                                ),
                                _buildStatChip(
                                  'Est. Hours',
                                  '${_summary['total_hours']?.toStringAsFixed(1) ?? '0'} hrs',
                                  secondaryColor,
                                ),
                                _buildStatChip(
                                  'Est. Budget',
                                  'Rs. ${_summary['total_budget']?.toStringAsFixed(0) ?? '0'}',
                                  successColor,
                                ),
                              ],
                            ),
                            SizedBox(height: 16),
                          ],

                          // Repair Summary
                          _buildRepairSummary(),
                          SizedBox(height: 16),

                          // Individual Detections
                          if (_detections.isNotEmpty) ...[
                            Text(
                              'Individual Damages',
                              style: TextStyle(
                                fontSize: 15,
                                fontWeight: FontWeight.bold,
                                color: primaryColor,
                              ),
                            ),
                            SizedBox(height: 10),
                            ..._detections.map((detection) {
                              Color damageColor = _getDamageTypeColor(detection['class_name']);
                              return Container(
                                margin: EdgeInsets.only(bottom: 8),
                                padding: EdgeInsets.all(12),
                                decoration: BoxDecoration(
                                  color: damageColor.withOpacity(0.05),
                                  borderRadius: BorderRadius.circular(10),
                                  border: Border.all(
                                    color: damageColor.withOpacity(0.3),
                                    width: 1,
                                  ),
                                ),
                                child: Column(
                                  children: [
                                    Row(
                                      children: [
                                        Container(
                                          padding: EdgeInsets.all(6),
                                          decoration: BoxDecoration(
                                            color: damageColor.withOpacity(0.1),
                                            borderRadius: BorderRadius.circular(8),
                                          ),
                                          child: Icon(
                                            Icons.warning,
                                            color: damageColor,
                                            size: 16,
                                          ),
                                        ),
                                        SizedBox(width: 10),
                                        Expanded(
                                          child: Column(
                                            crossAxisAlignment: CrossAxisAlignment.start,
                                            children: [
                                              Text(
                                                detection['class_name'] ?? 'Unknown',
                                                style: TextStyle(
                                                  fontWeight: FontWeight.w600,
                                                  color: primaryColor,
                                                  fontSize: 14,
                                                ),
                                              ),
                                              Text(
                                                'Confidence: ${(detection['confidence'] * 100).toStringAsFixed(1)}%',
                                                style: TextStyle(
                                                  fontSize: 12,
                                                  color: Colors.grey.shade600,
                                                ),
                                              ),
                                            ],
                                          ),
                                        ),
                                      ],
                                    ),
                                    Divider(height: 16, thickness: 1),
                                    Row(
                                      mainAxisAlignment: MainAxisAlignment.spaceAround,
                                      children: [
                                        _buildDamageDetail(
                                          icon: Icons.timer,
                                          label: 'Time',
                                          value: detection['repair_time'] ?? 'N/A',
                                          color: secondaryColor,
                                        ),
                                        _buildDamageDetail(
                                          icon: Icons.attach_money,
                                          label: 'Budget',
                                          value: detection['budget'] ?? 'N/A',
                                          color: successColor,
                                        ),
                                      ],
                                    ),
                                  ],
                                ),
                              );
                            }).toList(),
                          ],

                          // Annotated Image
                          if (_annotatedImageBase64.isNotEmpty) ...[
                            SizedBox(height: 16),
                            _buildAnnotatedImage(),
                          ],

                          SizedBox(height: 16),

                          // Save to History Button
                          Container(
                            width: double.infinity,
                            height: 48,
                            decoration: BoxDecoration(
                              gradient: LinearGradient(
                                colors: [secondaryColor, primaryColor],
                              ),
                              borderRadius: BorderRadius.circular(12),
                              boxShadow: [
                                BoxShadow(
                                  color: primaryColor.withOpacity(0.3),
                                  blurRadius: 8,
                                  offset: Offset(0, 3),
                                ),
                              ],
                            ),
                            child: ElevatedButton(
                              onPressed: _saveDetection,
                              style: ElevatedButton.styleFrom(
                                backgroundColor: Colors.transparent,
                                shadowColor: Colors.transparent,
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(12),
                                ),
                              ),
                              child: Row(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Icon(Icons.save, size: 18),
                                  SizedBox(width: 8),
                                  Text(
                                    'Save to History',
                                    style: TextStyle(
                                      fontSize: 15,
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),

                // No detections message
                if (_predictionCompleted && _detections.isEmpty)
                  Container(
                    margin: EdgeInsets.only(top: 16),
                    padding: EdgeInsets.all(24),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      boxShadow: [
                        BoxShadow(
                          color: primaryColor.withOpacity(0.1),
                          blurRadius: 10,
                          offset: Offset(0, 3),
                        ),
                      ],
                    ),
                    child: Column(
                      children: [
                        Container(
                          width: 70,
                          height: 70,
                          decoration: BoxDecoration(
                            color: successColor.withOpacity(0.1),
                            shape: BoxShape.circle,
                          ),
                          child: Icon(
                            Icons.check_circle,
                            size: 35,
                            color: successColor,
                          ),
                        ),
                        SizedBox(height: 12),
                        Text(
                          'No Damage Detected',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: primaryColor,
                          ),
                        ),
                        SizedBox(height: 6),
                        Text(
                          'The road section appears to be in good condition.\nNo damages were detected in this image.',
                          textAlign: TextAlign.center,
                          style: TextStyle(color: Colors.grey.shade600, fontSize: 13),
                        ),
                      ],
                    ),
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildDamageDetail({
    required IconData icon,
    required String label,
    required String value,
    required Color color,
  }) {
    return Row(
      children: [
        Icon(icon, size: 14, color: color),
        SizedBox(width: 4),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              label,
              style: TextStyle(
                fontSize: 10,
                color: Colors.grey.shade600,
              ),
            ),
            Text(
              value,
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w600,
                color: color,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildStatChip(String label, String value, Color color) {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withOpacity(0.3), width: 0.5),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            '$label: ',
            style: TextStyle(
              color: color,
              fontWeight: FontWeight.w500,
              fontSize: 12,
            ),
          ),
          Text(
            value,
            style: TextStyle(
              color: color,
              fontWeight: FontWeight.bold,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }
}