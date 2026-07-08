import 'package:flutter/material.dart';
import 'dashboard_screen.dart';
import 'transactions_screen.dart' as tx_screen;
import 'voice_screen.dart';
import 'customer_screen.dart';
import 'assistant_screen.dart';
import 'profile_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _selectedIndex = 0;

  static const _teal      = Color(0xFF2DC98E);
  static const _hintGreen = Color(0xFF7A9E8A);

  late final List<Widget> _screens = [
    const DashboardScreen(),
    const tx_screen.TransactionsScreen(),
    const VoiceScreen(),
    const CustomerScreen(),
    const AssistantScreen(),
    const ProfileScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF0FAF4),
      body: IndexedStack(
        index: _selectedIndex,
        children: _screens,
      ),
      bottomNavigationBar: Container(
        decoration: const BoxDecoration(
          color: Colors.white,
          border: Border(top: BorderSide(color: Color(0xFFDDF0E8), width: 1)),
        ),
        child: SafeArea(
          child: SizedBox(
            height: 64,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _navItem(0, Icons.dashboard_outlined,       Icons.dashboard_rounded,    'Home'),
                _navItem(1, Icons.list_alt_outlined,        Icons.list_alt_rounded,     'Ledger'),
                _voiceFab(),
                _navItem(3, Icons.person_outline_rounded,   Icons.person_rounded,       'Customer'),
                _navItem(4, Icons.chat_bubble_outline_rounded, Icons.chat_bubble_rounded, 'Chat'),
                _navItem(5, Icons.account_circle_outlined,  Icons.account_circle_rounded, 'Profile'),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _navItem(int index, IconData out, IconData filled, String label) {
    final sel = _selectedIndex == index;
    return GestureDetector(
      onTap: () => setState(() => _selectedIndex = index),
      behavior: HitTestBehavior.opaque,
      child: SizedBox(
        width: 56,
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(sel ? filled : out,
                color: sel ? _teal : _hintGreen, size: 21),
            const SizedBox(height: 4),
            Text(label,
                style: TextStyle(
                    fontSize: 9.5,
                    fontWeight: sel ? FontWeight.w600 : FontWeight.w400,
                    color: sel ? _teal : _hintGreen)),
          ],
        ),
      ),
    );
  }

  Widget _voiceFab() {
    final sel = _selectedIndex == 2;
    return GestureDetector(
      onTap: () => setState(() => _selectedIndex = 2),
      child: Container(
        width: 52,
        height: 52,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          color: sel ? _teal : const Color(0xFF1BB87A),
          boxShadow: [
            BoxShadow(
              color: _teal.withOpacity(0.35),
              blurRadius: 12,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: const Icon(Icons.mic_rounded, color: Colors.white, size: 24),
      ),
    );
  }
}