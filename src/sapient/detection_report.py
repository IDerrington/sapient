import logging
from  ulid import ULID

from sapient_msg.bsi_flex_335_v2_0 import detection_report_pb2, location_pb2, range_bearing_pb2

class DetectionReportBuilder():
    """
    Class to build a detection report message as per BSI Flex 335 v2.0:2024-03, 
    Table 69:  Field values of the “Detection report” field

    """
    def __init__(self) -> None:
        self.log = logging.getLogger(__name__)
        

    def build(self, coordinates: location_pb2.Location | range_bearing_pb2.RangeBearing) -> detection_report_pb2.DetectionReport:
        """
        Build a detection report message.
        :param coordinates: Location or RangeBearing object
        :returns: The constructed DetectionReport message.
        :raises ValueError: If the coordinates type is not Location or RangeBearing.
        """
        
        report = detection_report_pb2.DetectionReport()
        
        report.report_id = (str)(ULID())
        report.object_id =  report.report_id

        # report.task_id = "task_123"
        # report.state = "active"

        if coordinates is not None:
            if isinstance(coordinates, location_pb2.Location):
                location = location_pb2.Location()
                location.x = coordinates.x
                location.y = coordinates.y
                
                location.coordinate_system = coordinates.coordinate_system
                location.datum = coordinates.datum
                
                report.location.CopyFrom(location)

            elif isinstance(coordinates, range_bearing_pb2.RangeBearing):
                location = range_bearing_pb2.RangeBearing()
                location.elevation = coordinates.elevation
                location.azimuth = coordinates.azimuth
                location.range = coordinates.range

                location.coordinate_system = coordinates.coordinate_system
                location.datum = coordinates.datum
                
                report.range_bearing.CopyFrom(location)

            else:
                raise ValueError("Invalid cordinates type. Must be Location or RangeBearing.")

        # report.detection_confidence = 0.9
        #track_object_info = detection_report_pb2.TrackObjectInfo()
        #track_object_info.object_type = detection_report_pb2.TrackObjectInfo.ObjectType.VEHICLE
        #track_object_info.value = "Car"
        #report.track_object_info.CopyFrom(track_object_info)

        self.log.debug(f"Detection report built: {report}")

        return report
    
if __name__ == "__main__":
    # Example usage of the DetectionReport class
    report = DetectionReportBuilder()
    detection_report_message = report.build()
    payload = detection_report_message.SerializeToString()

