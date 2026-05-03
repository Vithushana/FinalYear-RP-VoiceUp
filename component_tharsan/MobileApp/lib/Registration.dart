import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'main.dart'; // Import the LoginPage

class AddUserPage extends StatefulWidget {
  @override
  _AddUserPageState createState() => _AddUserPageState();
}

class _AddUserPageState extends State<AddUserPage> {
  TextEditingController _nameController = TextEditingController();
  TextEditingController _contactNumberController = TextEditingController();
  TextEditingController _usernameController = TextEditingController();
  TextEditingController _passwordController = TextEditingController();
  String? _selectedGender;
  String _errorText = "";

  // Lavender color theme (matching login page)
  final Color lavenderPrimary = Color(0xFF9B6B9E); // Lavender purple
  final Color lavenderLight = Color(0xFFE6C8E8); // Light lavender
  final Color lavenderDark = Color(0xFF7B4B7E); // Dark lavender
  final Color lavenderAccent = Color(0xFFD6B0D8); // Soft lavender
  final Color lavenderMist = Color(0xFFF3E5F5); // Very light lavender

  void _showSnackbar(String message, {bool isError = false}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            Icon(
              isError ? Icons.error_outline : Icons.check_circle_outline,
              color: Colors.white,
            ),
            SizedBox(width: 8),
            Expanded(child: Text(message)),
          ],
        ),
        backgroundColor: isError ? Colors.red.shade400 : lavenderPrimary,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        duration: Duration(seconds: 2),
      ),
    );
  }

  Future<void> _addUser() async {
    // Validate inputs
    if (_nameController.text.isEmpty) {
      setState(() {
        _errorText = 'Name is required';
      });
      _showSnackbar('Name is required', isError: true);
      return;
    }

    if (_contactNumberController.text.isEmpty) {
      setState(() {
        _errorText = 'Contact number is required';
      });
      _showSnackbar('Contact number is required', isError: true);
      return;
    }

    if (_usernameController.text.isEmpty) {
      setState(() {
        _errorText = 'Email is required';
      });
      _showSnackbar('Email is required', isError: true);
      return;
    }

    if (!_usernameController.text.contains('@')) {
      setState(() {
        _errorText = 'Enter a valid email address';
      });
      _showSnackbar('Enter a valid email address', isError: true);
      return;
    }

    if (_passwordController.text.isEmpty) {
      setState(() {
        _errorText = 'Password is required';
      });
      _showSnackbar('Password is required', isError: true);
      return;
    }

    if (_passwordController.text.length < 6) {
      setState(() {
        _errorText = 'Password must be at least 6 characters';
      });
      _showSnackbar('Password must be at least 6 characters', isError: true);
      return;
    }

    if (_selectedGender == null) {
      setState(() {
        _errorText = 'Please select gender';
      });
      _showSnackbar('Please select gender', isError: true);
      return;
    }

    try {
      setState(() {
        _errorText = "";
      });

      // Check if the Username (Email) is already taken
      QuerySnapshot usernameExists = await FirebaseFirestore.instance
          .collection('users')
          .where('username', isEqualTo: _usernameController.text)
          .get();

      if (usernameExists.docs.isNotEmpty) {
        setState(() {
          _errorText = 'Email is already registered. Please use another email.';
        });
        _showSnackbar('Email is already registered', isError: true);
        return;
      }

      // Show loading indicator
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (BuildContext context) {
          return Dialog(
            backgroundColor: Colors.transparent,
            child: Container(
              padding: EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(20),
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  CircularProgressIndicator(color: lavenderPrimary),
                  SizedBox(height: 20),
                  Text('Creating account...', style: TextStyle(color: lavenderDark)),
                ],
              ),
            ),
          );
        },
      );

      // Create a user in Firebase Authentication
      UserCredential authUser = await FirebaseAuth.instance.createUserWithEmailAndPassword(
        email: _usernameController.text.trim(),
        password: _passwordController.text,
      );

      // User data for Firestore
      Map<String, dynamic> userData = {
        'name': _nameController.text.trim(),
        'contact_number': _contactNumberController.text.trim(),
        'username': _usernameController.text.trim(),
        'gender': _selectedGender,
        'role': 'user',
        'created_at': FieldValue.serverTimestamp(),
      };

      // Create Firestore document with UID
      await FirebaseFirestore.instance.collection('users').doc(authUser.user!.uid).set(userData);

      // Close loading dialog
      Navigator.pop(context);

      // Show success message
      _showSnackbar('Registration successful! Please login.', isError: false);

      // Navigate to login page after successful registration
      Future.delayed(Duration(seconds: 1), () {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (context) => LoginPage()),
        );
      });

    } on FirebaseAuthException catch (e) {
      // Close loading dialog if open
      Navigator.pop(context);

      String errorMessage = 'Registration failed';
      if (e.code == 'email-already-in-use') {
        errorMessage = 'This email is already registered';
      } else if (e.code == 'weak-password') {
        errorMessage = 'Password is too weak';
      } else if (e.code == 'invalid-email') {
        errorMessage = 'Invalid email address';
      }

      setState(() {
        _errorText = errorMessage;
      });
      _showSnackbar(errorMessage, isError: true);

    } catch (e) {
      // Close loading dialog if open
      Navigator.pop(context);

      setState(() {
        _errorText = 'Unexpected error occurred';
      });
      _showSnackbar('Registration failed. Please try again.', isError: true);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              lavenderMist,
              Colors.white,
              lavenderLight.withOpacity(0.3),
            ],
          ),
        ),
        child: SafeArea(
          child: Center(
            child: SingleChildScrollView(
              child: Container(
                constraints: BoxConstraints(maxWidth: 400),
                padding: EdgeInsets.all(20),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: <Widget>[
                    // Lavender Icon
                    Container(
                      width: 100,
                      height: 100,
                      decoration: BoxDecoration(
                        gradient: RadialGradient(
                          colors: [
                            lavenderLight,
                            lavenderPrimary.withOpacity(0.7),
                          ],
                        ),
                        shape: BoxShape.circle,
                        boxShadow: [
                          BoxShadow(
                            color: lavenderPrimary.withOpacity(0.3),
                            blurRadius: 15,
                            spreadRadius: 3,
                          ),
                        ],
                      ),
                      child: Icon(
                        Icons.person_add,
                        size: 50,
                        color: Colors.white,
                      ),
                    ),

                    SizedBox(height: 20),

                    // Lavender Heading
                    Column(
                      children: [
                        Text(
                          'CREATE ACCOUNT',
                          style: TextStyle(
                            color: lavenderDark,
                            fontSize: 28,
                            fontWeight: FontWeight.bold,
                            letterSpacing: 2,
                          ),
                        ),
                        SizedBox(height: 8),
                        Container(
                          width: 60,
                          height: 3,
                          decoration: BoxDecoration(
                            gradient: LinearGradient(
                              colors: [lavenderLight, lavenderPrimary, lavenderDark],
                            ),
                            borderRadius: BorderRadius.circular(10),
                          ),
                        ),
                      ],
                    ),

                    SizedBox(height: 10),

                    Text(
                      'Join Lavender Disease Diagnosis',
                      style: TextStyle(
                        color: Colors.grey.shade600,
                        fontSize: 14,
                      ),
                    ),

                    SizedBox(height: 25),

                    // Name Field
                    _buildTextField(
                      controller: _nameController,
                      label: 'Full Name',
                      icon: Icons.person_outline,
                    ),

                    SizedBox(height: 15),

                    // Contact Number Field
                    _buildTextField(
                      controller: _contactNumberController,
                      label: 'Contact Number',
                      icon: Icons.phone_outlined,
                      keyboardType: TextInputType.phone,
                    ),

                    SizedBox(height: 15),

                    // Email Field
                    _buildTextField(
                      controller: _usernameController,
                      label: 'Email Address',
                      icon: Icons.email_outlined,
                      keyboardType: TextInputType.emailAddress,
                    ),

                    SizedBox(height: 15),

                    // Password Field
                    _buildTextField(
                      controller: _passwordController,
                      label: 'Password',
                      icon: Icons.lock_outline,
                      isPassword: true,
                    ),

                    SizedBox(height: 15),

                    // Gender Selection
                    Container(
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(15),
                        boxShadow: [
                          BoxShadow(
                            color: lavenderPrimary.withOpacity(0.1),
                            blurRadius: 10,
                            offset: Offset(0, 5),
                          ),
                        ],
                      ),
                      child: Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 15, vertical: 5),
                        child: Row(
                          children: <Widget>[
                            Icon(Icons.person_outline, color: lavenderPrimary, size: 24),
                            SizedBox(width: 10),
                            Text(
                              'Gender:',
                              style: TextStyle(
                                color: lavenderDark,
                                fontSize: 16,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                            SizedBox(width: 20),
                            Row(
                              children: <Widget>[
                                _buildGenderOption('Male'),
                                SizedBox(width: 15),
                                _buildGenderOption('Female'),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),

                    SizedBox(height: 10),

                    // Error message if any
                    if (_errorText.isNotEmpty)
                      Container(
                        margin: EdgeInsets.symmetric(vertical: 10),
                        padding: EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: Colors.red.shade50,
                          borderRadius: BorderRadius.circular(10),
                          border: Border.all(color: Colors.red.shade200),
                        ),
                        child: Row(
                          children: [
                            Icon(Icons.error_outline, color: Colors.red.shade400, size: 20),
                            SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                _errorText,
                                style: TextStyle(color: Colors.red.shade700),
                              ),
                            ),
                          ],
                        ),
                      ),

                    SizedBox(height: 20),

                    // Register Button
                    Container(
                      width: double.infinity,
                      height: 55,
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: [lavenderPrimary, lavenderDark],
                        ),
                        borderRadius: BorderRadius.circular(15),
                        boxShadow: [
                          BoxShadow(
                            color: lavenderDark.withOpacity(0.3),
                            blurRadius: 10,
                            offset: Offset(0, 5),
                          ),
                        ],
                      ),
                      child: ElevatedButton(
                        onPressed: _addUser,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.transparent,
                          shadowColor: Colors.transparent,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(15),
                          ),
                        ),
                        child: Text(
                          'Register Me',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.w600,
                            color: Colors.white,
                          ),
                        ),
                      ),
                    ),

                    SizedBox(height: 15),

                    // Login Link
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          'Already have an account?',
                          style: TextStyle(color: Colors.grey.shade600),
                        ),
                        TextButton(
                          onPressed: () {
                            Navigator.pushReplacement(
                              context,
                              MaterialPageRoute(builder: (context) => LoginPage()),
                            );
                          },
                          child: Text(
                            'Sign In',
                            style: TextStyle(
                              color: lavenderPrimary,
                              fontWeight: FontWeight.bold,
                              fontSize: 16,
                            ),
                          ),
                        ),
                      ],
                    ),

                    SizedBox(height: 20),

                    // Footer text
                    Text(
                      '© 2024 Lavender Disease Diagnosis',
                      style: TextStyle(
                        color: Colors.grey.shade500,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildTextField({
    required TextEditingController controller,
    required String label,
    required IconData icon,
    bool isPassword = false,
    TextInputType? keyboardType,
  }) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(15),
        boxShadow: [
          BoxShadow(
            color: lavenderPrimary.withOpacity(0.1),
            blurRadius: 10,
            offset: Offset(0, 5),
          ),
        ],
      ),
      child: TextFormField(
        controller: controller,
        obscureText: isPassword,
        keyboardType: keyboardType,
        decoration: InputDecoration(
          labelText: label,
          labelStyle: TextStyle(color: lavenderPrimary),
          prefixIcon: Icon(icon, color: lavenderPrimary),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(15),
            borderSide: BorderSide.none,
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(15),
            borderSide: BorderSide.none,
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(15),
            borderSide: BorderSide(color: lavenderPrimary, width: 2),
          ),
          filled: true,
          fillColor: Colors.white,
        ),
      ),
    );
  }

  Widget _buildGenderOption(String gender) {
    bool isSelected = _selectedGender == gender;
    return GestureDetector(
      onTap: () {
        setState(() {
          _selectedGender = gender;
        });
      },
      child: Container(
        padding: EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: isSelected ? lavenderLight : Colors.transparent,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isSelected ? lavenderPrimary : lavenderLight,
            width: 1,
          ),
        ),
        child: Text(
          gender,
          style: TextStyle(
            color: isSelected ? lavenderDark : Colors.grey.shade700,
            fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
          ),
        ),
      ),
    );
  }
}