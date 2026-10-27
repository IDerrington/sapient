from sapient.config import RadarConfig, Capability
from sapient_msg.bsi_flex_335_v2_0 import registration_pb2

class RegistrationBuilder:
    def __init__(self, radar_config: RadarConfig):
        self.config = radar_config
    
    def build(self):
        """
        This method builds a registration message for the radar sensor based 
        on the provided configuration.

        Definition for the registration message is based on the protobuf definition in #
        BSI Flex 335 v2.0. The registration message includes the 
        node definition [List[NodeDefinition]], , 
        name            [string], 
        short name      [string],
        ICD version     [string], 
        Capabilities    [List[Capability]]
        Status Definition,
        Mode Definition,
        """

        # Node definition
        node_definition = registration_pb2.Registration.NodeDefinition()
        node_definition.node_type = registration_pb2.Registration.NodeType.NODE_TYPE_RADAR
        node_definition.node_sub_type.extend(self.config.node_sub_types)

        # Status definition
        status_definition = registration_pb2.Registration.StatusDefinition()
        status_definition.status_interval.value = self.config.status_interval_s
        status_definition.status_interval.units = (
            registration_pb2.Registration.TIME_UNITS_SECONDS
        )

        # Build the registration message
        registration_msg = registration_pb2.Registration()
        registration_msg.node_definition.append(node_definition)
        registration_msg.name = self.config.name
        registration_msg.short_name = self.config.short_name
        registration_msg.icd_version = self.config.icd_version
        registration_msg.status_definition.CopyFrom(status_definition)
        
        # Build the Capabilities list based on the radar configuration
        if self.config.max_range_m is not None:
            registration_msg.capabilities.append(
                registration_pb2.Registration.Capability(
                    category = "Radar",
                    type     = "MaxRange",
                    value    = str(self.config.max_range_m),
                    units    = "m",
                )
            )

        return registration_msg


if __name__ == "__main__":

    # Create a protobuf registration message for the radar sensor 
    # using the RegistrationBuilder class
    radar = RadarConfig(
        name           = "Radar",
        short_name     = "Phaser",
        max_range_m    = 200.0,
        node_sub_types = ["FMCW"],
        status_interval_s = 5.0
        )
    

    builder = RegistrationBuilder(radar)
    registration = builder.build()
    print(registration)



