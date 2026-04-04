import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter/foundation.dart' show kIsWeb;

class ApiService {
  // IMPORTANT: Automatically selects correct URL based on platform
  // - Web (Chrome): uses localhost:5000
  // - Android Emulator: use 'http://10.0.2.2:5000/api'
  // - Physical Device: use your computer's IP address (check with ipconfig)
  static String get baseUrl {
    if (kIsWeb) {
      // Running in Chrome/Web - use localhost
      return 'http://localhost:5000/api';
    } else {
      // Running on mobile device - use network IP
      return 'http://192.168.239.154:5000/api';
    }
  }

  static String get complaintBaseUrl {
    if (kIsWeb) {
      // Running in Chrome/Web - use localhost
      return 'http://localhost:5004/api';
    } else {
      // Running on mobile device - use network IP
      return 'http://192.168.239.154:5004/api';
    }
  }
  
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();
  
  String? _token;
  
  Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('auth_token');
  }
  
  Future<void> _saveToken(String token) async {
    _token = token;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('auth_token', token);
  }
  
  Map<String, String> _getHeaders({bool includeAuth = true}) {
    final headers = {'Content-Type': 'application/json'};
    if (includeAuth && _token != null) {
      headers['Authorization'] = 'Bearer $_token';
    }
    return headers;
  }
  
  // ===== AUTH =====
  
  Future<Map<String, dynamic>> register({
    required String username,
    required String email,
    required String password,
    String? mobile,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/register'),
      headers: _getHeaders(includeAuth: false),
      body: jsonEncode({
        'username': username,
        'email': email,
        'password': password,
        'mobile': mobile ?? '',
      }),
    );
    
    final data = jsonDecode(response.body);
    if (response.statusCode == 200 && data['success']) {
      await _saveToken(data['data']['token']);
      return data;
    }
    throw Exception(data['error'] ?? 'Registration failed');
  }
  
  Future<Map<String, dynamic>> completeSignup({
    required String phone,
    required String name,
    required String email,
    String? position,
    String? province,
    String? district,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/complete-signup'),
      headers: _getHeaders(includeAuth: false),
      body: jsonEncode({
        'phone': phone,
        'name': name,
        'email': email,
        'position': position ?? '',
        'province': province,
        'district': district,
      }),
    );
    
    final data = jsonDecode(response.body);
    if (response.statusCode == 200 && data['success']) {
      await _saveToken(data['data']['token']);
      return data;
    }
    throw Exception(data['error'] ?? 'Signup completion failed');
  }
  
  Future<Map<String, dynamic>> login({
    required String email,
    required String password,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: _getHeaders(includeAuth: false),
      body: jsonEncode({'email': email, 'password': password}),
    );
    
    final data = jsonDecode(response.body);
    if (response.statusCode == 200 && data['success']) {
      await _saveToken(data['data']['token']);
      return data;
    }
    throw Exception(data['error'] ?? 'Login failed');
  }
  
  // Save anonymous profile (display name and avatar)
  Future<Map<String, dynamic>> saveAnonymousProfile({
    required int userId,
    required String displayName,
    required String avatarType,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/anonymous-profile'),
      headers: _getHeaders(includeAuth: false),
      body: jsonEncode({
        'user_id': userId,
        'display_name': displayName,
        'avatar_type': avatarType,
      }),
    );
    
    final data = jsonDecode(response.body);
    if (response.statusCode == 200 && data['success']) {
      // Save to SharedPreferences
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('display_name', displayName);
      await prefs.setString('avatar_type', avatarType);
      return data;
    }
    throw Exception(data['error'] ?? 'Failed to save anonymous profile');
  }
  
  // ===== POSTS =====
  
  /// Validate post content before submission
  /// Returns validation result with flutter_response format
  Future<Map<String, dynamic>> validatePost({
    required String description,
    required String issueType,
    String? imageBase64,
    int? userId,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/posts/validate'),
      headers: _getHeaders(),
      body: jsonEncode({
        'description': description,
        'issue_type': issueType,
        'image': imageBase64 ?? '',
        'user_id': userId,
      }),
    );
    
    final data = jsonDecode(response.body);
    print('🔍 Validation response keys: ${data.keys.toList()}');
    print('🔍 Has flutter_response: ${data.containsKey("flutter_response")}');
    if (data.containsKey('flutter_response')) {
      print('🔍 flutter_response can_proceed: ${data["flutter_response"]["can_proceed"]}');
    }
    // Return the full validation response (includes flutter_response)
    return data;
  }
  
  /// Classify garbage type immediately when user selects image
  /// Used for auto-filling garbage type field
  Future<Map<String, dynamic>> classifyGarbage(String imageBase64) async {
    final response = await http.post(
      Uri.parse('$baseUrl/posts/classify-garbage'),
      headers: _getHeaders(),
      body: jsonEncode({'image': imageBase64}),
    );
    
    final data = jsonDecode(response.body);
    if (response.statusCode == 200 && data['success']) {
      return data;
    }
    throw Exception(data['error'] ?? 'Garbage classification failed');
  }
  
  Future<Map<String, dynamic>> getAllPosts({int page = 1}) async {
    final response = await http.get(
      Uri.parse('$baseUrl/posts?page=$page&per_page=20'),
      headers: _getHeaders(includeAuth: false),
    );
    
    final data = jsonDecode(response.body);
    if (response.statusCode == 200 && data['success']) {
      return data;
    }
    throw Exception(data['error'] ?? 'Failed to get posts');
  }
  
  Future<Map<String, dynamic>> submitPost({
    required String title,
    required String description,
    required String location,
    required String issueType,
    required List<String> images,
    double? latitude,
    double? longitude,
    String? province,
    String? district,
    String? priority,
    String? roadType,
  }) async {
    // STEP 1: Get user_id first
    final prefs = await SharedPreferences.getInstance();
    final userIdStr = prefs.getString('userId');
    final userId = userIdStr != null ? int.tryParse(userIdStr) : null;
    
    // STEP 2: Validate content first
    print('🔍 Validating post content before submission...');
    final validationResult = await validatePost(
      description: description,
      issueType: issueType,
      imageBase64: images.isNotEmpty ? images.first : null,
      userId: userId,
    );
    
    // Check if validation passed
    final flutterResponse = validationResult['flutter_response'];
    if (flutterResponse != null && flutterResponse['can_proceed'] == false) {
      // Validation failed - return the validation result so UI can show popup
      print('❌ Validation failed: ${flutterResponse['title']}');
      return {
        'success': false,
        'validation_failed': true,
        'flutter_response': flutterResponse,
        'final_decision': validationResult['final_decision'],
        'simple_notification': validationResult['simple_notification'],
        'strike_warning': validationResult['strike_warning'],  // Pass strike warning
        'strike_notification': validationResult['strike_notification'],  // Pass strike notification
      };
    }
    
    print('✅ Validation passed, submitting post...');
    
    // STEP 3: Submit the post (only if validation passed)
    final response = await http.post(
      Uri.parse('$baseUrl/posts/submit'),
      headers: _getHeaders(),
      body: jsonEncode({
        'user_id': userId,
        'title': title,
        'description': description,
        'location': location,
        'latitude': latitude,
        'longitude': longitude,
        'province': province,
        'district': district,
        'issue_type': issueType,
        'road_type': roadType,
        'priority': priority ?? 'medium',
        'images': images,
        'validation_passed': true,  // Flag to indicate validation was done
      }),
    );
    
    final data = jsonDecode(response.body);
    if (response.statusCode == 200) {
      return data;
    }
    throw Exception(data['error'] ?? 'Failed to submit post');
  }
  
  // ===== NOTIFICATIONS =====
  
  Future<Map<String, dynamic>> getNotifications(int userId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/notifications/$userId'),
      headers: _getHeaders(),
    );
    
    final data = jsonDecode(response.body);
    if (response.statusCode == 200 && data['success']) {
      return data;
    }
    throw Exception(data['error'] ?? 'Failed to get notifications');
  }
  
  Future<Map<String, dynamic>> markNotificationAsRead(int notificationId) async {
    final response = await http.put(
      Uri.parse('$baseUrl/notifications/$notificationId/read'),
      headers: _getHeaders(),
    );
    
    final data = jsonDecode(response.body);
    if (response.statusCode == 200 && data['success']) {
      return data;
    }
    throw Exception(data['error'] ?? 'Failed to mark notification as read');
  }
  
  Future<Map<String, dynamic>> verifyCompletion(int postId, int userId, bool verified) async {
    final response = await http.post(
      Uri.parse('$baseUrl/notifications/verify-completion/$postId'),
      headers: _getHeaders(),
      body: jsonEncode({
        'verified': verified,
        'user_id': userId,
      }),
    );
    
    final data = jsonDecode(response.body);
    if (response.statusCode == 200 && data['success']) {
      return data;
    }
    throw Exception(data['error'] ?? 'Failed to verify completion');
  }
  
  // ===== INTERACTIONS =====
  
  Future<Map<String, dynamic>> toggleLike(int postId) async {
    final prefs = await SharedPreferences.getInstance();
    final userId = prefs.getString('userId');
    
    final response = await http.post(
      Uri.parse('$baseUrl/interactions/like/$postId'),
      headers: _getHeaders(includeAuth: false),
      body: jsonEncode({'user_id': userId}),
    );
    
    final data = jsonDecode(response.body);
    if (response.statusCode == 200 && data['success']) {
      return data;
    }
    throw Exception(data['error'] ?? 'Failed to toggle like');
  }
  
  Future<Map<String, dynamic>> checkLike(int postId) async {
    final prefs = await SharedPreferences.getInstance();
    final userId = prefs.getString('userId');
    
    final response = await http.post(
      Uri.parse('$baseUrl/interactions/check-like/$postId'),
      headers: _getHeaders(includeAuth: false),
      body: jsonEncode({'user_id': userId}),
    );
    
    final data = jsonDecode(response.body);
    if (response.statusCode == 200 && data['success']) {
      return data;
    }
    throw Exception(data['error'] ?? 'Failed to check like status');
  }
  
  Future<Map<String, dynamic>> addComment(int postId, String text, {String? image}) async {
    final prefs = await SharedPreferences.getInstance();
    final userId = prefs.getString('userId');
    
    final response = await http.post(
      Uri.parse('$baseUrl/interactions/comment/$postId'),
      headers: _getHeaders(includeAuth: false),
      body: jsonEncode({
        'user_id': userId,
        'text': text,
        'image': image,  // Include image if provided
      }),
    );
    
    final data = jsonDecode(response.body);
    if (response.statusCode == 200 && data['success']) {
      return data;
    }
    throw Exception(data['error'] ?? 'Failed to add comment');
  }
  
  Future<Map<String, dynamic>> getComments(int postId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/interactions/comments/$postId'),
      headers: _getHeaders(includeAuth: false),
    );
    
    final data = jsonDecode(response.body);
    if (response.statusCode == 200 && data['success']) {
      return data;
    }
    throw Exception(data['error'] ?? 'Failed to get comments');
  }
  
  Future<Map<String, dynamic>> sharePost(int postId) async {
    final prefs = await SharedPreferences.getInstance();
    final userId = prefs.getString('userId');
    
    final response = await http.post(
      Uri.parse('$baseUrl/interactions/share/$postId'),
      headers: _getHeaders(includeAuth: false),
      body: jsonEncode({'user_id': userId}),
    );
    
    final data = jsonDecode(response.body);
    if (response.statusCode == 200 && data['success']) {
      return data;
    }
    throw Exception(data['error'] ?? 'Failed to share post');
  }
  
  // ===== USER POSTS =====
  
  Future<Map<String, dynamic>> getUserPosts(int userId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/posts/user/$userId'),
      headers: _getHeaders(includeAuth: false),
    );
    
    final data = jsonDecode(response.body);
    if (response.statusCode == 200 && data['success']) {
      return data;
    }
    throw Exception(data['error'] ?? 'Failed to get user posts');
  }
  
  Future<Map<String, dynamic>> getPostDetail(int postId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/posts/$postId'),
      headers: _getHeaders(includeAuth: false),
    );
    
    final data = jsonDecode(response.body);
    if (response.statusCode == 200 && data['success']) {
      return data;
    }
    throw Exception(data['error'] ?? 'Failed to get post detail');
  }
  
  // ===== OTP AUTHENTICATION =====
  
  // Helper to format phone number to E.164 format (+94...)
  String _formatPhoneNumber(String phone) {
    String formatted = phone.trim();
    if (formatted.startsWith('0')) {
      formatted = '+94' + formatted.substring(1);
    } else if (!formatted.startsWith('+')) {
      formatted = '+94' + formatted;
    }
    return formatted;
  }

  Future<Map<String, dynamic>> sendOtp({
    required String phone,
    String? name,
    String? email,
    String? password,
    String? province,
    String? district,
  }) async {
    try {
      final formattedPhone = _formatPhoneNumber(phone);
      
      print('🔄 Sending OTP request to: $baseUrl/auth/send-otp');
      print('📱 Phone: $formattedPhone');
      
      final response = await http.post(
        Uri.parse('$baseUrl/auth/send-otp'),
        headers: _getHeaders(includeAuth: false),
        body: jsonEncode({
          'phone': formattedPhone,
          'name': name,
          'email': email,
          'password': password,
          'province': province,
          'district': district,
        }),
      ).timeout(
        const Duration(seconds: 10),
        onTimeout: () {
          throw Exception('Connection timeout - please check your internet connection');
        },
      );
      
      print('📥 Response status: ${response.statusCode}');
      print('📥 Response body: ${response.body}');
      
      final data = jsonDecode(response.body);
      if (response.statusCode == 200 && data['success']) {
        print('✅ OTP sent successfully');
        return data;
      }
      throw Exception(data['error'] ?? 'Failed to send OTP');
    } catch (e) {
      print('❌ Error in sendOtp: $e');
      if (e.toString().contains('SocketException') || e.toString().contains('Failed host lookup')) {
        throw Exception('Cannot connect to server - please check your internet connection');
      }
      rethrow;
    }
  }
  
  Future<Map<String, dynamic>> verifyOtp({
    required String phone,
    required String otp,
  }) async {
    final formattedPhone = _formatPhoneNumber(phone);
    
    final response = await http.post(
      Uri.parse('$baseUrl/auth/verify-otp'),
      headers: _getHeaders(includeAuth: false),
      body: jsonEncode({
        'phone': formattedPhone,
        'otp': otp,
      }),
    );
    
    final data = jsonDecode(response.body);
    if (response.statusCode == 200 && data['success']) {
      return data;
    }
    throw Exception(data['error'] ?? 'OTP verification failed');
  }
  
  bool isLoggedIn() => _token != null;
  
  Future<void> logout() async {
    _token = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('auth_token');
  }

  // ============ FASTAPI ENGINE EXPANSION ============
    Future<Map<String, dynamic>> submitComplaintPost({
    required String text, // Final-ah select aana text (Raw or AI)
    required bool isExpanded, // Checkbox state
    required String location,
    required String category,
    double? latitude,
    double? longitude,
  }) async {
    try {
      final response = await http.post(
        Uri.parse("$complaintBaseUrl/complaints/submit"),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "category": category,
          "text": text, // UI-la irundhu vara final text
          "expand_text": isExpanded, // User expand panna ninaikiraaraa nu
          "location_link": location,
          "latitude": latitude,
          "longitude": longitude,
        }),
      );
      
      // Postman-la neenga paartha 200 OK success response inge return aagum
      return jsonDecode(response.body);
    } catch (e) {
      return {"status": "error", "message": e.toString()};
    }
  }

  // 2. NEW FUNCTION: AI expansion-kaka mattum separate-ah oru call
  Future<Map<String, dynamic>> expandText(String originalText) async {
    final response = await http.post(
      Uri.parse("$complaintBaseUrl/complaints/expand"), // FastAPI engine expansion endpoint
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"text": originalText}),
    );
    return jsonDecode(response.body);
  }

}
