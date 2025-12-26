import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../widgets/post_card.dart';
import '../widgets/custom_app_bar.dart';

class HomeScreen extends StatefulWidget {
  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final ApiService _api = ApiService();
  List<dynamic> posts = [];
  bool loading = true;
  
  @override
  void initState() {
    super.initState();
    _loadPosts();
  }
  
  Future<void> _loadPosts() async {
    try {
      setState(() => loading = true);
      final response = await _api.getAllPosts();
      setState(() {
        posts = response['data']['posts'];
        loading = false;
      });
    } catch (e) {
      print('Error loading posts: $e');
      setState(() => loading = false);
    }
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
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[200],
      appBar: const CustomAppBar(title: 'Voice Up'),
      body: loading
          ? Center(child: CircularProgressIndicator())
          : posts.isEmpty
              ? Center(child: Text('No posts yet'))
              : RefreshIndicator(
                  onRefresh: _loadPosts,
                  child: ListView.builder(
                    itemCount: posts.length,
                    itemBuilder: (context, index) {
                      final post = posts[index];
                      return Stack(
                        children: [
                          PostCard(post: post),
                          // Status badge overlay (same as My Requests page)
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
                      );
                    },
                  ),
                ),
    );
  }
}