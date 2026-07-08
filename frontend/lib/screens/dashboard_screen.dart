import 'package:flutter/material.dart';
import '../services/transaction_service.dart';
import '../models/transaction.dart' as tx_model;

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  static const _teal       = Color(0xFF2DC98E);
  static const _lightGreen = Color(0xFFF0FAF4);
  static const _hintGreen  = Color(0xFF7A9E8A);
  static const _darkGreen  = Color(0xFF1A3D2E);

  Map<String, dynamic>? _summary;
  List<tx_model.Transaction> _recent = [];
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() { _loading = true; _error = null; });
    try {
      final summary = await TransactionService.getSummary();
      final all     = await TransactionService.getAll();
      setState(() {
        _summary = summary;
        _recent  = all.take(5).toList();
        _loading = false;
      });
    } catch (e) {
      setState(() { _error = e.toString(); _loading = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _lightGreen,
      body: SafeArea(
        child: RefreshIndicator(
          color: _teal,
          onRefresh: _load,
          child: CustomScrollView(
            slivers: [
              // ── Header ─────────────────────────────────────────
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(24, 24, 24, 0),
                  child: Row(
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: const [
                            Text('Dukan Dost',
                                style: TextStyle(
                                    fontSize: 22,
                                    fontWeight: FontWeight.w900,
                                    color: _teal,
                                    letterSpacing: 1)),
                            SizedBox(height: 2),
                            Text('Your shop summary',
                                style:
                                    TextStyle(fontSize: 13, color: _hintGreen)),
                          ],
                        ),
                      ),
                      CircleAvatar(
                        backgroundColor: _teal.withOpacity(0.15),
                        radius: 22,
                        child: const Icon(Icons.storefront_rounded,
                            color: _teal, size: 22),
                      ),
                    ],
                  ),
                ),
              ),

              if (_loading)
                const SliverFillRemaining(
                  child:
                      Center(child: CircularProgressIndicator(color: _teal)),
                )
              else if (_error != null)
                SliverFillRemaining(
                  child: Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.wifi_off_rounded,
                            color: _hintGreen, size: 48),
                        const SizedBox(height: 12),
                        Text('Could not connect\n$_error',
                            textAlign: TextAlign.center,
                            style: const TextStyle(color: _hintGreen)),
                        const SizedBox(height: 16),
                        TextButton.icon(
                          onPressed: _load,
                          icon: const Icon(Icons.refresh, color: _teal),
                          label: const Text('Retry',
                              style: TextStyle(color: _teal)),
                        ),
                      ],
                    ),
                  ),
                )
              else ...[
                // ── Summary cards ───────────────────────────────
                SliverToBoxAdapter(
                  child: Padding(
                    padding: const EdgeInsets.fromLTRB(24, 24, 24, 0),
                    child: Row(
                      children: [
                        Expanded(
                          child: _SummaryCard(
                            label: 'Total Credit',
                            value: 'Rs ${_summary?['total_credit'] ?? 0}',
                            icon: Icons.arrow_downward_rounded,
                            color: _teal,
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: _SummaryCard(
                            label: 'Total Debit',
                            value: 'Rs ${_summary?['total_debit'] ?? 0}',
                            icon: Icons.arrow_upward_rounded,
                            color: Colors.redAccent,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),

                SliverToBoxAdapter(
                  child: Padding(
                    padding: const EdgeInsets.fromLTRB(24, 16, 24, 0),
                    child: _SummaryCard(
                      label: 'Net Balance',
                      value: 'Rs ${_summary?['overall_balance'] ?? 0}',
                      icon: Icons.account_balance_wallet_outlined,
                      color: Colors.deepPurple,
                      wide: true,
                    ),
                  ),
                ),

                // ── Recent header ───────────────────────────────
                SliverToBoxAdapter(
                  child: Padding(
                    padding: const EdgeInsets.fromLTRB(24, 28, 24, 12),
                    child: const Text('Recent Transactions',
                        style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w700,
                            color: _darkGreen)),
                  ),
                ),

                if (_recent.isEmpty)
                  const SliverToBoxAdapter(
                    child: Padding(
                      padding: EdgeInsets.symmetric(horizontal: 24),
                      child: Text(
                          'No transactions yet. Use the mic button to add one!',
                          style: TextStyle(color: _hintGreen)),
                    ),
                  )
                else
                  SliverList(
                    delegate: SliverChildBuilderDelegate(
                      (_, i) => Padding(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 24, vertical: 4),
                        child: _DashTxTile(_recent[i]),
                      ),
                      childCount: _recent.length,
                    ),
                  ),

                const SliverToBoxAdapter(child: SizedBox(height: 100)),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

// ── Summary card widget ─────────────────────────────────────────────
class _SummaryCard extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;
  final Color color;
  final bool wide;

  const _SummaryCard({
    required this.label,
    required this.value,
    required this.icon,
    required this.color,
    this.wide = false,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFDDF0E8), width: 1),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: color.withOpacity(0.12),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, color: color, size: 20),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(label,
                    style: const TextStyle(
                        fontSize: 12, color: Color(0xFF7A9E8A))),
                const SizedBox(height: 4),
                Text(value,
                    style: TextStyle(
                        fontSize: wide ? 20 : 18,
                        fontWeight: FontWeight.w800,
                        color: const Color(0xFF1A3D2E))),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// ── Transaction tile (named _DashTxTile to avoid clash with tx screen) ──
class _DashTxTile extends StatelessWidget {
  final tx_model.Transaction tx;
  const _DashTxTile(this.tx);

  @override
  Widget build(BuildContext context) {
    final isCredit = tx.transactionType == 'credit';
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFFDDF0E8), width: 1),
      ),
      child: Row(
        children: [
          CircleAvatar(
            radius: 20,
            backgroundColor: isCredit
                ? const Color(0xFFE6FAF3)
                : const Color(0xFFFFEEEE),
            child: Icon(
              isCredit
                  ? Icons.arrow_downward_rounded
                  : Icons.arrow_upward_rounded,
              color: isCredit ? const Color(0xFF2DC98E) : Colors.redAccent,
              size: 18,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(tx.personName,
                    style: const TextStyle(
                        fontWeight: FontWeight.w600,
                        fontSize: 14,
                        color: Color(0xFF1A3D2E))),
                if (tx.description != null && tx.description!.isNotEmpty)
                  Text(tx.description!,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                          fontSize: 12, color: Color(0xFF7A9E8A))),
              ],
            ),
          ),
          Text(
            '${isCredit ? '+' : '−'} Rs ${tx.amount.toStringAsFixed(0)}',
            style: TextStyle(
                fontWeight: FontWeight.w700,
                fontSize: 14,
                color: isCredit
                    ? const Color(0xFF2DC98E)
                    : Colors.redAccent),
          ),
        ],
      ),
    );
  }
}