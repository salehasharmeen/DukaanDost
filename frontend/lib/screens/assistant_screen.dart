import 'package:flutter/material.dart';
import '../services/assistant_service.dart';

class AssistantScreen extends StatefulWidget {
  const AssistantScreen({super.key});

  @override
  State<AssistantScreen> createState() => _AssistantScreenState();
}

class _AssistantScreenState extends State<AssistantScreen> {
  static const _teal       = Color(0xFF2DC98E);
  static const _lightGreen = Color(0xFFF0FAF4);
  static const _hintGreen  = Color(0xFF7A9E8A);
  static const _darkGreen  = Color(0xFF1A3D2E);

  final _textController   = TextEditingController();
  final _scrollController = ScrollController();
  final List<_Msg> _messages = [];
  bool _loading = false;

  static const _suggestions = [
    'Akmal ka hisab dikhao',
    'Sab transactions dikhao',
    'Ali ne kitna dena hai?',
  ];

  @override
  void dispose() {
    _textController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _send([String? override]) async {
    final text = override ?? _textController.text.trim();
    if (text.isEmpty || _loading) return;
    _textController.clear();
    setState(() {
      _messages.add(_Msg(text: text, isUser: true));
      _loading = true;
    });
    _scroll();
    try {
      final res   = await AssistantService.query(text);
      final reply = _format(res);
      setState(() {
        _messages.add(_Msg(text: reply, isUser: false));
        _loading = false;
      });
    } catch (e) {
      setState(() {
        _messages.add(_Msg(text: 'Server error: $e', isUser: false, isError: true));
        _loading = false;
      });
    }
    _scroll();
  }

  String _format(Map<String, dynamic> res) {
    if (res['intent'] == 'query') {
      final r = res['result'];
      if (r == null) return 'No result found.';
      if (r is Map) {
        return '${r['customer_name'] ?? ''}\n'
            '• Credit: Rs ${r['total_credit'] ?? 0}\n'
            '• Debit: Rs ${r['total_debit'] ?? 0}\n'
            '• Balance: Rs ${r['balance'] ?? 0}';
      }
    }
    if (res['intent'] == 'transaction') {
      final d = res['data'];
      return 'Transaction saved!\n'
          '• Person: ${d['person_name']}\n'
          '• Amount: Rs ${d['amount']}\n'
          '• Type: ${d['transaction_type']}';
    }
    return res['message'] ?? res.toString();
  }

  void _scroll() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent + 100,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _lightGreen,
      body: SafeArea(
        child: Column(
          children: [
            // Header
            Padding(
              padding: const EdgeInsets.fromLTRB(24, 24, 24, 12),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: _teal.withOpacity(0.12),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Icon(Icons.auto_awesome_rounded,
                        color: _teal, size: 22),
                  ),
                  const SizedBox(width: 12),
                  const Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Dukan Assistant',
                          style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.w800,
                              color: _darkGreen)),
                      Text('Ask in Punjabi or English',
                          style:
                              TextStyle(fontSize: 12, color: _hintGreen)),
                    ],
                  ),
                ],
              ),
            ),

            // Messages
            Expanded(
              child: _messages.isEmpty
                  ? _emptyState()
                  : ListView.builder(
                      controller: _scrollController,
                      padding: const EdgeInsets.symmetric(
                          horizontal: 20, vertical: 8),
                      itemCount: _messages.length + (_loading ? 1 : 0),
                      itemBuilder: (_, i) {
                        if (i == _messages.length && _loading) {
                          return _TypingBubble();
                        }
                        return _Bubble(_messages[i]);
                      },
                    ),
            ),

            // Suggestion chips (only when chat is empty)
            if (_messages.isEmpty) ...[
              SizedBox(
                height: 40,
                child: ListView.separated(
                  scrollDirection: Axis.horizontal,
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  itemCount: _suggestions.length,
                  separatorBuilder: (_, __) =>
                      const SizedBox(width: 8),
                  itemBuilder: (_, i) => GestureDetector(
                    onTap: () => _send(_suggestions[i]),
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 14, vertical: 8),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(
                            color: const Color(0xFFB2DFD0), width: 1.2),
                      ),
                      child: Text(_suggestions[i],
                          style: const TextStyle(
                              fontSize: 12,
                              color: Color(0xFF3A6B54),
                              fontWeight: FontWeight.w500)),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 12),
            ],

            // Input bar
            Container(
              color: Colors.white,
              padding: const EdgeInsets.fromLTRB(16, 10, 16, 16),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _textController,
                      style: const TextStyle(
                          fontSize: 14, color: _darkGreen),
                      onSubmitted: (_) => _send(),
                      decoration: const InputDecoration(
                        hintText: 'Type your query...',
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  GestureDetector(
                    onTap: _loading ? null : () => _send(),
                    child: Container(
                      width: 46,
                      height: 46,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: _loading
                            ? _teal.withOpacity(0.4)
                            : _teal,
                      ),
                      child: const Icon(Icons.send_rounded,
                          color: Colors.white, size: 20),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _emptyState() => Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.chat_bubble_outline_rounded,
                size: 64, color: _teal.withOpacity(0.2)),
            const SizedBox(height: 12),
            const Text(
              'Ask me anything about\nyour shop ledger',
              textAlign: TextAlign.center,
              style: TextStyle(
                  color: _hintGreen, fontSize: 14, height: 1.6),
            ),
          ],
        ),
      );
}

