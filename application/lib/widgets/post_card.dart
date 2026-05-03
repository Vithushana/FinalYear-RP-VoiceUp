import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:typed_data';
import 'dart:convert';
import 'package:url_launcher/url_launcher.dart';
import 'package:share_plus/share_plus.dart';
import 'package:image_picker/image_picker.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_service.dart';
class PostCard extends StatefulWidget {
  final Map<String, dynamic> post;
  final VoidCallback? onUpdate;
  
  const PostCard({super.key, required this.post, this.onUpdate});
  @override
  State<PostCard> createState() => _PostCardState();
}
class _PostCardState extends State<PostCard> {
  final ApiService _api = ApiService();
  bool isLiked = false;
  late int likeCount;
  late int commentCount;
  late int shareCount;
  
  // Comment input state
  final TextEditingController _commentController = TextEditingController();
  String? _selectedCommentImage;
  
  @override
  void initState() {
    super.initState();
    likeCount = widget.post['like_count'] ?? 0;
    commentCount = widget.post['comment_count'] ?? 0;
    shareCount = widget.post['share_count'] ?? 0;
    _checkIfLiked(); // Check if user has already liked this post
  }
  
  @override
  void dispose() {
    _commentController.dispose();
    super.dispose();
  }
  
  // Check if current user has liked this post
  Future<void> _checkIfLiked() async {
    try {
      final response = await _api.checkLike(widget.post['id']);
      if (mounted) {
        setState(() {
          isLiked = response['data']['liked'] ?? false;
        });
      }
    } catch (e) {
      print('Error checking like status: $e');
    }
  }
  
  // Get avatar icon based on avatar_type
  IconData _getAvatarIcon(String? avatarType) {
    switch (avatarType) {
      case 'male_1':
      case 'female_1':
        return Icons.person;
      case 'male_2':
      case 'female_2':
        return Icons.person_outline;
      case 'male_3':
      case 'female_3':
        return Icons.account_circle;
      default:
        return Icons.person;
    }
  }
  
