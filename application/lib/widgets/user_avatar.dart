import 'package:flutter/material.dart';

class UserAvatar extends StatelessWidget {
  final String name;
  final VoidCallback? onTap;
  final double size;

  const UserAvatar({
    super.key,
    required this.name,
    this.onTap,
    this.size = 40,
  });

  String _getInitials() {
    if (name.isEmpty) return 'U';
    
    // Split by spaces and filter out empty strings
    final parts = name.trim().split(RegExp(r'\s+')).where((p) => p.isNotEmpty).toList();
    
    if (parts.length >= 2) {
      // Take first letter of first name and first letter of last name
      return '${parts[0][0]}${parts[parts.length - 1][0]}'.toUpperCase();
    } else if (parts.length == 1 && parts[0].length >= 2) {
      // If single word with 2+ chars, take first two letters
      return parts[0].substring(0, 2).toUpperCase();
    } else if (parts.isNotEmpty) {
      // Single character name
      return parts[0][0].toUpperCase();
    }
    
    return 'U';
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: size,
        height: size,
        decoration: BoxDecoration(
          color: Colors.yellow[700], // Bright yellow color
          shape: BoxShape.circle,
        ),
        child: Center(
          child: Text(
            _getInitials(),
            style: TextStyle(
              color: Colors.white,
              fontSize: size * 0.4,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      ),
    );
  }
}
