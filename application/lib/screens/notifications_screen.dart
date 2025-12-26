import 'package:flutter/material.dart';
import 'dart:convert';
import '../widgets/custom_app_bar.dart';
import '../services/api_service.dart';
import '../navigation/bottom_nav_scaffold.dart';
import 'package:shared_preferences/shared_preferences.dart';

class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({super.key});

  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  final ApiService _api = ApiService();
  List<dynamic> notifications = [];
  bool loading = true;
  int? userId;

  @override
  void initState() {
    super.initState();
    _loadNotifications();
  }

  Future<void> _loadNotifications() async {
    try {
      setState(() => loading = true);
      
      // Get user ID from SharedPreferences
      final prefs = await SharedPreferences.getInstance();
      final userIdStr = prefs.getString('userId');
      
      if (userIdStr != null) {
        userId = int.tryParse(userIdStr);
      }
      
      // Fallback: try to get from user object
      if (userId == null) {
        final userJson = prefs.getString('user');
        if (userJson != null) {
          try {
            final user = jsonDecode(userJson);
            userId = user['id'];
          } catch (e) {
            print('Error parsing user JSON: $e');
          }
        }
      }
      
      if (userId == null) {
        print('No user ID found');
        setState(() {
          notifications = [];
          loading = false;
        });
        return;
      }
      
      final response = await _api.getNotifications(userId!);
      setState(() {
        notifications = response['data']['notifications'] ?? [];
        loading = false;
      });
    } catch (e) {
      print('Error loading notifications: $e');
      setState(() {
        notifications = [];
        loading = false;
      });
    }
  }

  Future<void> _handleNotificationTap(Map<String, dynamic> notification) async {
    final type = notification['type'] ?? 'info';
    final postId = notification['post_id'];
    
    print('\n🔔 Notification tapped:');
    print('   Type: $type');
    print('   Post ID: $postId');
    
    // Mark as read
    try {
      await _api.markNotificationAsRead(notification['id']);
    } catch (e) {
      print('Error marking notification as read: $e');
    }
    
    // Handle different notification types
    if (type == 'completion_verification' && postId != null) {
      print('   ✅ Showing completion verification dialog');
      // Show completion verification dialog
      _showCompletionVerificationDialog(postId);
    } else if (postId != null) {
      print('   → Navigating to post');
      // Navigate to BottomNavScaffold with scrollToPostId
      // This will automatically switch to My Requests tab and scroll to the post
      if (mounted) {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (_) => BottomNavScaffold(scrollToPostId: postId),
          ),
        );
      }
    }
  }

  String _formatTime(String timestamp) {
    try {
      // Remove 'Z' if present and parse as UTC explicitly
      final cleanTimestamp = timestamp.endsWith('Z') 
          ? timestamp.substring(0, timestamp.length - 1) 
          : timestamp;
      
      // Parse as UTC and convert to local time
      final date = DateTime.parse(cleanTimestamp).toUtc().toLocal();
      final now = DateTime.now();
      final diff = now.difference(date);
      
      if (diff.inMinutes < 1) {
        return 'Just now';
      } else if (diff.inMinutes < 60) {
        return '${diff.inMinutes}m ago';
      } else if (diff.inHours < 24) {
        return '${diff.inHours}h ago';
      } else if (diff.inDays < 7) {
        return '${diff.inDays}d ago';
      } else {
        return '${date.day}/${date.month}/${date.year}';
      }
    } catch (e) {
      print('Error formatting time: $e');
      return '';
    }
  }

  Future<void> _showCompletionVerificationDialog(int postId) async {
    return showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Verify Completion'),
        content: const Text(
          'Has the officer fixed this issue to your satisfaction?',
          style: TextStyle(fontSize: 16),
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              _verifyCompletion(postId, false);
            },
            child: const Text(
              'No, not fixed',
              style: TextStyle(color: Colors.red),
            ),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              _verifyCompletion(postId, true);
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.green,
            ),
            child: const Text('Yes, it\'s fixed'),
          ),
        ],
      ),
    );
  }

  Future<void> _verifyCompletion(int postId, bool verified) async {
    if (userId == null) return;
    
    try {
      await _api.verifyCompletion(postId, userId!, verified);
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            verified
                ? 'Thank you! Your feedback has been sent to the officer.'
                : 'Your feedback has been sent. The officer will review the issue.',
          ),
          backgroundColor: verified ? Colors.green : Colors.orange,
        ),
      );
      
      // Reload notifications
      await _loadNotifications();
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[200],
      appBar: const CustomAppBar(title: "Notifications"),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : notifications.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.notifications_none, size: 64, color: Colors.grey),
                      const SizedBox(height: 16),
                      Text(
                        'No notifications yet',
                        style: TextStyle(fontSize: 16, color: Colors.grey[600]),
                      ),
                    ],
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _loadNotifications,
                  child: ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: notifications.length,
                    itemBuilder: (context, index) {
                      final notification = notifications[index];
                      return _buildNotificationItem(notification);
                    },
                  ),
                ),
    );
  }

  Widget _buildNotificationItem(Map<String, dynamic> notification) {
    final type = notification['type'] ?? 'info';
    final title = notification['title'] ?? '';
    final message = notification['message'] ?? '';
    final time = notification['created_at'] ?? '';
    final isRead = notification['read'] ?? false;
    
    IconData icon;
    Color iconColor;

    switch (type.toLowerCase()) {
      case 'completion_verification':
        icon = Icons.check_circle_outline;
        iconColor = Colors.orange;
        break;
      case 'status_update':
        icon = Icons.update;
        iconColor = Colors.blue;
        break;
      case 'user_verified':
        icon = Icons.verified;
        iconColor = Colors.green;
        break;
      case 'user_rejected':
        icon = Icons.error_outline;
        iconColor = Colors.red;
        break;
      case 'reply':
        icon = Icons.reply;
        iconColor = Colors.green;
        break;
      case 'rejection':
        icon = Icons.cancel; // or Icons.block
        iconColor = Colors.red;
        break;
      case 'officer_reply':
        icon = Icons.support_agent; // or Icons.admin_panel_settings
        iconColor = Colors.blue;
        break;
      case 'comment':
      case 'repost':
        icon = Icons.comment;
        iconColor = Colors.orange;
        break;
      default:
        icon = Icons.notifications;
        iconColor = Colors.grey;
    }

    return GestureDetector(
      onTap: () => _handleNotificationTap(notification),
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: isRead ? Colors.white : Colors.blue[50],
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isRead ? Colors.grey[300]! : Colors.blue[200]!,
            width: 1,
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 4,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Row(
          children: [
            // Icon
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: iconColor.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(
                icon,
                color: iconColor,
                size: 24,
              ),
            ),
            const SizedBox(width: 16),
            // Message and time
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (title.isNotEmpty)
                    Text(
                      title,
                      style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.bold,
                        color: isRead ? Colors.grey[800] : Colors.black,
                      ),
                    ),
                  if (title.isNotEmpty) const SizedBox(height: 4),
                  Text(
                    notification['message'] ?? '',
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: isRead ? FontWeight.normal : FontWeight.w500,
                      color: isRead ? Colors.grey[700] : Colors.black87,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  // Time removed as per user request
                ],
              ),
            ),
            // Unread indicator
            if (!isRead)
              Container(
                width: 8,
                height: 8,
                decoration: const BoxDecoration(
                  color: Colors.blue,
                  shape: BoxShape.circle,
                ),
              ),
          ],
        ),
      ),
    );
  }
}