class _Msg {
  final String text;
  final bool isUser;
  final bool isError;
  const _Msg({required this.text, required this.isUser, this.isError = false});
}

class _Bubble extends StatelessWidget {
  final _Msg msg;
  const _Bubble(this.msg);

  static const _teal      = Color(0xFF2DC98E);
  static const _darkGreen = Color(0xFF1A3D2E);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Row(
        mainAxisAlignment:
            msg.isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          if (!msg.isUser) ...[
            CircleAvatar(
              radius: 16,
              backgroundColor: _teal.withOpacity(0.15),
              child: const Icon(Icons.auto_awesome_rounded,
                  color: _teal, size: 14),
            ),
            const SizedBox(width: 8),
          ],
          Flexible(
            child: Container(
              padding: const EdgeInsets.symmetric(
                  horizontal: 14, vertical: 10),
              decoration: BoxDecoration(
                color: msg.isUser
                    ? _teal
                    : msg.isError
                        ? Colors.redAccent.withOpacity(0.1)
                        : Colors.white,
                borderRadius: BorderRadius.only(
                  topLeft: const Radius.circular(16),
                  topRight: const Radius.circular(16),
                  bottomLeft: Radius.circular(msg.isUser ? 16 : 4),
                  bottomRight: Radius.circular(msg.isUser ? 4 : 16),
                ),
                border: msg.isUser
                    ? null
                    : Border.all(
                        color: msg.isError
                            ? Colors.redAccent.withOpacity(0.3)
                            : const Color(0xFFDDF0E8),
                        width: 1),
              ),
              child: Text(msg.text,
                  style: TextStyle(
                      fontSize: 14,
                      height: 1.5,
                      color: msg.isUser
                          ? Colors.white
                          : msg.isError
                              ? Colors.redAccent
                              : _darkGreen)),
            ),
          ),
          if (msg.isUser) const SizedBox(width: 8),
        ],
      ),
    );
  }
}

class _TypingBubble extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Row(
        children: [
          CircleAvatar(
            radius: 16,
            backgroundColor: const Color(0xFF2DC98E).withOpacity(0.15),
            child: const Icon(Icons.auto_awesome_rounded,
                color: Color(0xFF2DC98E), size: 14),
          ),
          const SizedBox(width: 8),
          Container(
            padding: const EdgeInsets.symmetric(
                horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(16),
                topRight: Radius.circular(16),
                bottomLeft: Radius.circular(4),
                bottomRight: Radius.circular(16),
              ),
              border: Border.all(
                  color: const Color(0xFFDDF0E8), width: 1),
            ),
            child: const SizedBox(
                width: 40, height: 14, child: _Dots()),
          ),
        ],
      ),
    );
  }
}

class _Dots extends StatefulWidget {
  const _Dots();

  @override
  State<_Dots> createState() => _DotsState();
}

class _DotsState extends State<_Dots> with SingleTickerProviderStateMixin {
  late AnimationController _c;

  @override
  void initState() {
    super.initState();
    _c = AnimationController(
        vsync: this, duration: const Duration(milliseconds: 900))
      ..repeat();
  }

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _c,
      builder: (_, __) => Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: List.generate(3, (i) {
          final delay   = i * 0.33;
          final t       = ((_c.value - delay) % 1.0).clamp(0.0, 1.0);
          final opacity = (0.3 + 0.7 * (t < 0.5 ? t * 2 : (1 - t) * 2))
              .clamp(0.3, 1.0);
          return Opacity(
            opacity: opacity,
            child: Container(
              width: 6,
              height: 6,
              decoration: const BoxDecoration(
                  shape: BoxShape.circle, color: Color(0xFF7A9E8A)),
            ),
          );
        }),
      ),
    );
  }
}