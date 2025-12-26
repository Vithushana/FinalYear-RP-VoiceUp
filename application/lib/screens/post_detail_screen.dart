import 'package:flutter/material.dart';
import 'dart:typed_data';
import 'dart:convert';
import '../services/api_service.dart';
import '../widgets/custom_app_bar.dart';

class PostDetailScreen extends StatefulWidget {
  final int postId;
  
  const PostDetailScreen({super.key, required this.postId});

  @override
  State<PostDetailScreen> createState() => _PostDetailScreenState();
}

class _PostDetailScreenState extends State<PostDetailScreen> {
  final ApiService _api = ApiService();
  Map<String, dynamic>? post;
  List<dynamic> officerReplies = [];
  bool loading = true;
  
  @override
  void initState() {
    super.initState();
    _loadPostDetail();
  }
  
  Future<void> _loadPostDetail() async {
    try {
      setState(() => loading = true);
      final response = await _api.getPostDetail(widget.postId);
      setState(() {
        post = response['data']['post'];
        officerReplies = post!['officer_replies'] ?? [];
        loading = false;
      });
    } catch (e) {
      print('Error loading post detail: $e');
      setState(() => loading = false);
    }
  }
  
  Uint8List? _getImageBytes(String? base64String) {
    if (base64String == null || base64String.isEmpty) return null;
    try {
      final base64Data = base64String.split(',').last;
      return base64Decode(base64Data);
    } catch (e) {
      return null;
    }
  }
  
