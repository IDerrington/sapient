from dataclasses import field, dataclass



@dataclass
class Duration:
    units: int
    value: float

@dataclass
class Capability:
    category: str
    type: str
    value: str
    units: str


@dataclass
class Mode:
    name: str
    type: int
    description: str
    duration: Duration = field(default_factory=Duration)
    

@dataclass
class SensorConfig:
    """Configuration shared by SAPIENT sensor nodes.

    Attributes:
        name: Human-readable system name.
        short_name: Abbreviated name suitable for display.
        icd_version: SAPIENT interface specification version.
        node_sub_types: Further descriptions of the sensor type.
        capabilities: Capabilities advertised during registration.
        status_interval_s: Time between heartbeat reports, in seconds.
        mode_settle_time_s: Time to wait for the sensor to settle after a mode change, in seconds.
    """
    name: str
    model: str
    short_name: str
    hw_version: str
    sw_version: str
    serial_number: str
    icd_version: str = "2.0"
    node_sub_types: list[str] = field(default_factory=list)
    capabilities: list[Capability] = field(default_factory=list)
    status_interval_s: float = 5.0
    mode_settle_time_s: float = 0.0


    
@dataclass
class RadarConfig(SensorConfig):
    max_range_m: str = "200.0"
    min_range_m: str = "0.5"    
    

if __name__ == "__main__":
    # Create a radar configuration object

    radar = RadarConfig(
        name = "Radar",
        model = "CN0566",
        short_name = "Phaser",
        serial_number= "123456789",
        hw_version = "C",
        sw_version = "1.0.0",
        max_range_m = "200.0",
        min_range_m = "0.5",
        node_sub_types =["FMCW"],
    )
