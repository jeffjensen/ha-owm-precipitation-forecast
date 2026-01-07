class FakeCoordinator:
    last_update_success = True
    last_error = None

def test_health_ok():
    from custom_components.ha_owm_precipitation_forecast.health import OWMPrecipitationHealthSensor
    sensor = OWMPrecipitationHealthSensor(FakeCoordinator())
    assert sensor.native_value == "ok"
