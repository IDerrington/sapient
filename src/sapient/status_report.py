
import logging

from sapient_msg.bsi_flex_335_v2_0 import status_report_pb2
from sapient.config import SensorConfig
from ulid import ULID

class StatusReport:
    def __init__(self, 
                 sensor_config:SensorConfig) -> None:
        self.log = logging.getLogger(__name__)
        self.sensor_config = sensor_config


    def build(self, 
              mode: str = "NORMAL") -> status_report_pb2.StatusReport:
        """
        Build a status report message with the given mode.
        Args:
            mode (str): The mode of the status report. Defaults to "NORMAL".
        Returns:
            status_report_pb2.StatusReport: The built status report message.
        """
        status_report = status_report_pb2.StatusReport()
        
        ulid = ULID()
        status_report.report_id = (str)(ulid)
        
        status_report.system = status_report_pb2.StatusReport.System.SYSTEM_OK
        status_report.info = status_report_pb2.StatusReport.Info.INFO_NEW

        # Location of the RADAR sensor node
        location = status_report_pb2.Location()
        location.x = self.sensor_config.location.latitude
        location.y = self.sensor_config.location.longitude
        location.z = self.sensor_config.location.altitude
        location.coordinate_system = status_report_pb2.Location.CoordinateSystem.CARTESIAN
        location.datum = status_report_pb2.Location.Datum.WGS84

        # status_report.active_task_id = "NONE"
        status_report.mode = mode

        self.log.debug("Status report built: %s", status_report)

        return status_report
    
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    status_report = StatusReport()
    status = status_report.build()   

    payload = status.SerializeToString()
    restored = status_report_pb2.StatusReport.FromString(payload)
    assert restored == status

    from google.protobuf.json_format import MessageToJson
    print(MessageToJson(status))
