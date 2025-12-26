import 'package:flutter/material.dart';

class TermsScreen extends StatelessWidget {
  const TermsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Terms & Conditions'),
        backgroundColor: Colors.indigo,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Terms & Conditions',
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
              'Acceptance of Terms',
              'By accessing and using Voice Up, you accept and agree to be bound by the terms and provision of this agreement.',
            ),
            
            _buildSection(
              'Use License',
              'Permission is granted to temporarily use Voice Up for personal, non-commercial purposes. This is the grant of a license, not a transfer of title.',
            ),
            
            _buildSection(
              'User Responsibilities',
              'You are responsible for:\n\n'
              '• Maintaining the confidentiality of your account\n'
              '• All activities that occur under your account\n'
              '• Ensuring all information you provide is accurate\n'
              '• Using the service in compliance with all applicable laws',
            ),
            
            _buildSection(
              'Content Guidelines',
              'When posting issues or content, you must:\n\n'
              '• Provide accurate and truthful information\n'
              '• Not post offensive or inappropriate content\n'
              '• Respect the privacy of others\n'
              '• Not misuse the platform for spam or harassment',
            ),
            
            _buildSection(
              'Limitation of Liability',
              'Voice Up shall not be liable for any indirect, incidental, special, consequential or punitive damages resulting from your use or inability to use the service.',
            ),
            
            _buildSection(
              'Changes to Terms',
              'We reserve the right to modify these terms at any time. We will notify users of any material changes via the app or email.',
            ),
            
            _buildSection(
              'Contact Us',
              'If you have any questions about these Terms & Conditions, please contact us through the app support section.',
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
