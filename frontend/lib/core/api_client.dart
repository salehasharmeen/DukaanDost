import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Global callback the app can set so ApiClient can trigger a
/// navigation-to-login when the session becomes invalid (401).
/// main.dart wires this up once, at startup.
typedef OnUnauthorized = void Function();

class ApiClient {
  static const String _emulatorUrl = 'http://10.0.2.2:8000';
  static const String _deviceUrl   = 'http://10.253.164.108:8000'; // <-- current hotspot IP

  static const bool _useEmulator = false;

  static String get baseUrl => _useEmulator ? _emulatorUrl : _deviceUrl;

  static OnUnauthorized? onUnauthorized;

  static final Dio _dio = Dio(
    BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: const Duration(seconds: 15),
      receiveTimeout: const Duration(seconds: 60),
      headers: {'Content-Type': 'application/json'},
    ),
  )..interceptors.add(
      InterceptorsWrapper(
        onError: (DioException error, handler) async {
          if (error.response?.statusCode == 401) {
            // ignore: avoid_print
            print('ApiClient: 401 received -> clearing stale token');
            await clearToken();
            onUnauthorized?.call(); // tells main.dart to show LoginScreen
          }
          return handler.next(error);
        },
      ),
    );

  static String? _token;
  static bool _tokenLoaded = false;

  static Future<void> loadToken() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('auth_token');
    if (_token != null && _token!.isNotEmpty) {
      _dio.options.headers['Authorization'] = 'Bearer $_token';
    }
    _tokenLoaded = true;
    // ignore: avoid_print
    print('ApiClient.loadToken() -> token loaded: ${_token != null}');
  }

  static Future<void> setToken(String token) async {
    _token = token;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('auth_token', token);
    _dio.options.headers['Authorization'] = 'Bearer $token';
  }

  static Future<void> clearToken() async {
    _token = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('auth_token');
    _dio.options.headers.remove('Authorization');
  }

  static bool get isLoggedIn {
    if (!_tokenLoaded) {
      // ignore: avoid_print
      print('WARNING: isLoggedIn checked before loadToken() finished!');
    }
    return _token != null && _token!.isNotEmpty;
  }

  static Dio get instance => _dio;
}