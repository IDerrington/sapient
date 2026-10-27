from dataclasses import dataclass

@dataclass
class SensorConfig:
    name: str
    short_name: str
    icd_version: str = "2.0"

@dataclass
class RadarConfig(SensorConfig):
    max_range_m: float | None = None

radar = RadarConfig(
    name="Radar",
    short_name="Phaser",
    max_range_m=200.0
)