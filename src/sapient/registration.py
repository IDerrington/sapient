
from sapient.config import RadarConfig
from sapient_msg.bsi_flex_335_v2_0 import range_bearing_pb2, registration_pb2

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
        Capabilities    [list[Capability]]
        Status Definition,
        Mode Definition,
        """

        # Node definition
        node_definition_list = self._build_node_definition()
        
        # Caoabilities definition
        capabilities_definition_list = self._build_capabilities_definition()

        # Status definition
        status_definition = self._build_status_definition()

        # Mode definition
        mode_definition_list = self._build_mode_definition()

        # Configuration Data
        config_definition_list = self._build_config_definition()

        # Build the registration message
        registration_msg = registration_pb2.Registration()
        registration_msg.node_definition.extend(node_definition_list)
        registration_msg.name = self.config.name
        registration_msg.short_name = self.config.short_name
        registration_msg.icd_version = self.config.icd_version
        registration_msg.status_definition.CopyFrom(status_definition)
        registration_msg.capabilities.extend(capabilities_definition_list)
        registration_msg.mode_definition.extend(mode_definition_list)
        registration_msg.config_data.extend(config_definition_list)

        return registration_msg
    
    def _build_node_definition(self) -> list[registration_pb2.Registration.NodeDefinition]:
        """
        This method builds the node definition for the radar sensor based on the 
        provided configuration.
        The node definition includes the node type, subtypes, and other relevant 
        information.
        """
        node_list = []

        node_definition = registration_pb2.Registration.NodeDefinition()
        node_definition.node_type = registration_pb2.Registration.NODE_TYPE_RADAR
        node_definition.node_sub_type.extend(self.config.node_sub_types)
    
        node_list.append(node_definition)

        return node_list
    
    def _build_status_definition(self) -> registration_pb2.Registration.StatusDefinition:
        """
        This method builds the status definition for the radar sensor based on 
        the provided configuration.
        
        The status definition includes the status interval and other relevant information.
        """
        status_definition = registration_pb2.Registration.StatusDefinition()
        status_definition.status_interval.value = self.config.status_interval_s
        status_definition.status_interval.units = (
            registration_pb2.Registration.TIME_UNITS_SECONDS
        )
        
        return status_definition
    
    def _build_capabilities_definition(self) -> list[registration_pb2.Registration.Capability]:
        """
        This method builds the capabilities definition for the radar sensor 
        based on the provided configuration.
        The capabilities definition includes the list of capabilities 
        advertised during registration.
        """

        capabilities = []

        capabilities_definition = registration_pb2.Registration.Capability()
        capabilities_definition.category = "Radar"
        capabilities_definition.type = "Max"
        capabilities_definition.value = self.config.max_range_m
        capabilities_definition.units = "m"
        capabilities.append(capabilities_definition)

        capabilities_definition = registration_pb2.Registration.Capability()
        capabilities_definition.category = "Radar"
        capabilities_definition.type = "Min"
        capabilities_definition.value = self.config.min_range_m
        capabilities_definition.units = "m"
        capabilities.append(capabilities_definition)

        return capabilities
    
    def _build_mode_definition(self) -> list[registration_pb2.Registration.ModeDefinition]:
        """
        This method builds the mode definition for the radar sensor based on 
        the provided configuration. 
        The mode definition includes the list of modes supported by the sensor.
        """
        mode_definition = []
        
        # Add a default mode for demonstration purposes
        default_mode = registration_pb2.Registration.ModeDefinition()
        default_mode.mode_name = "Default"
        default_mode.mode_type = registration_pb2.Registration.MODE_TYPE_DEFAULT
        default_mode.mode_description = "Phaser default operating mode"
        default_mode.settle_time.value = self.config.mode_settle_time_s
        default_mode.settle_time.units = registration_pb2.Registration.TIME_UNITS_SECONDS
        default_mode.task.CopyFrom(self._build_task_definition())
   
        mode_definition.append(default_mode)
        
        return mode_definition
    
    def _build_config_definition(self) -> list[registration_pb2.Registration.ConfigurationData]:
        """
        This method builds the configuration data for the radar sensor based on
        the provided configuration.The configuration data includes any additional 
        configuration parameters specific to the sensor.

        @return: List of ConfigurationData messages
        """

        config_definition_list = []

        config_definition = registration_pb2.Registration.ConfigurationData()
        config_definition.manufacturer = "Analog Devices"
        config_definition.model = self.config.model
        config_definition.serial_number = self.config.serial_number
        config_definition.hardware_version = self.config.hw_version
        config_definition.software_version = self.config.sw_version

        config_definition_list.append(config_definition)
    
        return config_definition_list

    def _build_task_definition(self) -> registration_pb2.Registration.TaskDefinition:
        """
        This method builds the task definition for the radar sensor based on 
        the provided configuration. The task definition includes the list of 
        tasks supported by the sensor.
        """
        default_task = registration_pb2.Registration.TaskDefinition()
        default_task.concurrent_tasks = 1
        default_task.region_definition.CopyFrom(self._build_region_definition())
  
        return default_task  

    def _build_region_definition(self) -> registration_pb2.Registration.RegionDefinition:
        """
        This method builds the region definition for the radar sensor based on 
        the provided configuration. The region definition includes the list of 
        regions supported by the sensor.
        """

        region_type = []
        region_type_definition = registration_pb2.Registration.RegionDefinition()
        region_type.append( registration_pb2.Registration.REGION_TYPE_AREA_OF_INTEREST)
        region_type_definition.region_type.extend(region_type)
        

        region_type_definition.region_area.extend( self._build_location_definition() ) 
        
        #location_type_definition = self._build_location_definition()
        #region_type_definition.location_type.extend([location_type_definition]) 
       
        return region_type_definition

    def _build_location_definition(self) -> list[registration_pb2.Registration.LocationType]:
        """
        This method builds the location definition for the radar sensor based on the provided configuration.
        The location definition includes the list of locations supported by the sensor.
        """

        location_type = []

        location_type_definition = registration_pb2.Registration.LocationType()
        
        location_type_definition.range_bearing_units = (
            range_bearing_pb2.RANGE_BEARING_COORDINATE_SYSTEM_DEGREES_M)
        location_type_definition.range_bearing_datum = (
            range_bearing_pb2.RANGE_BEARING_DATUM_TRUE)
        
        location_type.append(location_type_definition)
        
        return location_type

if __name__ == "__main__":
 

    
    # Create a protobuf registration message for the radar sensor
    radar = RadarConfig(
        name = "Radar",
        model = "CN0566",
        short_name= "Phaser",
        serial_number= "123456789",
        hw_version = "C",
        sw_version = "1.0.0",
        status_interval_s = 5.0,
        max_range_m = "200.0",
        min_range_m = "0.5",
    )
        

    builder = RegistrationBuilder(radar)
    registration = builder.build()

    payload = registration.SerializeToString()
    restored = registration_pb2.Registration.FromString(payload)
    assert restored == registration

    from google.protobuf.json_format import MessageToJson
    print(MessageToJson(registration))






