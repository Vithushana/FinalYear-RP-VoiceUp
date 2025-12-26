import 'package:flutter/material.dart';
import 'dart:convert';
import '../services/api_service.dart';
import 'anonymous_profile_screen.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ProfileConfirmationScreen extends StatefulWidget {
  final String phoneNumber;
  final Map<String, String> signupData;

  const ProfileConfirmationScreen({
    super.key,
    required this.phoneNumber,
    required this.signupData,
  });

  @override
  State<ProfileConfirmationScreen> createState() => _ProfileConfirmationScreenState();
}

class _ProfileConfirmationScreenState extends State<ProfileConfirmationScreen> {
  bool _isLoading = false;

  Future<void> _handleConfirm() async {
    setState(() => _isLoading = true);

    try {
      // Complete signup with all details via backend
      final response = await ApiService().completeSignup(
        phone: widget.phoneNumber,
        name: widget.signupData['name']!,
        email: widget.signupData['email']!,
        position: widget.signupData['position'],
        province: widget.signupData['province'],  // Include province
        district: widget.signupData['district'],  // Include district
      );

      if (mounted) {
        // Save user data from backend response
        final prefs = await SharedPreferences.getInstance();
        final userData = response['data']['user'];
        final userId = userData['id'];
        
        await prefs.setBool('is_logged_in', true);
        await prefs.setString('user_name', userData['username'] ?? 'User');
        await prefs.setString('user_email', userData['email'] ?? '');
        await prefs.setString('user_phone', userData['mobile'] ?? '');
        await prefs.setString('user_province', userData['province'] ?? '');
        await prefs.setString('user_district', userData['district'] ?? '');
        await prefs.setString('user_position', userData['position'] ?? '');
        await prefs.setString('userId', userData['id']?.toString() ?? '');
        
        // Also save as JSON for other screens
        await prefs.setString('user', jsonEncode(userData));

        // Navigate to anonymous profile selection
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (_) => AnonymousProfileScreen(userId: userId),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(e.toString().replaceAll('Exception: ', '')),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Confirm Profile'),
        backgroundColor: Colors.indigo,
      ),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Icon
                const Icon(
                  Icons.check_circle_outline,
                  size: 80,
                  color: Colors.green,
                ),
                const SizedBox(height: 24),

                // Title
                const Text(
                  'Confirm Your Profile',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                    color: Colors.indigo,
                  ),
                ),
                const SizedBox(height: 12),

                // Subtitle
                const Text(
                  'Please review your information',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey,
                  ),
                ),
                const SizedBox(height: 32),

                // Profile Card
                Card(
                  elevation: 2,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(20.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        _buildInfoRow(
                          icon: Icons.person,
                          label: 'Name',
                          value: widget.signupData['name'] ?? '',
                        ),
                        const Divider(height: 24),
                        _buildInfoRow(
                          icon: Icons.email,
                          label: 'Email',
                          value: widget.signupData['email'] ?? '',
                        ),
                        const Divider(height: 24),
                        _buildInfoRow(
                          icon: Icons.phone,
                          label: 'Phone',
                          value: widget.phoneNumber,
                        ),
                        const Divider(height: 24),
                        _buildInfoRow(
                          icon: Icons.location_city,
                          label: 'Province',
                          value: widget.signupData['province'] ?? '',
                        ),
                        const Divider(height: 24),
                        _buildInfoRow(
                          icon: Icons.location_on,
                          label: 'District',
                          value: widget.signupData['district'] ?? '',
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 32),

                // Confirm Button
                ElevatedButton(
                  onPressed: _isLoading ? null : _handleConfirm,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.indigo,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: _isLoading
                      ? const SizedBox(
                          height: 20,
                          width: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                          ),
                        )
                      : const Text(
                          'Confirm & Create Account',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                ),
                const SizedBox(height: 16),

                // Back Button
                TextButton(
                  onPressed: _isLoading
                      ? null
                      : () {
                          Navigator.of(context).pop();
                        },
                  child: const Text(
                    '← Back to Edit',
                    style: TextStyle(
                      color: Colors.indigo,
                      fontSize: 14,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildInfoRow({
    required IconData icon,
    required String label,
    required String value,
  }) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, color: Colors.indigo, size: 20),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: const TextStyle(
                  fontSize: 12,
                  color: Colors.grey,
                  fontWeight: FontWeight.w500,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                value,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                  color: Colors.black87,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
