import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../services/transaction_service.dart';
import '../models/transaction.dart' as tx_model;

class TransactionsScreen extends StatefulWidget {
  const TransactionsScreen({super.key});

  @override
  State<TransactionsScreen> createState() => _TransactionsScreenState();
}

class _TransactionsScreenState extends State<TransactionsScreen> {
  static const _teal       = Color(0xFF2DC98E);
  static const _lightGreen = Color(0xFFF0FAF4);
  static const _hintGreen  = Color(0xFF7A9E8A);
  static const _darkGreen  = Color(0xFF1A3D2E);

  List<tx_model.Transaction> _all      = [];
  List<tx_model.Transaction> _filtered = [];
  bool _loading = true;
  String? _error;
  String _filter = 'all';
  final _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _load();
    _searchController.addListener(_applyFilter);
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    setState(() { _loading = true; _error = null; });
    try {
      final data = await TransactionService.getAll();
      setState(() { _all = data; _loading = false; });
      _applyFilter();
    } catch (e) {
      setState(() { _error = e.toString(); _loading = false; });
    }
  }

  void _applyFilter() {
    final q = _searchController.text.toLowerCase();
    setState(() {
      _filtered = _all.where((tx) {
        final matchType = _filter == 'all' || tx.transactionType == _filter;
        final matchSearch = tx.personName.toLowerCase().contains(q) ||
            (tx.description ?? '').toLowerCase().contains(q);
        return matchType && matchSearch;
      }).toList();
    });
  }

  void _setFilter(String f) {
    setState(() => _filter = f);
    _applyFilter();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _lightGreen,
      body: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(24, 24, 24, 0),
              child: const Text('Ledger',
                  style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.w800,
                      color: _darkGreen)),
            ),

            const SizedBox(height: 16),

            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24),
              child: TextField(
                controller: _searchController,
                style: const TextStyle(fontSize: 14, color: _darkGreen),
                decoration: const InputDecoration(
                  hintText: 'Search by name or description...',
                  prefixIcon:
                      Icon(Icons.search_rounded, color: _hintGreen, size: 20),
                ),
              ),
            ),

            const SizedBox(height: 12),

            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24),
              child: Row(
                children: [
                  _chip('All', 'all'),
                  const SizedBox(width: 8),
                  _chip('Credit', 'credit'),
                  const SizedBox(width: 8),
                  _chip('Debit', 'debit'),
                ],
              ),
            ),

            const SizedBox(height: 12),

            Expanded(
              child: _loading
                  ? const Center(
                      child: CircularProgressIndicator(color: _teal))
                  : _error != null
                      ? Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              const Icon(Icons.wifi_off_rounded,
                                  color: _hintGreen, size: 48),
                              const SizedBox(height: 12),
                              Text(_error!,
                                  textAlign: TextAlign.center,
                                  style:
                                      const TextStyle(color: _hintGreen)),
                              const SizedBox(height: 16),
                              TextButton.icon(
                                onPressed: _load,
                                icon: const Icon(Icons.refresh, color: _teal),
                                label: const Text('Retry',
                                    style: TextStyle(color: _teal)),
                              ),
                            ],
                          ),
                        )
                      : _filtered.isEmpty
                          ? const Center(
                              child: Text('No transactions found.',
                                  style: TextStyle(color: _hintGreen)))
                          : RefreshIndicator(
                              color: _teal,
                              onRefresh: _load,
                              child: ListView.separated(
                                padding: const EdgeInsets.symmetric(
                                    horizontal: 24, vertical: 8),
                                itemCount: _filtered.length,
                                separatorBuilder: (_, __) =>
                                    const SizedBox(height: 8),
                                itemBuilder: (_, i) => _TxCard(_filtered[i]),
                              ),
                            ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _chip(String label, String value) {
    final selected = _filter == value;
    return GestureDetector(
      onTap: () => _setFilter(value),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: selected ? _teal : Colors.white,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: selected ? _teal : const Color(0xFFB2DFD0),
            width: 1.2,
          ),
        ),
        child: Text(label,
            style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w600,
                color: selected ? Colors.white : _hintGreen)),
      ),
    );
  }
}

class _TxCard extends StatelessWidget {
  final tx_model.Transaction tx;
  const _TxCard(this.tx);

  @override
  Widget build(BuildContext context) {
    final isCredit = tx.transactionType == 'credit';
    final dateStr =
        DateFormat('dd MMM, hh:mm a').format(tx.createdAt.toLocal());
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFDDF0E8), width: 1),
      ),
      child: Row(
        children: [
          Container(
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              color: isCredit
                  ? const Color(0xFFE6FAF3)
                  : const Color(0xFFFFEEEE),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(
              isCredit ? Icons.south_rounded : Icons.north_rounded,
              color:
                  isCredit ? const Color(0xFF2DC98E) : Colors.redAccent,
              size: 22,
            ),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(tx.personName,
                    style: const TextStyle(
                        fontWeight: FontWeight.w700,
                        fontSize: 15,
                        color: Color(0xFF1A3D2E))),
                if (tx.description != null && tx.description!.isNotEmpty)
                  Text(tx.description!,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                          fontSize: 12, color: Color(0xFF7A9E8A))),
                Text(dateStr,
                    style: const TextStyle(
                        fontSize: 11, color: Color(0xFFADD4C2))),
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                '${isCredit ? '+' : '−'} Rs ${tx.amount.toStringAsFixed(0)}',
                style: TextStyle(
                    fontWeight: FontWeight.w800,
                    fontSize: 15,
                    color: isCredit
                        ? const Color(0xFF2DC98E)
                        : Colors.redAccent),
              ),
              const SizedBox(height: 4),
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: isCredit
                      ? const Color(0xFFE6FAF3)
                      : const Color(0xFFFFEEEE),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Text(
                  isCredit ? 'Credit' : 'Debit',
                  style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w600,
                      color: isCredit
                          ? const Color(0xFF2DC98E)
                          : Colors.redAccent),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}