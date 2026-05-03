import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:cloud_firestore/cloud_firestore.dart';

class CurrentUser extends StatefulWidget {
  const CurrentUser({Key? key}) : super(key: key);

  @override
  State<CurrentUser> createState() => _CurrentUserState();
}

class _CurrentUserState extends State<CurrentUser> {
  Map<String, dynamic> currentUserData = {};

  @override
  void initState() {
    super.initState();
    fetchUserData();
  }

  Future<void> fetchUserData() async {
    try {
      // Get the current user ID
      String? userId = FirebaseAuth.instance.currentUser?.uid;

      if (userId != null) {
        // Retrieve the document for the current user from Firestore
        DocumentSnapshot<Map<String, dynamic>> snapshot =
        await FirebaseFirestore.instance.collection('users').doc(userId).get();

        if (snapshot.exists) {
          // If the document exists, save the data to currentUserData variable
          setState(() {
            currentUserData = snapshot.data()!;
          });
        }
      }
    } catch (e) {
      // Handle any errors
      print("Error fetching user data: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Current User Data'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Text('Email: ${currentUserData['email']}'),
            Text('Name: ${currentUserData['name']}'),
            Text('User ID: ${currentUserData['userId']}'),
          ],
        ),
      ),
    );
  }
}
