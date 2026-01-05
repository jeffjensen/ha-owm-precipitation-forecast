"""Snow accumulation calculator based on temperature ratios."""

class SnowCalculator:
    """Calculates snow accumulation based on liquid equivalent and temperature."""

    def __init__(self, ratios: dict):
        """Initialize with a dictionary of temperature thresholds to ratios."""
        self.ratios = ratios

    def get_ratio(self, temp_f: float) -> float:
        """Determine the liquid-to-snow ratio based on temperature in Fahrenheit."""
        if temp_f >= 34:
            return self.ratios.get("ratio_34_plus", 10.0)
        elif 28 <= temp_f < 34:
            return self.ratios.get("ratio_28_34", 12.0)
        elif 20 <= temp_f < 28:
            return self.ratios.get("ratio_20_28", 15.0)
        elif 10 <= temp_f < 20:
            return self.ratios.get("ratio_10_20", 20.0)
        elif 0 <= temp_f < 10:
            return self.ratios.get("ratio_0_10", 30.0)
        else:
            return self.ratios.get("ratio_neg", 50.0)

    def calculate_snow(self, liquid_in: float, temp_f: float) -> float:
        """Calculate snow inches from liquid inches and temp."""
        if liquid_in <= 0:
            return 0.0
        ratio = self.get_ratio(temp_f)
        return liquid_in * ratio