import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/transaction.dart';
import '../services/transaction_service.dart';

/// All transactions from GET /transactions
final transactionsProvider = FutureProvider<List<Transaction>>((ref) async {
  return TransactionService.getAll();
});

/// Shop-wide summary from GET /summary
final summaryProvider =
    FutureProvider<Map<String, dynamic>>((ref) async {
  return TransactionService.getSummary();
});

/// Per-customer summary from GET /customer/{name}
final customerProvider =
    FutureProvider.family<Map<String, dynamic>, String>(
        (ref, name) async {
  return TransactionService.getCustomerSummary(name);
});