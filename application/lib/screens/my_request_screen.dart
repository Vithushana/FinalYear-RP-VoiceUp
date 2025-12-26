import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_service.dart';
import '../widgets/custom_app_bar.dart';
import '../widgets/post_card.dart';
import 'post_detail_screen.dart';

class MyRequestScreen extends StatefulWidget {
  final int? scrollToPostId;
  
  const MyRequestScreen({super.key, this.scrollToPostId});

  @override
  State<MyRequestScreen> createState() => _MyRequestScreenState();
}

class _MyRequestScreenState extends State<MyRequestScreen> {
  final ApiService _api = ApiService();
  final ScrollController _scrollController = ScrollController();
  List<dynamic> myPosts = [];
  bool loading = true;
  int? highlightedPostId;
  
  @override
  void initState() {
    super.initState();
    _loadMyPosts();
  }
  
  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }
  
  Future<void> _loadMyPosts() async {
    try {
      setState(() => loading = true);
      
      // Get current user ID from SharedPreferences
      final prefs = await SharedPreferences.getInstance();
      final userIdStr = prefs.getString('userId');
      
      if (userIdStr == null) {
        print('No user ID found in SharedPreferences');
        setState(() {
          myPosts = [];
          loading = false;
        });
        return;
      }
      
      final userId = int.parse(userIdStr);
      final response = await _api.getUserPosts(userId);
      setState(() {
        myPosts = response['data']['posts'];
        loading = false;
      });
      
      // Scroll to specific post if scrollToPostId is provided
      if (widget.scrollToPostId != null && myPosts.isNotEmpty) {
        _scrollToPost(widget.scrollToPostId!);
      }
    } catch (e) {
      print('Error loading my posts: $e');
      setState(() => loading = false);
    }
  }
  
  void _scrollToPost(int postId) {
    // Find the index of the post
    final index = myPosts.indexWhere((post) => post['id'] == postId);
    
    if (index != -1) {
      // Highlight the post
      setState(() {
        highlightedPostId = postId;
      });
      
      // Wait for the list to build, then scroll
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (_scrollController.hasClients) {
          // Calculate approximate position (each card is roughly 180 pixels)
          final position = index * 180.0;
          _scrollController.animateTo(
            position,
            duration: const Duration(milliseconds: 600),
            curve: Curves.easeInOut,
          );
          
          // Remove highlight after 3 seconds
          Future.delayed(const Duration(seconds: 3), () {
            if (mounted) {
              setState(() {
                highlightedPostId = null;
              });
            }
          });
        }
      });
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[200],
      appBar: const CustomAppBar(title: 'My Requests'),
      body: loading
          ? Center(child: CircularProgressIndicator())
          : myPosts.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.inbox, size: 64, color: Colors.grey),
                      SizedBox(height: 16),
                      Text(
                        'No requests yet',
                        style: TextStyle(fontSize: 16, color: Colors.grey[600]),
                      ),
                    ],
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _loadMyPosts,
                  child: ListView.builder(
                    controller: _scrollController, // Add scroll controller
                    itemCount: myPosts.length,
                    itemBuilder: (context, index) {
                      final post = myPosts[index];
                      final isHighlighted = highlightedPostId == post['id'];
                      
                      return Container(
                        // Add highlight effect
                        decoration: isHighlighted
                            ? BoxDecoration(
                                border: Border.all(color: Colors.blue, width: 3),
                                borderRadius: BorderRadius.circular(12),
                              )
                            : null,
                        child: Stack(
                          children: [
                            // Use PostCard for consistent display
                            PostCard(post: post),
                            // Status badge overlay
                            Positioned(
                              top: 16,
                              right: 24,
                              child: Container(
                                padding: EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                                decoration: BoxDecoration(
                                  color: _getStatusColor(post['status'] ?? 'pending'),
                                  borderRadius: BorderRadius.circular(20),
                                  boxShadow: [
                                    BoxShadow(
                                      color: Colors.black.withOpacity(0.2),
                                      blurRadius: 4,
                                      offset: Offset(0, 2),
                                    ),
                                  ],
                                ),
                                child: Text(
                                  (post['status'] ?? 'pending').toUpperCase(),
                                  style: TextStyle(
                                    color: Colors.white,
                                    fontWeight: FontWeight.bold,
                                    fontSize: 11,
                                  ),
                                ),
                              ),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
                ),
    );
  }
  
  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'submitted':
        return Colors.grey;
      case 'seen':
      case 'verified':
        return Colors.blue;
      case 'approved':
      case 'completed':
        return Colors.green;
      case 'in_progress':
      case 'in progress':
        return Colors.blue;
      case 'hold':
        return Colors.orange;
      case 'rejected':
      case 'closed':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }
}

