from dataclasses import field, dataclass

@dataclass
class Capability:
    category: str
    type: str
    value: str
    units: str

@dataclass
class SensorConfig:
    name: str
    short_name: str
    icd_version: str = "2.0"
    node_sub_types: list[str] = field(default_factory=list)
    capabilities: list[Capability] = field(default_factory=list)
    status_interval_s: float = 5.0
    
@dataclass
class RadarConfig(SensorConfig):
    max_range_m: float | None = None
    



radar = RadarConfig(
    name = "Radar",
    short_name = "Phaser",
    max_range_m = 200.0,
    node_sub_types =["FMCW"]
)