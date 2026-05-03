import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:geolocator/geolocator.dart';
import 'package:geocoding/geocoding.dart';

class LocationPickerDialog extends StatefulWidget {
  final Position? initialPosition;
  
  const LocationPickerDialog({super.key, this.initialPosition});

  @override
  State<LocationPickerDialog> createState() => _LocationPickerDialogState();
}

class _LocationPickerDialogState extends State<LocationPickerDialog> {
  GoogleMapController? _mapController;
  LatLng? _selectedLocation;
  String _selectedAddress = '';

  @override
  void initState() {
    super.initState();
    if (widget.initialPosition != null) {
      _selectedLocation = LatLng(
        widget.initialPosition!.latitude,
        widget.initialPosition!.longitude,
      );
    }
  }

  Future<void> _getAddressFromLatLng(LatLng position) async {
    try {
      final placemarks = await placemarkFromCoordinates(
        position.latitude,
        position.longitude,
      );
      
      if (placemarks.isNotEmpty) {
        final place = placemarks.first;
        setState(() {
          _selectedAddress = '${place.street}, ${place.locality}, ${place.administrativeArea}';
        });
      }
    } catch (e) {
      print('Error getting address: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      child: Container(
        height: 500,
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            Text(
              'Select Location',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 8),
            if (_selectedAddress.isNotEmpty)
              Text(
                _selectedAddress,
                style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                textAlign: TextAlign.center,
              ),
            SizedBox(height: 16),
            Expanded(
              child: GoogleMap(
                initialCameraPosition: CameraPosition(
                  target: _selectedLocation ?? LatLng(6.9271, 79.8612), // Colombo default
                  zoom: 14,
                ),
                onMapCreated: (controller) {
                  _mapController = controller;
                },
                onTap: (position) {
                  setState(() {
                    _selectedLocation = position;
                  });
                  _getAddressFromLatLng(position);
                },
                markers: _selectedLocation != null
                    ? {
                        Marker(
                          markerId: MarkerId('selected'),
                          position: _selectedLocation!,
                        ),
                      }
                    : {},
              ),
            ),
            SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: Text('Cancel'),
                ),
                ElevatedButton(
                  onPressed: _selectedLocation != null
                      ? () {
                          Navigator.pop(context, {
                            'address': _selectedAddress,
                            'lat': _selectedLocation!.latitude,
                            'lng': _selectedLocation!.longitude,
                          });
                        }
                      : null,
                  child: Text('Select'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
