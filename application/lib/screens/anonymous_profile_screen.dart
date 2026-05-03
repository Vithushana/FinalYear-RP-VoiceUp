import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../navigation/bottom_nav_scaffold.dart';

class AnonymousProfileScreen extends StatefulWidget {
  final int userId;
  
  const AnonymousProfileScreen({super.key, required this.userId});

  @override
  State<AnonymousProfileScreen> createState() => _AnonymousProfileScreenState();
}

class _AnonymousProfileScreenState extends State<AnonymousProfileScreen> {
  final ApiService _api = ApiService();
  
  String? _selectedAvatar;
  String? _selectedName;
  bool _isSaving = false;
  
  // Avatar options
  final List<Map<String, dynamic>> _avatars = [
    {'type': 'male_1', 'icon': Icons.person, 'color': Colors.blue, 'label': 'Male 1'},
    {'type': 'male_2', 'icon': Icons.person_outline, 'color': Colors.indigo, 'label': 'Male 2'},
    {'type': 'male_3', 'icon': Icons.account_circle, 'color': Colors.cyan, 'label': 'Male 3'},
    {'type': 'female_1', 'icon': Icons.person, 'color': Colors.pink, 'label': 'Female 1'},
    {'type': 'female_2', 'icon': Icons.person_outline, 'color': Colors.purple, 'label': 'Female 2'},
    {'type': 'female_3', 'icon': Icons.account_circle, 'color': Colors.deepPurple, 'label': 'Female 3'},
  ];
  
  // Display name options
  final List<String> _displayNames = [
    'Albert',
    'Ravi',
    'Saman',
    'Nimal',
    'Kumar',
    'Priya',
    'Sita',
    'Maya',
    'Rani',
    'Lakshmi',
  ];

  Future<void> _saveProfile() async {
    if (_selectedAvatar == null || _selectedName == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select both avatar and name')),
      );
      return;
    }

    setState(() => _isSaving = true);

    try {
      await _api.saveAnonymousProfile(
        userId: widget.userId,
        displayName: _selectedName!,
        avatarType: _selectedAvatar!,
      );

      if (mounted) {
        // Navigate to dashboard
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (_) => const BottomNavScaffold()),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: ${e.toString()}')),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isSaving = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Choose Your Anonymous Profile'),
        backgroundColor: Colors.indigo,
        automaticallyImplyLeading: false, // Prevent back button
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Privacy explanation
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.indigo.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.indigo.withOpacity(0.3)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(Icons.privacy_tip, color: Colors.indigo),
                      const SizedBox(width: 8),
                      const Text(
                        'Privacy Protection',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: Colors.indigo,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  const Text(
                    'For your privacy, select an anonymous name and avatar. This will be shown to everyone except in your profile page. Your real details remain private.',
                    style: TextStyle(fontSize: 14, height: 1.5),
                  ),
                ],
              ),
            ),
            
            const SizedBox(height: 32),
            
            // Avatar selection
            const Text(
              'Select Avatar',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            
            GridView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 3,
                crossAxisSpacing: 16,
                mainAxisSpacing: 16,
                childAspectRatio: 1,
              ),
              itemCount: _avatars.length,
              itemBuilder: (context, index) {
                final avatar = _avatars[index];
                final isSelected = _selectedAvatar == avatar['type'];
                
                return GestureDetector(
                  onTap: () {
                    setState(() => _selectedAvatar = avatar['type']);
                  },
                  child: Container(
                    decoration: BoxDecoration(
                      color: isSelected ? avatar['color'].withOpacity(0.2) : Colors.grey[100],
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(
                        color: isSelected ? avatar['color'] : Colors.grey[300]!,
                        width: isSelected ? 3 : 1,
                      ),
                    ),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          avatar['icon'],
                          size: 48,
                          color: avatar['color'],
                        ),
                        const SizedBox(height: 8),
                        Text(
                          avatar['label'],
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                            color: isSelected ? avatar['color'] : Colors.grey[600],
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
            
            const SizedBox(height: 32),
            
            // Display name selection
            const Text(
              'Select Display Name',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            
            Wrap(
              spacing: 12,
              runSpacing: 12,
              children: _displayNames.map((name) {
                final isSelected = _selectedName == name;
                
                return GestureDetector(
                  onTap: () {
                    setState(() => _selectedName = name);
                  },
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                    decoration: BoxDecoration(
                      color: isSelected ? Colors.indigo : Colors.grey[100],
                      borderRadius: BorderRadius.circular(24),
                      border: Border.all(
                        color: isSelected ? Colors.indigo : Colors.grey[300]!,
                        width: isSelected ? 2 : 1,
                      ),
                    ),
                    child: Text(
                      name,
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                        color: isSelected ? Colors.white : Colors.grey[700],
                      ),
                    ),
                  ),
                );
              }).toList(),
            ),
            
            const SizedBox(height: 40),
            
            // Save button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _isSaving ? null : _saveProfile,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.indigo,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: _isSaving
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(
                          color: Colors.white,
                          strokeWidth: 2,
                        ),
                      )
                    : const Text(
                        'Continue to App',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
              ),
            ),
            
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }
}
