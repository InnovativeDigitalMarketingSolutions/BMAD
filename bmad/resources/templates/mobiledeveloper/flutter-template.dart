import 'package:flutter/material.dart';

class MobileComponent extends StatefulWidget {
  final String title;
  final VoidCallback? onPressed;
  final bool disabled;

  const MobileComponent({
    Key? key,
    this.title = 'Mobile Component',
    this.onPressed,
    this.disabled = false,
  }) : super(key: key);

  @override
  State<MobileComponent> createState() => _MobileComponentState();
}

class _MobileComponentState extends State<MobileComponent> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: Center(
          child: Padding(
            padding: const EdgeInsets.all(20.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  widget.title,
                  style: const TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: Colors.black87,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 30),
                ElevatedButton(
                  onPressed: widget.disabled ? null : widget.onPressed,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: widget.disabled ? Colors.grey : Colors.blue,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(
                      horizontal: 30,
                      vertical: 15,
                    ),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10),
                    ),
                    minimumSize: const Size(120, 50),
                  ),
                  child: Text(
                    widget.disabled ? 'Disabled' : 'Press Me',
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Mobile Component Demo',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
      ),
      home: const MobileComponent(),
    );
  }
} 