  @override
  Widget build(BuildContext context) {
    if (loading) {
      return Scaffold(
        appBar: const CustomAppBar(title: 'Post Details'),
        body: Center(child: CircularProgressIndicator()),
      );
    }
    
    if (post == null) {
      return Scaffold(
        appBar: const CustomAppBar(title: 'Post Details'),
        body: Center(child: Text('Post not found')),
      );
    }
    
    final images = post!['images'] as List<dynamic>? ?? [];
    final status = post!['status'] ?? 'pending';
    
    return Scaffold(
      backgroundColor: Colors.grey[200],
      appBar: const CustomAppBar(title: 'Request Details'),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Status badge at top
            Container(
              width: double.infinity,
              padding: EdgeInsets.all(16),
              color: _getStatusColor(status).withOpacity(0.1),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(_getStatusIcon(status), color: _getStatusColor(status)),
                  SizedBox(width: 8),
                  Text(
                    status.toUpperCase(),
                    style: TextStyle(
                      color: _getStatusColor(status),
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                ],
              ),
            ),
            
            // Post content
            Container(
              margin: EdgeInsets.all(16),
              padding: EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Description:',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[600],
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  SizedBox(height: 8),
                  Text(
                    post!['description'] ?? '',
                    style: TextStyle(fontSize: 14, height: 1.4),
                  ),
                  SizedBox(height: 16),
                  
                  // Location
                  Row(
                    children: [
                      Icon(Icons.location_on, size: 20, color: Colors.blue),
                      SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          post!['location'] ?? '',
                          style: TextStyle(fontSize: 14),
                        ),
                      ),
                    ],
                  ),
                  SizedBox(height: 8),
                  
                  // Issue type
                  Row(
                    children: [
                      Icon(Icons.category, size: 20, color: Colors.orange),
                      SizedBox(width: 8),
                      Text(
                        post!['issue_type'] ?? '',
                        style: TextStyle(fontSize: 14),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            
            // Images
            if (images.isNotEmpty)
              Container(
                margin: EdgeInsets.symmetric(horizontal: 16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Uploaded Photos:',
                      style: TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    SizedBox(height: 8),
                    ...images.map((img) {
                      final imageBytes = _getImageBytes(img);
                      return imageBytes != null
                          ? Container(
                              margin: EdgeInsets.only(bottom: 8),
                              child: ClipRRect(
                                borderRadius: BorderRadius.circular(8),
                                child: Image.memory(
                                  imageBytes,
                                  width: double.infinity,
                                  fit: BoxFit.cover,
                                ),
                              ),
                            )
                          : SizedBox.shrink();
                    }).toList(),
                  ],
                ),
              ),
            
            SizedBox(height: 16),
            
            // Status levels
            Container(
              margin: EdgeInsets.symmetric(horizontal: 16),
              padding: EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Status Progress:',
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  SizedBox(height: 16),
                  _buildStatusLevel('Submitted', status),
                  _buildStatusLevel('Seen', status),
                  _buildStatusLevel('Verified', status),
                  _buildStatusLevel('Hold', status),
                  _buildStatusLevel('In Progress', status),
                  _buildStatusLevel('Completed', status),
                  _buildStatusLevel('Closed', status),
                ],
              ),
            ),
            
            SizedBox(height: 16),
            
            // Officer replies
            if (officerReplies.isNotEmpty)
              Container(
                margin: EdgeInsets.symmetric(horizontal: 16),
                padding: EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.admin_panel_settings, color: Colors.blue),
                        SizedBox(width: 8),
                        Text(
                          'Official Replies:',
                          style: TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                    SizedBox(height: 16),
                    ...officerReplies.map((reply) => _buildOfficerReply(reply)).toList(),
                  ],
                ),
              ),
            
            SizedBox(height: 80),
          ],
        ),
      ),
      
      // Bottom buttons
      bottomNavigationBar: Container(
        padding: EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              blurRadius: 8,
              offset: Offset(0, -2),
            ),
          ],
        ),
        child: Row(
          children: [
            Expanded(
              child: OutlinedButton(
                onPressed: () => Navigator.pop(context),
                style: OutlinedButton.styleFrom(
                  padding: EdgeInsets.symmetric(vertical: 12),
                  side: BorderSide(color: Colors.grey),
                ),
                child: Text('Back'),
              ),
            ),
            SizedBox(width: 16),
            Expanded(
              child: ElevatedButton(
                onPressed: () {
                  // TODO: Implement re-tag functionality
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: Color(0xFF004C89),
                  padding: EdgeInsets.symmetric(vertical: 12),
                ),
                child: Text('Re-tag', style: TextStyle(color: Colors.white)),
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildStatusLevel(String level, String currentStatus) {
    final isCompleted = _isStatusCompleted(level, currentStatus);
    final isCurrent = _isCurrentStatus(level, currentStatus);
    
    return Padding(
      padding: EdgeInsets.only(bottom: 12),
      child: Row(
        children: [
          // Blinking circle for current status
          isCurrent
              ? TweenAnimationBuilder(
                  duration: Duration(milliseconds: 1000),
                  tween: Tween<double>(begin: 0.3, end: 1.0),
                  builder: (context, double value, child) {
                    return Opacity(
                      opacity: value,
                      child: Container(
                        width: 20,
                        height: 20,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: Colors.green,
                          boxShadow: [
                            BoxShadow(
                              color: Colors.green.withOpacity(value * 0.5),
                              blurRadius: 8,
                              spreadRadius: 2,
                            ),
                          ],
                        ),
                        child: Icon(Icons.circle, size: 12, color: Colors.white),
                      ),
                    );
                  },
                  onEnd: () {
                    // Restart animation
                    setState(() {});
                  },
                )
              : Container(
                  width: 20,
                  height: 20,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: isCompleted ? Colors.green : Colors.grey[300],
                    border: Border.all(
                      color: isCompleted ? Colors.green : Colors.grey,
                      width: 2,
                    ),
                  ),
                  child: isCompleted
                      ? Icon(Icons.check, size: 12, color: Colors.white)
                      : null,
                ),
          SizedBox(width: 12),
          Text(
            level,
            style: TextStyle(
              fontSize: 14,
              color: (isCompleted || isCurrent) ? Colors.black : Colors.grey,
              fontWeight: (isCompleted || isCurrent) ? FontWeight.bold : FontWeight.normal,
            ),
          ),
        ],
      ),
    );
  }
  
  bool _isStatusCompleted(String level, String currentStatus) {
    final statusOrder = [
      'submitted',
      'seen',
      'verified',
      'hold',
      'in progress',
      'completed',
      'closed',
    ];
    
    final currentIndex = statusOrder.indexOf(currentStatus.toLowerCase().replaceAll('_', ' '));
    final levelIndex = statusOrder.indexOf(level.toLowerCase());
    
    if (currentIndex == -1 || levelIndex == -1) return false;
    return levelIndex < currentIndex;
  }
  
  bool _isCurrentStatus(String level, String currentStatus) {
    return level.toLowerCase() == currentStatus.toLowerCase().replaceAll('_', ' ');
  }
  
  Widget _buildOfficerReply(Map<String, dynamic> reply) {
    return Container(
      margin: EdgeInsets.only(bottom: 16),
      padding: EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.blue[50],
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.blue[200]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              CircleAvatar(
                radius: 16,
                backgroundColor: Colors.blue,
                child: Icon(Icons.admin_panel_settings, size: 16, color: Colors.white),
              ),
              SizedBox(width: 8),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      reply['department'] ?? 'Road Development Authority (RDA)',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 13,
                      ),
                    ),
                    Text(
                      _formatDate(reply['created_at']),
                      style: TextStyle(fontSize: 11, color: Colors.grey[600]),
                    ),
                  ],
                ),
              ),
            ],
          ),
          SizedBox(height: 8),
          Text(
            reply['message'] ?? '',
            style: TextStyle(fontSize: 13, height: 1.4),
          ),
        ],
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
  
  IconData _getStatusIcon(String status) {
    switch (status.toLowerCase()) {
      case 'submitted':
        return Icons.send;
      case 'seen':
      case 'verified':
        return Icons.visibility;
      case 'approved':
      case 'completed':
        return Icons.check_circle;
      case 'in_progress':
      case 'in progress':
        return Icons.hourglass_empty;
      case 'hold':
        return Icons.pause_circle;
      case 'rejected':
      case 'closed':
        return Icons.cancel;
      default:
        return Icons.info;
    }
  }
  
  String _formatDate(String? isoDate) {
    if (isoDate == null) return '';
    try {
      final date = DateTime.parse(isoDate);
      return '${date.day}/${date.month}/${date.year} ${date.hour}:${date.minute.toString().padLeft(2, '0')}';
    } catch (e) {
      return '';
    }
  }
}
