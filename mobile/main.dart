// ATENÇÃO: Este código depende do ambiente Flutter/Dart corretamente instalado.
// Instale o Flutter SDK: https://docs.flutter.dev/get-started/install
// Instale os pacotes necessários com:
//   flutter pub add http
//   flutter pub get
// Execute o app com:
//   flutter run

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() => runApp(AnalyticaApp());

class AnalyticaApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Dashboard(),
    );
  }
}

class Dashboard extends StatefulWidget {
  @override
  _DashboardState createState() => _DashboardState();
}

class _DashboardState extends State<Dashboard> {
  int members = 0;

  @override
  void initState() {
    super.initState();
    loadKPIs();
  }

  loadKPIs() async {
    final res = await http.get(Uri.parse("https://analytica.com.br/api/kpis"));
    final data = json.decode(res.body);
    setState(() => members = data["members"]);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("ANALYTIC.A PRO")),
      body: Center(child: Text("Membros: $members")),
    );
  }
}
