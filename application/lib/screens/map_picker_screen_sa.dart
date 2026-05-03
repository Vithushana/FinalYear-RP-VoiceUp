import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

import 'dart:convert'; // json.decode-kaga
import 'package:http/http.dart' as http; // API calls-kaga

class MapPickerScreenSA extends StatefulWidget {
  const MapPickerScreenSA({
    super.key,
    required this.initialLat,
    required this.initialLng,
  });

  final double initialLat;
  final double initialLng;

  @override
  State<MapPickerScreenSA> createState() => _MapPickerScreenSAState();
}

class _MapPickerScreenSAState extends State<MapPickerScreenSA> {
  late LatLng picked;

  final MapController _mapController = MapController();

  @override
  void initState() {
    super.initState();
    picked = LatLng(widget.initialLat, widget.initialLng);
  }

  // Search location using Nominatim API
  Future<void> _searchAndMove(String address) async {
    try {
      final encodedAddress = Uri.encodeQueryComponent(address);

      // Nominatim API URL
      final url = Uri.parse(
        'https://nominatim.openstreetmap.org/search?q=$encodedAddress&format=json&limit=1',
      );
      final response = await http.get(url);

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data.isNotEmpty) {
          double lat = double.parse(data[0]['lat']);
          double lon = double.parse(data[0]['lon']);
          
          if (!mounted) return;
          
          setState(() {
            picked = LatLng(lat, lon); // Update picked location
          });
          
          // Move map to searched location 
          _mapController.move(picked, 15); 
        }
      }
    } catch (e) {
      print("Location not found: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Select location")),
      body: Stack(

        children: [
          FlutterMap(
            mapController: _mapController, // Assign controller 
            options: MapOptions(
              initialCenter: picked,
              initialZoom: 15,
              onTap: (_, point) => setState(() => picked = point),
            ),
            children: [
              TileLayer(
                urlTemplate: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                userAgentPackageName: "sarma_application",
              ),
              MarkerLayer(
                markers: [
                  Marker(
                    point: picked,
                    width: 50,
                    height: 50,
                    child: const Icon(Icons.location_pin,
                        size: 46, color: Colors.red),
                  ),
                ],
              ),
            ],
          ),

          /* 
           ==================== Search bar ==============================
          */
          Positioned(
            top: 15,
            left: 15,
            right: 15,
            child: Container(
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(10),
                boxShadow: const [BoxShadow(color: Colors.black26, blurRadius: 10)],
              ),
              child: TextField(
                decoration: const InputDecoration(
                  hintText: "Search for a location...",
                  prefixIcon: Icon(Icons.search),
                  border: InputBorder.none,
                  contentPadding: EdgeInsets.symmetric(vertical: 15),
                ),
                onSubmitted: (value) {
                  // Implement search functionality here
                  _searchAndMove(value); 
                },
              ),
            ),
          ),

          Positioned(
            left: 12,
            right: 12,
            bottom: 12,
            child: ElevatedButton(
              onPressed: () => Navigator.pop(context, picked),
              child: const Text("Confirm Location"),
            ),
          ),
        ],
      ),
    );
  }
}
