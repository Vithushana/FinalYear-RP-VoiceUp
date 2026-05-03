import 'package:flutter/material.dart';
import '../screens/complaint_making_screen.dart';

class ComplaintPostToggleScreen extends StatefulWidget {
  const ComplaintPostToggleScreen({super.key});

  @override
  State<ComplaintPostToggleScreen> createState() =>
      _ComplaintPostToggleScreenState();
}

class _ComplaintPostToggleScreenState extends State<ComplaintPostToggleScreen> {
  bool isComplaintSelected = true;

  static const Color darkBlue = Color(0xFF004C89);
  static const Color yellow = Color(0xFFFFD600);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[200],
      body: SafeArea(
        child: SingleChildScrollView(
          child: Column(
            children: [
              const SizedBox(height: 40),

              // ================= POST / COMPLAINT TOGGLE =================
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 18),
                child: Container(
                  padding: const EdgeInsets.all(4),
                  decoration: BoxDecoration(
                    color: Colors.grey[300],
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Row(
                    children: [
                      // POST
                      Expanded(
                        child: GestureDetector(
                          onTap: () {
                            // Go back to POST screen (ExploreScreen in BottomNavScaffold)
                            Navigator.pop(context);
                          },
                          child: Container(
                            padding: const EdgeInsets.symmetric(vertical: 10),
                            decoration: BoxDecoration(
                              color: !isComplaintSelected
                                  ? darkBlue
                                  : Colors.transparent,
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Center(
                              child: Text(
                                "POST",
                                style: TextStyle(
                                  fontWeight: FontWeight.w700,
                                  color: !isComplaintSelected
                                      ? Colors.white
                                      : Colors.grey[600],
                                ),
                              ),
                            ),
                          ),
                        ),
                      ),

                      // COMPLAINT
                      Expanded(
                        child: GestureDetector(
                          onTap: () {
                            setState(() => isComplaintSelected = true);
                          },
                          child: Container(
                            padding: const EdgeInsets.symmetric(vertical: 10),
                            decoration: BoxDecoration(
                              color: isComplaintSelected
                                  ? darkBlue
                                  : Colors.transparent,
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Center(
                              child: Text(
                                "COMPLAINT",
                                style: TextStyle(
                                  fontWeight: FontWeight.w700,
                                  color: isComplaintSelected
                                      ? Colors.white
                                      : Colors.grey[600],
                                ),
                              ),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 80),

              // ================= MAIN CARD =================
              Center(
                child: Container(
                  width: 320,
                  padding: const EdgeInsets.fromLTRB(20, 24, 20, 16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(18),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.12),
                        blurRadius: 12,
                        offset: const Offset(0, 6),
                      ),
                    ],
                  ),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.report_problem, size: 36, color: darkBlue),
                      const SizedBox(height: 12),

                      const Text(
                        'Report a Complaint',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.w700,
                          color: darkBlue,
                        ),
                        textAlign: TextAlign.center,
                      ),

                      const SizedBox(height: 8),

                      const Text(
                        'Report issues that need\nofficial attention.',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.black54,
                          height: 1.3,
                        ),
                        textAlign: TextAlign.center,
                      ),

                      const SizedBox(height: 40),

                      // ================= MAKE COMPLAINT BUTTON =================
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton.icon(
                          onPressed: () {
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (_) => const ComplaintMakingScreen(),
                              ),
                            );
                          },
                          style: ElevatedButton.styleFrom(
                            backgroundColor: yellow,
                            foregroundColor: Colors.black,
                            padding: const EdgeInsets.symmetric(vertical: 12),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(10),
                            ),
                          ),
                          icon: const Icon(Icons.edit),
                          label: const Text(
                            'Make Complaint',
                            style: TextStyle(
                              fontWeight: FontWeight.w600,
                              fontSize: 16,
                            ),
                          ),
                        ),
                      ),

                      const SizedBox(height: 14),

                      // ================= BACK BUTTON =================
                      GestureDetector(
                        onTap: () {
                          // Go back to previous screen (BottomNavScaffold)
                          Navigator.pop(context);
                        },
                        child: Container(
                          width: double.infinity,
                          padding: const EdgeInsets.symmetric(vertical: 12),
                          decoration: BoxDecoration(
                            color: Colors.grey[300],
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: const Center(
                            child: Text(
                              'Back',
                              style: TextStyle(
                                color: Colors.black54,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 40),
            ],
          ),
        ),
      ),
    );
  }
}
