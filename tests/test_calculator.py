from custom_components.owm_precipitation_forecast.calculator import SnowCalculator

def test_ratios():
    ratios = {
        "ratio_34_plus": 10.0,
        "ratio_28_34": 12.0,
        "ratio_20_28": 15.0,
        "ratio_10_20": 20.0,
        "ratio_0_10": 30.0,
        "ratio_neg": 50.0
    }
    calc = SnowCalculator(ratios)

    # Test 35F (>= 34)
    assert calc.calculate_snow(1, 35) == 10.0
    # Test 30F (28-34)
    assert calc.calculate_snow(1, 30) == 12.0
    # Test 25F (20-28)
    assert calc.calculate_snow(1, 25) == 15.0
    # Test 15F (10-20)
    assert calc.calculate_snow(1, 15) == 20.0
    # Test 5F (0-10)
    assert calc.calculate_snow(1, 5) == 30.0
    # Test -5F (<0)
    assert calc.calculate_snow(1, -5) == 50.0

    # Zero liquid
    assert calc.calculate_snow(0, 25) == 0.0