  // Get avatar color based on avatar_type
  Color _getAvatarColor(String? avatarType) {
    switch (avatarType) {
      case 'male_1':
        return Colors.blue;
      case 'male_2':
        return Colors.indigo;
      case 'male_3':
        return Colors.cyan;
      case 'female_1':
        return Colors.pink;
      case 'female_2':
        return Colors.purple;
      case 'female_3':
        return Colors.deepPurple;
      default:
        return Colors.blue;
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
  Future<void> _toggleLike() async {
    try {
      final response = await _api.toggleLike(widget.post['id']);
      setState(() {
        isLiked = response['data']['liked'];
        likeCount = response['data']['like_count'];
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    }
  }
  Future<void> _showComments() async {
    try {
      final response = await _api.getComments(widget.post['id']);
      final comments = response['data']['comments'] as List;
      
      showModalBottomSheet(
        context: context,
        isScrollControlled: true,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        ),
        builder: (context) => DraggableScrollableSheet(
          initialChildSize: 0.7,
          minChildSize: 0.5,
          maxChildSize: 0.95,
          expand: false,
          builder: (context, scrollController) => Column(
            children: [
              // Header
              Container(
                padding: EdgeInsets.all(16),
                decoration: BoxDecoration(
                  border: Border(bottom: BorderSide(color: Colors.grey[300]!)),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('Comments ($commentCount)', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                    IconButton(icon: Icon(Icons.close), onPressed: () => Navigator.pop(context)),
                  ],
                ),
              ),
              
              // Comments list
              Expanded(
                child: comments.isEmpty
                    ? Center(child: Text('No comments yet'))
                    : ListView.builder(
                        controller: scrollController,
                        itemCount: comments.length,
                        itemBuilder: (context, index) {
                          final comment = comments[index];
                          final isOfficer = comment['is_officer'] == true;
                          
                          return Container(
                            margin: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                            decoration: BoxDecoration(
                              color: isOfficer ? Colors.blue[50] : Colors.transparent,
                              borderRadius: BorderRadius.circular(8),
                              border: isOfficer ? Border.all(color: Colors.blue[200]!, width: 1) : null,
                            ),
                            child: ListTile(
                              leading: CircleAvatar(
                                backgroundColor: isOfficer ? Colors.blue : Colors.grey,
                                child: Icon(
                                  isOfficer ? Icons.verified_user : Icons.person,
                                  color: Colors.white,
                                  size: 20,
                                ),
                              ),
                              title: Row(
                                children: [
                                  Flexible(
                                    child: Text(
                                      comment['username'] ?? 'Unknown',
                                      style: TextStyle(
                                        fontWeight: FontWeight.bold,
                                        color: isOfficer ? Colors.blue[900] : Colors.black,
                                      ),
                                    ),
                                  ),
                                  if (isOfficer) ...[
                                    SizedBox(width: 6),
                                    Container(
                                      padding: EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                      decoration: BoxDecoration(
                                        color: Colors.blue,
                                        borderRadius: BorderRadius.circular(4),
                                      ),
                                      child: Text(
                                        'OFFICER',
                                        style: TextStyle(
                                          color: Colors.white,
                                          fontSize: 10,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                    ),
                                  ],
                                ],
                              ),
                              subtitle: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  SizedBox(height: 4),
                                  Text(
                                    comment['text'] ?? '',
                                    style: TextStyle(
                                      color: isOfficer ? Colors.blue[800] : Colors.black87,
                                    ),
                                  ),
                                  // Display comment image if present (officer replies or user reposts)
                                  if (comment['image'] != null && comment['image'].toString().isNotEmpty) ...[
                                    SizedBox(height: 8),
                                    ClipRRect(
                                      borderRadius: BorderRadius.circular(8),
                                      child: Image.memory(
                                        _getImageBytes(comment['image'])!,
                                        width: double.infinity,
                                        fit: BoxFit.cover,
                                        errorBuilder: (context, error, stackTrace) {
                                          return Container(
                                            height: 100,
                                            color: Colors.grey[300],
                                            child: Icon(Icons.broken_image, color: Colors.grey[600]),
                                          );
                                        },
                                      ),
                                    ),
                                  ],
                                ],
                              ),
                            ),
                          );
                        },
                      ),
              ),
              
              // Add comment input
              _buildCommentInput(context),
            ],
          ),
        ),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error loading comments: $e')),
      );
    }
  }
  
  Widget _buildCommentInput(BuildContext context) {
    return StatefulBuilder(
      builder: (context, setModalState) {
        return Container(
          padding: EdgeInsets.all(16),
          decoration: BoxDecoration(
            border: Border(top: BorderSide(color: Colors.grey[300]!)),
          ),
          child: Column(
            children: [
              // Image preview if selected
              if (_selectedCommentImage != null) ...[
                Stack(
                  children: [
                    ClipRRect(
                      borderRadius: BorderRadius.circular(8),
                      child: Image.memory(
                        _getImageBytes(_selectedCommentImage)!,
                        width: double.infinity,
                        height: 150,
                        fit: BoxFit.cover,
                      ),
                    ),
                    Positioned(
                      top: 8,
                      right: 8,
                      child: GestureDetector(
                        onTap: () {
                          setState(() {
                            _selectedCommentImage = null;
                          });
                          setModalState(() {});
                        },
                        child: Container(
                          padding: EdgeInsets.all(4),
                          decoration: BoxDecoration(
                            color: Colors.red,
                            shape: BoxShape.circle,
                          ),
                          child: Icon(Icons.close, color: Colors.white, size: 16),
                        ),
                      ),
                    ),
                  ],
                ),
                SizedBox(height: 8),
              ],
              
              Row(
                children: [
                  // Show image button only for original post author
                  FutureBuilder<bool>(
                    future: _isOriginalAuthor(),
                    builder: (context, snapshot) {
                      if (snapshot.data == true) {
                        return IconButton(
                          icon: Icon(Icons.image, color: Colors.blue),
                          onPressed: () async {
                            final ImagePicker picker = ImagePicker();
                            final XFile? image = await picker.pickImage(source: ImageSource.gallery);
                            if (image != null) {
                              final bytes = await image.readAsBytes();
                              setState(() {
                                _selectedCommentImage = 'data:image/jpeg;base64,${base64Encode(bytes)}';
                              });
                              setModalState(() {});
                            }
                          },
                        );
                      }
                      return SizedBox.shrink();
                    },
                  ),
                  
                  Expanded(
                    child: TextField(
                      controller: _commentController,
                      decoration: InputDecoration(
                        hintText: 'Write a comment...',
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(25)),
                        contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                      ),
                    ),
                  ),
                  
                  IconButton(
                    icon: Icon(Icons.send, color: Colors.blue),
                    onPressed: () async {
                      final text = _commentController.text.trim();
                      if (text.isNotEmpty || _selectedCommentImage != null) {
                        try {
                          final response = await _api.addComment(
                            widget.post['id'],
                            text.isEmpty ? 'Image update' : text,
                            image: _selectedCommentImage,
                          );
                          setState(() {
                            commentCount = response['data']['comment_count'];
                            _commentController.clear();
                            _selectedCommentImage = null;
                          });
                          Navigator.pop(context);
                          _showComments(); // Refresh comments
                        } catch (e) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(content: Text('Error: $e')),
                          );
                        }
                      }
                    },
                  ),
                ],
              ),
            ],
          ),
        );
      },
    );
  }
  
  Future<bool> _isOriginalAuthor() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final currentUserId = prefs.getString('userId');  // Changed from getInt to getString
      if (currentUserId == null) return false;
      
