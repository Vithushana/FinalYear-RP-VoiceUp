import 'package:flutter/material.dart';
import 'package:voice_up_ime/screens/home_screen.dart';
import 'package:voice_up_ime/screens/login_screen.dart';
import 'package:voice_up_ime/screens/signup_screen.dart';
import 'package:voice_up_ime/screens/otp_verification_screen.dart';
import 'package:voice_up_ime/screens/profile_confirmation_screen.dart';
import 'package:voice_up_ime/screens/explore_screen.dart';
import 'package:voice_up_ime/screens/complaint_post_toggle_screen.dart';
import 'package:voice_up_ime/screens/complaint_making_screen.dart';
import 'package:voice_up_ime/screens/post_detail_screen.dart';
import '../navigation/bottom_nav_scaffold.dart';

class AppRoutes {
  static const String root = '/';
  static const String login = '/login';
  static const String signup = '/signup';
  static const String otpVerification = '/otp-verification';
  static const String profileConfirmation = '/profile-confirmation';
  static const String explore = '/explore';
  static const String complaintToggle = '/complaint-toggle';
  static const String complaintMaking = '/complaint-making';
  static const String postDetail = '/post-detail';
}

final Map<String, WidgetBuilder> appRoutes = {
  AppRoutes.root: (context) => const BottomNavScaffold(),
  AppRoutes.login: (context) => const LoginScreen(),
  AppRoutes.signup: (context) => const SignupScreen(),
  AppRoutes.otpVerification: (context) {
    final args = ModalRoute.of(context)!.settings.arguments as Map<String, dynamic>;
    return OtpVerificationScreen(
      phoneNumber: args['phoneNumber'] as String,
      signupData: args['signupData'] as Map<String, String>,
    );
  },
  AppRoutes.profileConfirmation: (context) {
    final args = ModalRoute.of(context)!.settings.arguments as Map<String, dynamic>;
    return ProfileConfirmationScreen(
      phoneNumber: args['phoneNumber'] as String,
      signupData: args['signupData'] as Map<String, String>,
    );
  },
  AppRoutes.explore: (context) => const ExploreScreen(),
  AppRoutes.complaintToggle: (context) => const ComplaintPostToggleScreen(),
  AppRoutes.complaintMaking: (context) => const ComplaintMakingScreen(),
  AppRoutes.postDetail: (context) {
    final args = ModalRoute.of(context)!.settings.arguments as Map<String, dynamic>;
    return PostDetailScreen(postId: args['postId'] as int);
  },
};
