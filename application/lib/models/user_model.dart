class User {
  final int id;
  final String name;
  final String email;
  final String phone;
  final String province;
  final String district;
  
  User({
    required this.id,
    required this.name,
    required this.email,
    required this.phone,
    required this.province,
    required this.district,
  });
  
  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      name: json['username'] ?? json['name'] ?? '',
      email: json['email'] ?? '',
      phone: json['mobile'] ?? json['phone'] ?? '',
      province: json['province'] ?? '',
      district: json['district'] ?? '',
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'username': name,
      'email': email,
      'mobile': phone,
      'province': province,
      'district': district,
    };
  }
  
  String getInitials() {
    if (name.isEmpty) return 'U';
    final parts = name.trim().split(' ');
    if (parts.length >= 2) {
      return '${parts[0][0]}${parts[1][0]}'.toUpperCase();
    }
    return name[0].toUpperCase();
  }
}