      // Compare as strings since userId is stored as string
      final postUserId = widget.post['user_id']?.toString();
      print('DEBUG: Current user ID: $currentUserId, Post user ID: $postUserId');
      return currentUserId == postUserId;
    } catch (e) {
      print('Error checking if original author: $e');
      return false;
    }
  }
  
  Future<void> _showShareDialog() async {
    final postUrl = 'http://localhost:62627/post/${widget.post['id']}';
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Share Post'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: Icon(Icons.link, color: Colors.blue),
              title: Text('Copy Link'),
              onTap: () {
                Clipboard.setData(ClipboardData(text: postUrl));
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('Link copied to clipboard!')),
                );
                _trackShare();
              },
            ),
            ListTile(
              leading: Icon(Icons.message, color: Colors.green),
              title: Text('Share on WhatsApp'),
              onTap: () async {
                final whatsappUrl = 'https://wa.me/?text=${Uri.encodeComponent("Check out this post: $postUrl")}';
                if (await canLaunchUrl(Uri.parse(whatsappUrl))) {
                  await launchUrl(Uri.parse(whatsappUrl), mode: LaunchMode.externalApplication);
                  Navigator.pop(context);
                  _trackShare();
                } else {
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Could not open WhatsApp')),
                  );
                }
              },
            ),
            ListTile(
              leading: Icon(Icons.share, color: Colors.orange),
              title: Text('Share via...'),
              onTap: () {
                Share.share('Check out this post: $postUrl');
                Navigator.pop(context);
                _trackShare();
              },
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Cancel'),
          ),
        ],
      ),
    );
  }
  Future<void> _trackShare() async {
    try {
      final response = await _api.sharePost(widget.post['id']);
      setState(() {
        shareCount = response['data']['share_count'];
      });
    } catch (e) {
      print('Error tracking share: $e');
    }
  }
  String _formatTime(String isoTime) {
    final time = DateTime.parse(isoTime);
    final now = DateTime.now();
    final diff = now.difference(time);
    
    if (diff.inDays > 0) return '${diff.inDays}d ago';
    if (diff.inHours > 0) return '${diff.inHours}h ago';
    if (diff.inMinutes > 0) return '${diff.inMinutes}m ago';
    return 'Just now';
  }
  @override
  Widget build(BuildContext context) {
    final images = widget.post['images'] as List<dynamic>? ?? [];
    final firstImage = images.isNotEmpty ? images[0] as String : null;
    final imageBytes = _getImageBytes(firstImage);
    
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Author header with avatar
          Padding(
            padding: const EdgeInsets.all(12),
            child: Row(
              children: [
                CircleAvatar(
                  backgroundColor: _getAvatarColor(widget.post['avatar_type']),
                  child: Icon(
                    _getAvatarIcon(widget.post['avatar_type']),
                    color: Colors.white,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        widget.post['display_name'] ?? widget.post['username'] ?? 'Anonymous',
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      Text(
                        _formatTime(widget.post['created_at'] ?? DateTime.now().toIso8601String()),
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          
          const Divider(height: 1),
          
          // Description
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Description:', style: TextStyle(fontSize: 12, color: Colors.grey[600], fontWeight: FontWeight.w500)),
                const SizedBox(height: 4),
                Text(widget.post['description'] ?? '', style: const TextStyle(fontSize: 14, height: 1.4), maxLines: 3, overflow: TextOverflow.ellipsis),
              ],
            ),
          ),
          
          // Image
          imageBytes != null
            ? Image.memory(
                imageBytes,
                width: double.infinity,
                height: 250,
                fit: BoxFit.cover,
                errorBuilder: (context, error, stackTrace) {
                  return Container(
                    width: double.infinity,
                    height: 250,
                    color: Colors.grey[300],
                    child: Icon(Icons.broken_image, size: 50, color: Colors.grey[600]),
                  );
                },
              )
            : Container(width: double.infinity, height: 250, color: Colors.grey[300], child: const Icon(Icons.image, size: 60, color: Colors.grey)),
          // Like, Comment, Share
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                InkWell(
                  onTap: _toggleLike,
                  child: Row(children: [
                    Icon(isLiked ? Icons.favorite : Icons.favorite_border, size: 22, color: isLiked ? Colors.red : Colors.grey[700]), 
                    const SizedBox(width: 6), 
                    Text(likeCount.toString(), style: TextStyle(color: Colors.grey[700]))
                  ]),
                ),
                InkWell(
                  onTap: _showComments,
                  child: Row(children: [
                    Icon(Icons.chat_bubble_outline, size: 22, color: Colors.grey[700]), 
                    const SizedBox(width: 6), 
                    Text(commentCount.toString(), style: TextStyle(color: Colors.grey[700]))
                  ]),
                ),
                InkWell(
                  onTap: _showShareDialog,
                  child: Row(children: [
                    Icon(Icons.share_outlined, size: 22, color: Colors.grey[700]), 
                    const SizedBox(width: 6), 
                    Text(shareCount.toString(), style: TextStyle(color: Colors.grey[700]))
                  ]),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}