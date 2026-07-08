import 'package:flutter/material.dart';
import '../services/voice_service.dart';

class VoiceScreen extends StatefulWidget {
  const VoiceScreen({super.key});

  @override
  State<VoiceScreen> createState() => _VoiceScreenState();
}

class _VoiceScreenState extends State<VoiceScreen>
    with SingleTickerProviderStateMixin {
  static const _teal       = Color(0xFF2DC98E);
  static const _lightGreen = Color(0xFFF0FAF4);
  static const _hintGreen  = Color(0xFF7A9E8A);
  static const _darkGreen  = Color(0xFF1A3D2E);

  bool _recording = false;
  bool _loading   = false;
  Map<String, dynamic>? _result;
  String? _error;

  late AnimationController _pulseController;
  late Animation<double>   _pulseAnimation;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 900),
    );
    _pulseAnimation = Tween<double>(begin: 1.0, end: 1.18).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  Future<void> _toggle() async {
    if (_loading) return;
    if (_recording) {
      _pulseController.stop();
      _pulseController.reset();
      setState(() { _recording = false; _loading = true; _result = null; _error = null; });
      try {
        final res = await VoiceService.stopAndTranscribe();
        // ignore: avoid_print
        print('VOICE RESULT: $res'); // debug visibility in Flutter logs
        setState(() { _result = res; _loading = false; });
      } catch (e) {
        setState(() { _error = e.toString(); _loading = false; });
      }
    } else {
      setState(() { _recording = true; _result = null; _error = null; });
      _pulseController.repeat(reverse: true);
      try {
        await VoiceService.startRecording();
      } catch (e) {
        _pulseController.stop();
        setState(() { _recording = false; _error = e.toString(); });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _lightGreen,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 28),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 28),
              const Text('Voice Entry',
                  style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.w800,
                      color: _darkGreen)),
              const SizedBox(height: 6),
              const Text('Record a transaction in Punjabi',
                  style: TextStyle(fontSize: 14, color: _hintGreen)),

              const SizedBox(height: 40),

              // Hint box
              Container(
                padding: const EdgeInsets.symmetric(
                    horizontal: 20, vertical: 14),
                decoration: BoxDecoration(
                  color: _teal.withOpacity(0.08),
                  borderRadius: BorderRadius.circular(14),
                  border:
                      Border.all(color: _teal.withOpacity(0.2), width: 1),
                ),
                child: Row(
                  children: const [
                    Icon(Icons.info_outline_rounded, color: _teal, size: 18),
                    SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        'Try: "Akmal ko 500 rupay diye"\nor "Ali ne aloo de do kilo bechay te 200 rupay mile"',
                        style: TextStyle(
                            fontSize: 13,
                            color: Color(0xFF3A6B54),
                            height: 1.5),
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 40),

              // Mic button
              Center(
                child: GestureDetector(
                  onTap: _toggle,
                  child: _loading
                      ? Container(
                          width: 100,
                          height: 100,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: _teal.withOpacity(0.15),
                          ),
                          child: const Center(
                            child: CircularProgressIndicator(
                                color: _teal, strokeWidth: 3),
                          ),
                        )
                      : AnimatedBuilder(
                          animation: _pulseAnimation,
                          builder: (_, child) => Transform.scale(
                            scale: _recording ? _pulseAnimation.value : 1.0,
                            child: child,
                          ),
                          child: Container(
                            width: 100,
                            height: 100,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              color: _recording ? Colors.redAccent : _teal,
                              boxShadow: [
                                BoxShadow(
                                  color: (_recording
                                          ? Colors.redAccent
                                          : _teal)
                                      .withOpacity(0.35),
                                  blurRadius: 24,
                                  offset: const Offset(0, 6),
                                ),
                              ],
                            ),
                            child: Icon(
                              _recording
                                  ? Icons.stop_rounded
                                  : Icons.mic_rounded,
                              color: Colors.white,
                              size: 44,
                            ),
                          ),
                        ),
                ),
              ),

              const SizedBox(height: 20),

              Center(
                child: AnimatedSwitcher(
                  duration: const Duration(milliseconds: 300),
                  child: Text(
                    _loading
                        ? 'Transcribing...'
                        : _recording
                            ? 'Tap to stop'
                            : 'Tap to record',
                    key: ValueKey(_recording || _loading),
                    style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w600,
                        color: _recording ? Colors.redAccent : _hintGreen),
                  ),
                ),
              ),

              const SizedBox(height: 32),

              if (_error != null)
                _StatusCard(
                    icon: Icons.error_outline_rounded,
                    color: Colors.redAccent,
                    title: 'Error',
                    body: _error!),

              // ── Result card — now handles EVERY possible backend response ──
              if (_result != null) _buildResultCard(_result!),

              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }

  /// Builds the right card based on whatever the backend actually returned.
  /// Handles: transaction saved, unclear audio, delete command, AND
  /// any unexpected/unknown shape — so the screen never silently shows nothing.
  Widget _buildResultCard(Map<String, dynamic> result) {
    final intent = result['intent'] as String?;

    // 🔍 Spoken query — "akmal da hisab dikhao" etc.
    if (intent == 'query') {
      final queryType = result['query_type'] as String?;

      if (queryType == 'customer_balance' && result['result'] != null) {
        final r = result['result'] as Map<String, dynamic>;
        return _StatusCard(
          icon: Icons.account_balance_wallet_outlined,
          color: Colors.deepPurple,
          title: 'Customer Balance',
          body: '',
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _row('Customer', '${r['customer'] ?? '-'}'),
              _row('Total Credit', 'Rs ${r['total_credit'] ?? 0}'),
              _row('Total Debit', 'Rs ${r['total_debit'] ?? 0}'),
              _row('Balance', 'Rs ${r['balance'] ?? 0}'),
            ],
          ),
        );
      }

      if (queryType == 'all_transactions') {
        return _StatusCard(
          icon: Icons.list_alt_rounded,
          color: Colors.deepPurple,
          title: 'All Transactions',
          body: 'Found ${result['total'] ?? 0} transactions. '
              'Check the Ledger tab to view them.',
        );
      }

      if (queryType == 'summary') {
        final r = result['result'] as Map<String, dynamic>?;
        return _StatusCard(
          icon: Icons.summarize_outlined,
          color: Colors.deepPurple,
          title: 'Shop Summary',
          body: '',
          child: r != null
              ? Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _row('Total Customers', '${r['total_customers'] ?? 0}'),
                    _row('Total Transactions', '${r['total_transactions'] ?? 0}'),
                    _row('Net Balance', 'Rs ${r['overall_balance'] ?? 0}'),
                  ],
                )
              : null,
        );
      }

      // Query detected but couldn't figure out what was asked
      return _StatusCard(
        icon: Icons.help_outline_rounded,
        color: Colors.orange,
        title: 'Query Not Understood',
        body: result['error']?.toString() ??
            'Recognized this as a question, but could not determine '
                'what you wanted to know.',
        child: result['transcript'] != null
            ? _row('Heard', '${result['transcript']}')
            : null,
      );
    }

    // ✅ Normal transaction saved
    if (intent == 'transaction' && result['data'] != null) {
      final d = result['data'] as Map<String, dynamic>;
      return _StatusCard(
        icon: Icons.check_circle_outline_rounded,
        color: _teal,
        title: 'Transaction Saved!',
        body: '',
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _row('Person', '${d['person_name'] ?? 'Unknown'}'),
            _row('Amount', 'Rs ${d['amount'] ?? 0}'),
            _row('Type',   '${d['transaction_type'] ?? '-'}'),
            if (d['transcript'] != null && '${d['transcript']}'.isNotEmpty)
              _row('Heard', '${d['transcript']}'),
            if (d['description'] != null && '${d['description']}'.isNotEmpty)
              _row('Note', '${d['description']}'),
          ],
        ),
      );
    }

    // ⚠️ Backend explicitly flagged unclear/noisy audio
    if (intent == 'unclear' ||
        result['warning'] == 'prompt_bleed' ||
        result['message'] == 'Audio unclear, nothing saved') {
      return _StatusCard(
        icon: Icons.hearing_disabled_rounded,
        color: Colors.orange,
        title: 'Audio Unclear',
        body: 'Could not understand the recording clearly. '
            'Try speaking closer to the mic, in a quiet area.',
        child: result['transcript'] != null
            ? _row('Heard', '${result['transcript']}')
            : null,
      );
    }

    // 🗑️ Delete/cancel command detected
    if (intent == 'delete' || result['warning'] == 'delete_intent') {
      return _StatusCard(
        icon: Icons.delete_outline_rounded,
        color: Colors.blueGrey,
        title: 'Delete Command Detected',
        body: result['message']?.toString() ??
            'Detected a delete/cancel request. Use the Ledger screen '
                'to remove the specific entry.',
        child: result['person_name'] != null
            ? _row('For', '${result['person_name']}')
            : null,
      );
    }

    // ❓ Anything else — show raw response instead of silently doing nothing.
    // This is the key fix: you'll NEVER see a blank "nothing happened" again.
    return _StatusCard(
      icon: Icons.help_outline_rounded,
      color: Colors.deepPurple,
      title: 'Unexpected Response',
      body: 'The server replied but in an unexpected format. '
          'Raw response below (useful for debugging):',
      child: Text(
        result.toString(),
        style: const TextStyle(fontSize: 11, color: Color(0xFF7A9E8A)),
      ),
    );
  }

  Widget _row(String label, String value) => Padding(
        padding: const EdgeInsets.symmetric(vertical: 3),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('$label: ',
                style: const TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF3A6B54))),
            Expanded(
              child: Text(value,
                  style: const TextStyle(
                      fontSize: 13, color: Color(0xFF1A3D2E))),
            ),
          ],
        ),
      );
}

class _StatusCard extends StatelessWidget {
  final IconData icon;
  final Color color;
  final String title;
  final String body;
  final Widget? child;

  const _StatusCard({
    required this.icon,
    required this.color,
    required this.title,
    required this.body,
    this.child,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withOpacity(0.3), width: 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(children: [
            Icon(icon, color: color, size: 20),
            const SizedBox(width: 8),
            Expanded(
              child: Text(title,
                  style: TextStyle(
                      fontWeight: FontWeight.w700, fontSize: 14, color: color)),
            ),
          ]),
          if (body.isNotEmpty) ...[
            const SizedBox(height: 8),
            Text(body,
                style: const TextStyle(
                    fontSize: 13, color: Color(0xFF7A9E8A))),
          ],
          if (child != null) ...[
            const SizedBox(height: 8),
            child!,
          ],
        ],
      ),
    );
  }
}