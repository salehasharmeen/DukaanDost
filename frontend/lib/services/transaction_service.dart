import '../core/api_client.dart';
import '../models/transaction.dart';

class TransactionService {
  /// GET /transactions
  /// Skips any individual record that fails to parse instead of
  /// crashing the whole list — old/malformed test entries won't
  /// take down the Dashboard or Ledger screen anymore.
  static Future<List<Transaction>> getAll() async {
    final res = await ApiClient.instance.get('/transactions');
    final list = res.data as List<dynamic>;

    final List<Transaction> result = [];
    for (final item in list) {
      try {
        result.add(Transaction.fromJson(item as Map<String, dynamic>));
      } catch (e) {
        // Skip malformed record, log for debugging, keep going.
        // ignore: avoid_print
        print('Skipped malformed transaction: $e — raw: $item');
      }
    }
    // Newest first
    result.sort((a, b) => b.createdAt.compareTo(a.createdAt));
    return result;
  }

  /// GET /customer/{customer_name}
  static Future<Map<String, dynamic>> getCustomerSummary(String name) async {
    final res = await ApiClient.instance.get('/customer/$name');
    return res.data as Map<String, dynamic>;
  }

  /// GET /summary
  static Future<Map<String, dynamic>> getSummary() async {
    final res = await ApiClient.instance.get('/summary');
    return res.data as Map<String, dynamic>;
  }
}