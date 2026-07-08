import 'package:flutter/material.dart';
import '../services/transaction_service.dart';

class CustomerScreen extends StatefulWidget {
  const CustomerScreen({super.key});

  @override
  State<CustomerScreen> createState() => _CustomerScreenState();
}

class _CustomerScreenState extends State<CustomerScreen> {
  static const _teal       = Color(0xFF2DC98E);
  static const _lightGreen = Color(0xFFF0FAF4);
  static const _hintGreen  = Color(0xFF7A9E8A);
  static const _darkGreen  = Color(0xFF1A3D2E);

  final _nameController = TextEditingController();
  bool _loading = false;
  Map<String, dynamic>? _result;
  String? _error;

  @override
  void dispose() {
    _nameController.dispose();
    super.dispose();
  }

  Future<void> _search() async {
    final name = _nameController.text.trim();
    if (name.isEmpty) return;
    FocusScope.of(context).unfocus();
    setState(() { _loading = true; _result = null; _error = null; });
    try {
      final data = await TransactionService.getCustomerSummary(name);
      setState(() { _result = data; _loading = false; });
    } catch (e) {
      setState(() { _error = 'Customer not found or server error.'; _loading = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _lightGreen,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 28),
              const Text('Customer Ledger',
                  style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.w800,
                      color: _darkGreen)),
              const SizedBox(height: 6),
              const Text('Look up a customer balance',
                  style: TextStyle(fontSize: 14, color: _hintGreen)),
              const SizedBox(height: 28),

              // Search row
              Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _nameController,
                      style: const TextStyle(fontSize: 15, color: _darkGreen),
                      onSubmitted: (_) => _search(),
                      decoration: const InputDecoration(
                        hintText: 'Enter customer name...',
                        prefixIcon: Icon(Icons.person_search_rounded,
                            color: _hintGreen, size: 20),
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  SizedBox(
                    height: 50,
                    child: ElevatedButton(
                      onPressed: _loading ? null : _search,
                      style: ElevatedButton.styleFrom(
                        shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(14)),
                        padding: const EdgeInsets.symmetric(horizontal: 20),
                      ),
                      child: _loading
                          ? const SizedBox(
                              width: 20,
                              height: 20,
                              child: CircularProgressIndicator(
                                  color: Colors.white, strokeWidth: 2.5),
                            )
                          : const Icon(Icons.search_rounded, size: 22),
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 28),

              if (_error != null)
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.redAccent.withOpacity(0.08),
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(
                        color: Colors.redAccent.withOpacity(0.3)),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.person_off_rounded,
                          color: Colors.redAccent, size: 20),
                      const SizedBox(width: 10),
                      Expanded(
                          child: Text(_error!,
                              style: const TextStyle(
                                  color: Colors.redAccent, fontSize: 13))),
                    ],
                  ),
                ),

              if (_result != null) ...[
                // Balance hero card
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: _teal,
                    borderRadius: BorderRadius.circular(18),
                    boxShadow: [
                      BoxShadow(
                          color: _teal.withOpacity(0.3),
                          blurRadius: 16,
                          offset: const Offset(0, 6)),
                    ],
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          const CircleAvatar(
                            radius: 22,
                            backgroundColor: Colors.white24,
                            child: Icon(Icons.person_rounded,
                                color: Colors.white, size: 22),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              _result!['customer_name'] ??
                                  _nameController.text,
                              style: const TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.w800,
                                  color: Colors.white),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 20),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceAround,
                        children: [
                          _stat('Total Credit',
                              'Rs ${_result!['total_credit'] ?? 0}'),
                          _vDivider(),
                          _stat('Total Debit',
                              'Rs ${_result!['total_debit'] ?? 0}'),
                          _vDivider(),
                          _stat('Balance',
                              'Rs ${_result!['balance'] ?? 0}'),
                        ],
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 24),
                const Text('Transaction History',
                    style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w700,
                        color: _darkGreen)),
                const SizedBox(height: 12),

                if (_result!['transactions'] != null)
                  Expanded(
                    child: ListView.separated(
                      itemCount:
                          (_result!['transactions'] as List).length,
                      separatorBuilder: (_, __) =>
                          const SizedBox(height: 8),
                      itemBuilder: (_, i) {
                        final tx = (_result!['transactions'] as List)[i]
                            as Map<String, dynamic>;
                        final isCredit =
                            tx['transaction_type'] == 'credit';
                        return Container(
                          padding: const EdgeInsets.all(14),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(14),
                            border: Border.all(
                                color: const Color(0xFFDDF0E8), width: 1),
                          ),
                          child: Row(
                            children: [
                              Container(
                                width: 38,
                                height: 38,
                                decoration: BoxDecoration(
                                  color: isCredit
                                      ? const Color(0xFFE6FAF3)
                                      : const Color(0xFFFFEEEE),
                                  borderRadius: BorderRadius.circular(10),
                                ),
                                child: Icon(
                                  isCredit
                                      ? Icons.south_rounded
                                      : Icons.north_rounded,
                                  color: isCredit ? _teal : Colors.redAccent,
                                  size: 18,
                                ),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Text(
                                  tx['description'] ??
                                      tx['transaction_type'],
                                  style: const TextStyle(
                                      fontSize: 13, color: _darkGreen),
                                ),
                              ),
                              Text(
                                '${isCredit ? '+' : '−'} Rs ${tx['amount']}',
                                style: TextStyle(
                                    fontWeight: FontWeight.w700,
                                    fontSize: 14,
                                    color: isCredit
                                        ? _teal
                                        : Colors.redAccent),
                              ),
                            ],
                          ),
                        );
                      },
                    ),
                  ),
              ],

              if (_result == null && _error == null && !_loading) ...[
                const Spacer(),
                Center(
                  child: Column(
                    children: [
                      Icon(Icons.manage_search_rounded,
                          size: 64,
                          color: _teal.withOpacity(0.25)),
                      const SizedBox(height: 12),
                      const Text(
                        'Enter a customer name above\nto see their ledger',
                        textAlign: TextAlign.center,
                        style:
                            TextStyle(color: _hintGreen, fontSize: 14),
                      ),
                    ],
                  ),
                ),
                const Spacer(),
              ],

              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }

  Widget _stat(String label, String value) => Column(
        children: [
          Text(label,
              style: const TextStyle(
                  fontSize: 11,
                  color: Colors.white70,
                  fontWeight: FontWeight.w500)),
          const SizedBox(height: 4),
          Text(value,
              style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w800,
                  color: Colors.white)),
        ],
      );

  Widget _vDivider() =>
      Container(width: 1, height: 36, color: Colors.white24);
}