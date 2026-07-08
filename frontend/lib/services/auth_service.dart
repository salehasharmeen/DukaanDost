import '../core/api_client.dart';

class AuthService {
  static Future<void> signup({
    required String email,
    required String password,
    String? shopName,
  }) async {
    final res = await ApiClient.instance.post('/signup', data: {
      'email': email,
      'password': password,
      'shop_name': shopName,
    });
    final token = res.data['access_token'] as String;
    await ApiClient.setToken(token);
  }

  static Future<void> login({
    required String email,
    required String password,
  }) async {
    final res = await ApiClient.instance.post('/login', data: {
      'email': email,
      'password': password,
    });
    final token = res.data['access_token'] as String;
    await ApiClient.setToken(token);
  }

  static Future<void> logout() async {
    await ApiClient.clearToken();
  }

  static bool get isLoggedIn => ApiClient.isLoggedIn;

  /// Fetches the logged-in user's profile info (email, shop_name)
  /// from GET /me. Used by ProfileScreen.
  static Future<Map<String, dynamic>> getProfile() async {
    final res = await ApiClient.instance.get('/me');
    return res.data as Map<String, dynamic>;
  }
}