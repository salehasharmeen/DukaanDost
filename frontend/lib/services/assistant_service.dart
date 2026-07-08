import '../core/api_client.dart';

class AssistantService {
  /// POST /assistant/?text=...
  /// Detects intent (query vs transaction) and returns structured result
  static Future<Map<String, dynamic>> query(String text) async {
    final res = await ApiClient.instance.post(
      '/assistant/',
      queryParameters: {'text': text},
    );
    return res.data as Map<String, dynamic>;
  }

  /// POST /voice-query/?query=...
  /// Handles pure query strings (no transaction extraction)
  static Future<Map<String, dynamic>> voiceQuery(String query) async {
    final res = await ApiClient.instance.post(
      '/voice-query/',
      queryParameters: {'query': query},
    );
    return res.data as Map<String, dynamic>;
  }
}