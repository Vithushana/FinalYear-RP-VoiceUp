import 'dart:js' as js;
import 'dart:async';

class LocationHelperWeb {
  // Default location coordinates for Sri Lanka region
  static const double _defaultLatitude = 6.9147;
  static const double _defaultLongitude = 79.9729;
  static const bool _useDefaultLocation = true;
  
  static void requestLocation(
    Function(double lat, double lng) onSuccess,
    Function(String error) onError,
  ) {
    try {
      // Access navigator.geolocation via JS interop
      final navigator = js.context['navigator'];
      final geolocation = navigator['geolocation'];
      
      if (geolocation == null) {
        onError('Geolocation is not supported by this browser');
        return;
      }
      
      // Define success callback
      final successCallback = js.allowInterop((position) {
        try {
          Future.delayed(const Duration(milliseconds: 800), () {
            if (_useDefaultLocation) {
              // Use default location for web platform
              onSuccess(_defaultLatitude, _defaultLongitude);
            } else {
              // Use actual browser location
              final coords = position['coords'];
              final lat = coords['latitude'] as num;
              final lng = coords['longitude'] as num;
              
              onSuccess(lat.toDouble(), lng.toDouble());
            }
          });
        } catch (e) {
          onError('Error parsing location data');
        }
      });
      
      // Define error callback
      final errorCallback = js.allowInterop((error) {
        try {
          if (_useDefaultLocation) {
            // Fallback to default location
            Future.delayed(const Duration(milliseconds: 800), () {
              onSuccess(_defaultLatitude, _defaultLongitude);
            });
          } else {
            final code = error['code'] as int;
            String errorMsg = 'Location access denied';
            
            if (code == 1) {
              errorMsg = 'Location permission denied. Click "Allow" in browser prompt.';
            } else if (code == 2) {
              errorMsg = 'Location unavailable. Check your internet connection.';
            } else if (code == 3) {
              errorMsg = 'Location request timeout. Please try again.';
            }
            
            onError(errorMsg);
          }
        } catch (e) {
          onError('Location error occurred');
        }
      });
      
      // Request location from browser
      geolocation.callMethod('getCurrentPosition', [successCallback, errorCallback]);
      
    } catch (e) {
      // Fallback to default location on exception
      if (_useDefaultLocation) {
        Future.delayed(const Duration(milliseconds: 800), () {
          onSuccess(_defaultLatitude, _defaultLongitude);
        });
      } else {
        onError('Location error: ${e.toString()}');
      }
    }
  }
}
