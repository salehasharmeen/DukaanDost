import 'package:flutter/material.dart';
import 'login_screen.dart';
import 'home_screen.dart';
import '../services/auth_service.dart';

class SignupScreen extends StatefulWidget {
  const SignupScreen({super.key});

  @override
  State<SignupScreen> createState() => _SignupScreenState();
}

class _SignupScreenState extends State<SignupScreen> {
  final _formKey           = GlobalKey<FormState>();
  final _nameController    = TextEditingController();
  final _shopController    = TextEditingController();
  final _emailController   = TextEditingController();
  final _passController    = TextEditingController();
  final _confirmController = TextEditingController();
  bool _obscurePass    = true;
  bool _obscureConfirm = true;
  bool _loading        = false;
  String? _error;

  static const _teal       = Color(0xFF2DC98E);
  static const _lightGreen = Color(0xFFF0FAF4);
  static const _hintGreen  = Color(0xFF7A9E8A);
  static const _darkGreen  = Color(0xFF1A3D2E);

  @override
  void dispose() {
    _nameController.dispose();
    _shopController.dispose();
    _emailController.dispose();
    _passController.dispose();
    _confirmController.dispose();
    super.dispose();
  }

  Future<void> _signup() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() { _loading = true; _error = null; });

    try {
      // REAL signup call — hits POST /signup on the backend,
      // saves the returned JWT token to local storage.
      await AuthService.signup(
        email: _emailController.text.trim(),
        password: _passController.text,
        shopName: _shopController.text.trim(),
      );

      if (!mounted) return;

      Navigator.of(context).pushAndRemoveUntil(
        MaterialPageRoute(builder: (_) => const HomeScreen()),
        (_) => false,
      );
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = 'Signup failed. This email may already be registered.\n($e)';
        _loading = false;
      });
      return;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _lightGreen,
      appBar: AppBar(
        backgroundColor: _lightGreen,
        elevation: 0,
        leading: const BackButton(color: _darkGreen),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 32),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: 8),
                const Text('Create Account',
                    style: TextStyle(
                        fontSize: 28,
                        fontWeight: FontWeight.w800,
                        color: _darkGreen)),
                const SizedBox(height: 6),
                const Text('Set up your Dukan Dost shop account',
                    style: TextStyle(fontSize: 14, color: _hintGreen)),
                const SizedBox(height: 32),

                _label('Your Name'),
                const SizedBox(height: 8),
                _field(
                  controller: _nameController,
                  hint: 'e.g. Tariq Hussain',
                  icon: Icons.person_outline_rounded,
                  validator: (v) =>
                      v == null || v.isEmpty ? 'Enter your name' : null,
                ),

                const SizedBox(height: 20),
                _label('Shop Name'),
                const SizedBox(height: 8),
                _field(
                  controller: _shopController,
                  hint: 'e.g. Hussain General Store',
                  icon: Icons.storefront_outlined,
                  validator: (v) =>
                      v == null || v.isEmpty ? 'Enter your shop name' : null,
                ),

                const SizedBox(height: 20),
                _label('Email'),
                const SizedBox(height: 8),
                _field(
                  controller: _emailController,
                  hint: 'you@example.com',
                  icon: Icons.alternate_email_rounded,
                  keyboardType: TextInputType.emailAddress,
                  validator: (v) =>
                      v == null || v.isEmpty ? 'Enter your email' : null,
                ),

                const SizedBox(height: 20),
                _label('Password'),
                const SizedBox(height: 8),
                _field(
                  controller: _passController,
                  hint: 'Min 6 characters',
                  icon: Icons.lock_outline_rounded,
                  obscure: _obscurePass,
                  suffix: _eyeIcon(
                    visible: _obscurePass,
                    onTap: () => setState(() => _obscurePass = !_obscurePass),
                  ),
                  validator: (v) =>
                      v == null || v.length < 6 ? 'Password too short' : null,
                ),

                const SizedBox(height: 20),
                _label('Confirm Password'),
                const SizedBox(height: 8),
                _field(
                  controller: _confirmController,
                  hint: 'Re-enter password',
                  icon: Icons.lock_outline_rounded,
                  obscure: _obscureConfirm,
                  suffix: _eyeIcon(
                    visible: _obscureConfirm,
                    onTap: () =>
                        setState(() => _obscureConfirm = !_obscureConfirm),
                  ),
                  validator: (v) => v != _passController.text
                      ? 'Passwords do not match'
                      : null,
                ),

                if (_error != null) ...[
                  const SizedBox(height: 16),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.redAccent.withOpacity(0.08),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(_error!,
                        style: const TextStyle(
                            color: Colors.redAccent, fontSize: 13)),
                  ),
                ],

                const SizedBox(height: 36),
                SizedBox(
                  width: double.infinity,
                  height: 52,
                  child: ElevatedButton(
                    onPressed: _loading ? null : _signup,
                    child: _loading
                        ? const SizedBox(
                            width: 22,
                            height: 22,
                            child: CircularProgressIndicator(
                                color: Colors.white, strokeWidth: 2.5),
                          )
                        : const Text('Create Account'),
                  ),
                ),

                const SizedBox(height: 24),
                Row(mainAxisAlignment: MainAxisAlignment.center, children: [
                  const Text('Already have an account? ',
                      style: TextStyle(color: _hintGreen, fontSize: 14)),
                  GestureDetector(
                    onTap: () => Navigator.of(context).pushReplacement(
                      MaterialPageRoute(builder: (_) => const LoginScreen()),
                    ),
                    child: const Text('Log In',
                        style: TextStyle(
                            color: _teal,
                            fontSize: 14,
                            fontWeight: FontWeight.w700)),
                  ),
                ]),
                const SizedBox(height: 32),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _label(String t) => Text(t,
      style: const TextStyle(
          fontSize: 13,
          fontWeight: FontWeight.w600,
          color: Color(0xFF3A6B54)));

  Widget _eyeIcon({required bool visible, required VoidCallback onTap}) =>
      IconButton(
        icon: Icon(
          visible ? Icons.visibility_off_outlined : Icons.visibility_outlined,
          color: _hintGreen,
          size: 20,
        ),
        onPressed: onTap,
      );

  Widget _field({
    required TextEditingController controller,
    required String hint,
    required IconData icon,
    bool obscure = false,
    Widget? suffix,
    TextInputType? keyboardType,
    String? Function(String?)? validator,
  }) {
    return TextFormField(
      controller: controller,
      obscureText: obscure,
      keyboardType: keyboardType,
      validator: validator,
      style: const TextStyle(fontSize: 15, color: Color(0xFF1A3D2E)),
      decoration: InputDecoration(
        hintText: hint,
        prefixIcon: Icon(icon, color: _hintGreen, size: 20),
        suffixIcon: suffix,
      ),
    );
  }
}