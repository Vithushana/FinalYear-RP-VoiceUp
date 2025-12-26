import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../widgets/user_avatar.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  String _userName = '';
  String _userEmail = '';
  String _userPhone = '';
  String _selectedProvince = '';
  String _selectedDistrict = '';
  bool _isLoading = false;
  bool _isEditing = false;
  
  final List<String> _provinces = [
    'Western Province',
    'Central Province',
    'Southern Province',
    'Northern Province',
    'Eastern Province',
    'North Western Province',
    'North Central Province',
    'Uva Province',
    'Sabaragamuwa Province',
  ];
  
  final Map<String, List<String>> _districtsByProvince = {
    'Western Province': ['Colombo', 'Gampaha', 'Kalutara'],
    'Central Province': ['Kandy', 'Matale', 'Nuwara Eliya'],
    'Southern Province': ['Galle', 'Matara', 'Hambantota'],
    'Northern Province': ['Jaffna', 'Kilinochchi', 'Mannar', 'Vavuniya', 'Mullaitivu'],
    'Eastern Province': ['Trincomalee', 'Batticaloa', 'Ampara'],
    'North Western Province': ['Kurunegala', 'Puttalam'],
    'North Central Province': ['Anuradhapura', 'Polonnaruwa'],
    'Uva Province': ['Badulla', 'Monaragala'],
    'Sabaragamuwa Province': ['Ratnapura', 'Kegalle'],
  };

  @override
  void initState() {
    super.initState();
    _loadUserData();
  }

  Future<void> _loadUserData() async {
    final prefs = await SharedPreferences.getInstance();
    
    // Try to load from individual fields first
    String? userName = prefs.getString('user_name');
    String? userEmail = prefs.getString('user_email');
    String? userPhone = prefs.getString('user_phone');
    String? userProvince = prefs.getString('user_province');
    String? userDistrict = prefs.getString('user_district');
    
    // If individual fields are missing, try to load from user JSON object
    if (userName == null || userName == 'User' || userName.isEmpty) {
      final userJson = prefs.getString('user');
      if (userJson != null) {
        try {
          final user = jsonDecode(userJson);
          userName = user['username'] ?? 'User';
          userEmail = user['email'] ?? '';
          userPhone = user['mobile'] ?? '';
          userProvince = user['province'] ?? '';
          userDistrict = user['district'] ?? '';
          
          // Save to individual fields for next time
          await prefs.setString('user_name', userName ?? 'User');
          await prefs.setString('user_email', userEmail ?? '');
          await prefs.setString('user_phone', userPhone ?? '');
          await prefs.setString('user_province', userProvince ?? '');
          await prefs.setString('user_district', userDistrict ?? '');
        } catch (e) {
          print('Error parsing user JSON: $e');
        }
      }
    }
    
    setState(() {
      _userName = userName ?? 'User';
      _userEmail = userEmail ?? '';
      _userPhone = userPhone ?? '';
      _selectedProvince = userProvince ?? '';
      _selectedDistrict = userDistrict ?? '';
    });
  }

  Future<void> _saveLocation() async {
    setState(() => _isLoading = true);

    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('user_province', _selectedProvince);
      await prefs.setString('user_district', _selectedDistrict);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Location updated successfully!'),
            backgroundColor: Colors.green,
          ),
        );
        setState(() => _isEditing = false);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to update location: $e'),
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

  Future<void> _handleLogout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
    
    if (mounted) {
      Navigator.of(context).pushNamedAndRemoveUntil('/login', (route) => false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      resizeToAvoidBottomInset: true,
      appBar: AppBar(
        title: const Text('Profile'),
        backgroundColor: Colors.indigo,
        actions: [
          IconButton(
            icon: const Icon(Icons.edit),
            onPressed: () {
              setState(() => _isEditing = !_isEditing);
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            // Avatar and Name
            UserAvatar(
              name: _userName,
              size: 100,
            ),
            const SizedBox(height: 16),
            Text(
              _userName,
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: Colors.indigo,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              _userEmail,
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey[600],
              ),
            ),
            const SizedBox(height: 32),

            // Personal Information Section
            _buildSectionHeader('Personal Information'),
            const SizedBox(height: 16),
            _buildInfoCard([
              _buildInfoRow(
                icon: Icons.person,
                label: 'Name',
                value: _userName,
              ),
              const Divider(height: 24),
              _buildInfoRow(
                icon: Icons.email,
                label: 'Email',
                value: _userEmail,
              ),
              const Divider(height: 24),
              _buildInfoRow(
                icon: Icons.phone,
                label: 'Phone',
                value: _userPhone,
              ),
            ]),
            const SizedBox(height: 24),

            // Location Section (Editable)
            _buildSectionHeader('Location ${_isEditing ? "(Editing)" : ""}'),
            const SizedBox(height: 16),
            _buildInfoCard([
              if (!_isEditing) ...[
                _buildInfoRow(
                  icon: Icons.location_city,
                  label: 'Province',
                  value: _selectedProvince.isEmpty ? 'Not set' : _selectedProvince,
                ),
                const Divider(height: 24),
                _buildInfoRow(
                  icon: Icons.location_on,
                  label: 'District',
                  value: _selectedDistrict.isEmpty ? 'Not set' : _selectedDistrict,
                ),
              ] else ...[
                // Province Dropdown
                DropdownButtonFormField<String>(
                  value: _selectedProvince.isEmpty ? null : _selectedProvince,
                  decoration: InputDecoration(
                    labelText: 'Province',
                    prefixIcon: const Icon(Icons.location_city),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 16),
                  ),
                  items: _provinces.map((province) {
                    return DropdownMenuItem(
                      value: province,
                      child: Text(province),
                    );
                  }).toList(),
                  onChanged: (value) {
                    setState(() {
                      _selectedProvince = value ?? '';
                      _selectedDistrict = ''; // Reset district
                    });
                  },
                ),
                const SizedBox(height: 16),
                // District Dropdown
                DropdownButtonFormField<String>(
                  value: _selectedDistrict.isEmpty ? null : _selectedDistrict,
                  decoration: InputDecoration(
                    labelText: 'District',
                    prefixIcon: const Icon(Icons.location_on),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 16),
                  ),
                  items: _selectedProvince.isNotEmpty
                      ? _districtsByProvince[_selectedProvince]!.map((district) {
                          return DropdownMenuItem(
                            value: district,
                            child: Text(district),
                          );
                        }).toList()
                      : [],
                  onChanged: _selectedProvince.isNotEmpty
                      ? (value) {
                          setState(() {
                            _selectedDistrict = value ?? '';
                          });
                        }
                      : null,
                ),
                const SizedBox(height: 16),
                // Save Button
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: _isLoading ? null : _saveLocation,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.indigo,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 12),
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
                        : const Text('Save Changes'),
                  ),
                ),
              ],
            ]),
            const SizedBox(height: 32),

            // Logout Button
            SizedBox(
              width: double.infinity,
              child: OutlinedButton(
                onPressed: _handleLogout,
                style: OutlinedButton.styleFrom(
                  foregroundColor: Colors.red,
                  side: const BorderSide(color: Colors.red),
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: const Text(
                  'Logout',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.indigo.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          const Icon(
            Icons.info_outline,
            color: Colors.indigo,
            size: 20,
          ),
          const SizedBox(width: 8),
          Flexible(
            child: Text(
              title,
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: Colors.indigo,
              ),
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInfoCard(List<Widget> children) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: children,
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
                overflow: TextOverflow.ellipsis,
                maxLines: 2,
              ),
            ],
          ),
        ),
      ],
    );
  }
}
