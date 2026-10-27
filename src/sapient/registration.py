from sapient.config import RadarConfig
from sapient_msg.bsi_flex_335_v2_0 import registration_pb2

class RegistrationBuilder:
    def __init__(self, radar_config: RadarConfig):
        self.config = radar_config
    
    def build(self):
        """
        This method builds a registration message for the radar sensor based 
        on the provided configuration.
        """
        registration = registration_pb2.Registration(
            node_definition=[
                registration_pb2.Registration.NodeDefinition(
                    node_type=registration_pb2.Registration.NodeType.NODE_TYPE_RADAR
                )
            ],
            name = self.config.name,
            short_name = self.config.short_name,
            icd_version = self.config.icd_version
            )
        


  
        return registration


if __name__ == "__main__":
    radar = RadarConfig(
        name="Radar",
        short_name="Phaser",
        max_range_m=200.0
    )

    builder = RegistrationBuilder(radar)
    registration = builder.build()
    print(registration)

