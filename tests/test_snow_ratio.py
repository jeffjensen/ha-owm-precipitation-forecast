
from custom_components.ha_owm_precipitation_forecast.snow_ratio import SnowRatioCalculator

def test_ratio_selection():
    calc = SnowRatioCalculator({32.0: 10.0, 20.0: 15.0, 10.0: 20.0})
    assert calc.ratio_for_temp(35) == 10.0
    assert calc.ratio_for_temp(25) == 15.0
    assert calc.ratio_for_temp(5) == 20.0

def test_liquid_to_snow():
    calc = SnowRatioCalculator({32.0: 10.0})
    assert calc.liquid_to_snow_inches(1.0, 30.0) == 10.0
