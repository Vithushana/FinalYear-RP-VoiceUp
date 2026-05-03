import 'package:flutter/material.dart';

class PoliciesScreen extends StatelessWidget {
  const PoliciesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Privacy & Policies'),
        backgroundColor: Colors.indigo,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Privacy Policy',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Last updated: ${DateTime.now().year}',
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey[600],
              ),
            ),
            const SizedBox(height: 24),
            
            _buildSection(
              'Information We Collect',
              'We collect information you provide directly to us, including:\n\n'
              '• Account information (name, email, phone number)\n'
              '• Profile information\n'
              '• Posts and reports you submit\n'
              '• Location data (when you report issues)\n'
              '• Images and media you upload',
            ),
            
            _buildSection(
              'How We Use Your Information',
              'We use the information we collect to:\n\n'
              '• Provide, maintain, and improve our services\n'
              '• Process and route your reports to relevant authorities\n'
              '• Send you notifications about your reports\n'
              '• Communicate with you about updates and changes\n'
              '• Ensure the security of our platform',
            ),
            
            _buildSection(
              'Information Sharing',
              'We may share your information with:\n\n'
              '• Government authorities and departments (for issue resolution)\n'
              '• Service providers who assist in our operations\n'
              '• Law enforcement when required by law\n\n'
              'We do not sell your personal information to third parties.',
            ),
            
            _buildSection(
              'Data Security',
              'We implement appropriate technical and organizational measures to protect your personal information against unauthorized access, alteration, disclosure, or destruction.',
            ),
            
            _buildSection(
              'Your Rights',
              'You have the right to:\n\n'
              '• Access your personal information\n'
              '• Correct inaccurate data\n'
              '• Request deletion of your data\n'
              '• Opt-out of certain data collection\n'
              '• Export your data',
            ),
            
            _buildSection(
              'Data Retention',
              'We retain your information for as long as necessary to provide our services and comply with legal obligations. You can request deletion of your account at any time.',
            ),
            
            _buildSection(
              'Changes to This Policy',
              'We may update this privacy policy from time to time. We will notify you of any changes by posting the new policy on this page and updating the "Last updated" date.',
            ),
            
            _buildSection(
              'Contact Us',
              'If you have questions about this Privacy Policy, please contact us through the app support section.',
            ),
            
            const SizedBox(height: 32),
          ],
        ),
      ),
    );
  }
  
  Widget _buildSection(String title, String content) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w600,
              color: Colors.indigo,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            content,
            style: const TextStyle(
              fontSize: 15,
              height: 1.5,
            ),
          ),
        ],
      ),
    );
  }
}
