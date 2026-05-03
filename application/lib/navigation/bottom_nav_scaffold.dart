import 'package:flutter/material.dart';
import '../screens/home_screen.dart';
import '../screens/explore_screen.dart';
import '../screens/my_request_screen.dart';
import '../widgets/menu_bottom_sheet.dart';

class BottomNavScaffold extends StatefulWidget {
  final int? scrollToPostId;
  
  const BottomNavScaffold({super.key, this.scrollToPostId});

  @override
  State<BottomNavScaffold> createState() => _BottomNavScaffoldState();
}

class _BottomNavScaffoldState extends State<BottomNavScaffold> {
  int _currentIndex = 0;
  int? _scrollToPostId;

  @override
  void initState() {
    super.initState();
    // If scrollToPostId is provided, switch to My Requests tab
    if (widget.scrollToPostId != null) {
      _currentIndex = 2; // My Requests tab
      _scrollToPostId = widget.scrollToPostId;
    }
  }

  @override
  Widget build(BuildContext context) {
    const Color selectedColor = Color(0xFF004C89); // Friend's dark blue
    const Color unselectedColor = Colors.grey;

    // Build pages list - YOUR screens with backend integration
    final pages = [
      HomeScreen(), // Home
      ExploreScreen( // Request/Create Post - friend's UI
        onCancel: () {
          setState(() {
            _currentIndex = 0;
          });
        },
      ),
      MyRequestScreen(scrollToPostId: _scrollToPostId), // My Requests - YOUR screen
    ];

    // Safety check
    if (_currentIndex < 0 || _currentIndex >= pages.length) {
      _currentIndex = 0;
    }

    return Scaffold(
      body: pages[_currentIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        type: BottomNavigationBarType.fixed,
        selectedItemColor: selectedColor,
        unselectedItemColor: unselectedColor,
        onTap: (index) {
          if (index == 3) {
            // Menu button - show bottom sheet
            showModalBottomSheet(
              context: context,
              backgroundColor: Colors.transparent,
              builder: (context) => const MenuBottomSheet(),
            );
          } else if (index < 3) {
            setState(() {
              _currentIndex = index;
            });
          }
        },
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.home),
            label: 'Home',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.mic), // Friend's mic icon
            label: 'Request',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.list_alt),
            label: 'My Requests',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.menu),
            label: 'Menu',
          ),
        ],
      ),
    );
  }
}
