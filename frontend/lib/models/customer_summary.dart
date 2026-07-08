class CustomerSummary {
  final String customerName;
  final double totalCredit;
  final double totalDebit;
  final double balance;
  final List<Map<String, dynamic>> transactions;

  CustomerSummary({
    required this.customerName,
    required this.totalCredit,
    required this.totalDebit,
    required this.balance,
    required this.transactions,
  });

  factory CustomerSummary.fromJson(Map<String, dynamic> json) {
    return CustomerSummary(
      customerName: json['customer_name'] as String? ?? '',
      totalCredit: (json['total_credit'] as num?)?.toDouble() ?? 0.0,
      totalDebit: (json['total_debit'] as num?)?.toDouble() ?? 0.0,
      balance: (json['balance'] as num?)?.toDouble() ?? 0.0,
      transactions: (json['transactions'] as List<dynamic>?)
              ?.map((e) => e as Map<String, dynamic>)
              .toList() ??
          [],
    );
  }
}