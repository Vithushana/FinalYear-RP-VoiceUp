import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:async';
import 'package:flutter/foundation.dart' show kIsWeb;
import '../widgets/user_avatar.dart';
import '../screens/profile_screen.dart';
import '../screens/notifications_screen.dart';
import '../services/api_service.dart';

class CustomAppBar extends StatefulWidget implements PreferredSizeWidget {
  final String title;

  const CustomAppBar({
    super.key,
    required this.title,
  });

  @override
  State<CustomAppBar> createState() => _CustomAppBarState();

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);
}

class _CustomAppBarState extends State<CustomAppBar> {
  String _userName = 'User';
  int _unreadCount = 0;
  Timer? _timer;
  
  @override
  void initState() {
    super.initState();
    _loadUserName();
    _loadUnreadCount();
    // Update unread count every 15 seconds
    _timer = Timer.periodic(const Duration(seconds: 15), (timer) {
      _loadUnreadCount();
    });
  }
  
  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  Future<void> _loadUserName() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _userName = prefs.getString('user_name') ?? 'User';
    });
  }

  void _navigateToProfile() {
    Navigator.of(context).push(
      MaterialPageRoute(builder: (context) => const ProfileScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return AppBar(
      title: Text(widget.title),
      backgroundColor: Colors.indigo,
      actions: [
        // Notification Bell Icon with Badge
        Stack(
          children: [
            IconButton(
              icon: const Icon(Icons.notifications),
              onPressed: () {
                Navigator.of(context).push(
                  MaterialPageRoute(builder: (context) => const NotificationsScreen()),
                );
              },
            ),
            // Red dot badge for unread notifications
            if (_unreadCount > 0)
              Positioned(
                right: 8,
                top: 8,
                child: Container(
                  padding: const EdgeInsets.all(4),
                  decoration: const BoxDecoration(
                    color: Colors.red,
                    shape: BoxShape.circle,
                  ),
                  constraints: const BoxConstraints(
                    minWidth: 16,
                    minHeight: 16,
                  ),
                  child: Text(
                    _unreadCount > 9 ? '9+' : _unreadCount.toString(),
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ),
              ),
          ],
        ),
        // Profile Avatar
        Padding(
          padding: const EdgeInsets.only(right: 16.0, left: 8.0),
          child: UserAvatar(
            name: _userName,
            size: 36,
            onTap: _navigateToProfile,
          ),
        ),
      ],
    );
  }
  
  Future<void> _loadUnreadCount() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final userId = prefs.getString('userId');
      if (userId == null) return;
      
      final response = await http.get(
        Uri.parse('${ApiService.baseUrl}/notifications/$userId'),
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final notifications = data['data']['notifications'] as List;
        final count = notifications.where((n) => n['read'] == false).length;
        
        if (mounted) {
          setState(() {
            _unreadCount = count;
          });
        }
      }
    } catch (e) {
      print('Error getting unread count: $e');
    }
  }
}
