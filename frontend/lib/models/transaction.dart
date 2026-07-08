class Transaction {
  final int id;
  final String personName;
  final double amount;
  final String transactionType; // 'credit' | 'debit'
  final String? description;
  final String? transcript;
  final DateTime createdAt;

  Transaction({
    required this.id,
    required this.personName,
    required this.amount,
    required this.transactionType,
    this.description,
    this.transcript,
    required this.createdAt,
  });

  /// Backend sends the date field as "date", not "created_at".
  /// Defensive parsing — never crashes on null/missing fields.
  factory Transaction.fromJson(Map<String, dynamic> json) {
    return Transaction(
      id: json['id'] as int? ?? 0,
      personName: (json['person_name'] as String?)?.trim().isNotEmpty == true
          ? json['person_name'] as String
          : 'Unknown',
      amount: (json['amount'] as num?)?.toDouble() ?? 0.0,
      transactionType: (json['transaction_type'] as String?) ?? 'debit',
      description: json['description'] as String?,
      transcript: json['transcript'] as String?,
      createdAt: _parseDate(json['date'] ?? json['created_at']),
    );
  }

  static DateTime _parseDate(dynamic value) {
    if (value == null) return DateTime.now();
    if (value is String && value.isNotEmpty) {
      try {
        return DateTime.parse(value);
      } catch (_) {
        return DateTime.now();
      }
    }
    return DateTime.now();
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'person_name': personName,
        'amount': amount,
        'transaction_type': transactionType,
        'description': description,
        'transcript': transcript,
        'date': createdAt.toIso8601String(),
      };
}