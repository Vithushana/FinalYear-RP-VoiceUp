import 'package:flutter/material.dart';
import 'services/api_service.dart';
import 'app/app.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize API service
  await ApiService().init();
  
  runApp(MyApp());
}