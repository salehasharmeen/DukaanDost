import 'package:flutter/material.dart';
import 'login_screen.dart';
import 'signup_screen.dart';

class WelcomeScreen extends StatelessWidget {
  const WelcomeScreen({super.key});

  static const _teal       = Color(0xFF2DC98E);
  static const _lightGreen = Color(0xFFF0FAF4);
  static const _hintGreen  = Color(0xFF7A9E8A);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _lightGreen,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 32.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              const Spacer(flex: 2),

              // ── Mascot ───────────────────────────────────────
              Stack(
                alignment: Alignment.center,
                children: [
                  Container(
                    width: 164,
                    height: 164,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      border: Border.all(color: _teal, width: 2.5),
                    ),
                  ),
                  ClipOval(
                    child: Container(
                      width: 144,
                      height: 144,
                      color: Colors.white,
                      child: Image.asset(
                        'assets/images/mascot.png',
                        fit: BoxFit.cover,
                        errorBuilder: (_, __, ___) => const Icon(
                          Icons.storefront_rounded,
                          size: 70,
                          color: _teal,
                        ),
                      ),
                    ),
                  ),
                  Positioned(
                    bottom: 10,
                    right: 10,
                    child: Container(
                      padding: const EdgeInsets.all(7),
                      decoration: const BoxDecoration(
                        color: _teal,
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(
                        Icons.shopping_bag_rounded,
                        color: Colors.white,
                        size: 18,
                      ),
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 28),

              // ── App name ─────────────────────────────────────
              const Text(
                'DUKAN DOST',
                style: TextStyle(
                  fontSize: 30,
                  fontWeight: FontWeight.w900,
                  color: _teal,
                  letterSpacing: 2.0,
                ),
              ),
              const SizedBox(height: 6),
              const Text(
                'Your Shop Companion',
                style: TextStyle(
                  fontSize: 14,
                  color: _hintGreen,
                  letterSpacing: 0.5,
                ),
              ),

              const Spacer(flex: 2),

              // ── Feature pills ─────────────────────────────────
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  _pill(Icons.mic_rounded, 'Voice'),
                  const SizedBox(width: 10),
                  _pill(Icons.auto_awesome_rounded, 'AI Ledger'),
                  const SizedBox(width: 10),
                  _pill(Icons.menu_book_rounded, 'Punjabi'),
                ],
              ),

              const SizedBox(height: 36),

              // ── Log In ────────────────────────────────────────
              SizedBox(
                width: double.infinity,
                height: 52,
                child: ElevatedButton(
                  onPressed: () => Navigator.of(context).push(
                    MaterialPageRoute(builder: (_) => const LoginScreen()),
                  ),
                  child: const Text('Log In'),
                ),
              ),

              const SizedBox(height: 14),

              // ── Sign Up ───────────────────────────────────────
              SizedBox(
                width: double.infinity,
                height: 52,
                child: OutlinedButton(
                  onPressed: () => Navigator.of(context).push(
                    MaterialPageRoute(builder: (_) => const SignupScreen()),
                  ),
                  child: const Text('Sign Up'),
                ),
              ),

              const SizedBox(height: 16),

              TextButton(
                onPressed: () {},
                child: const Text(
                  'Forgot Password?',
                  style: TextStyle(color: _hintGreen, fontSize: 13),
                ),
              ),

              const Spacer(flex: 1),

              const Text(
                'By continuing you agree to our Terms & Privacy Policy',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 11, color: Color(0xFFADD4C2)),
              ),
              const SizedBox(height: 16),
            ],
          ),
        ),
      ),
    );
  }

  static Widget _pill(IconData icon, String label) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: const Color(0xFFE0F7EE),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFB2DFD0), width: 1),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 13, color: _teal),
          const SizedBox(width: 5),
          Text(
            label,
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: Color(0xFF3A6B54),
            ),
          ),
        ],
      ),
    );
  }
}