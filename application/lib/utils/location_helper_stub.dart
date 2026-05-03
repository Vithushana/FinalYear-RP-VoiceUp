class LocationHelperWeb {
  static void requestLocation(
    Function(double lat, double lng) onSuccess,
    Function(String error) onError,
  ) {
    onError('Web location not available on this platform');
  }
}
