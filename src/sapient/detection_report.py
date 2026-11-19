import logging
import ulid

from sapient_msg.bsi_flex_335_v2_0 import detection_report_pb2, location_pb2, range_bearing_pb2

class DetectionReport():
    """
    Class to build a detection report message.
    """
    def __init__(self,
                 coordinate_system: range_bearing_pb2.RangeBearing.CoordinateSystem = range_bearing_pb2.RangeBearing.CoordinateSystem.CARTESIAN,
                 datum: range_bearing_pb2.RangeBearing.Datum = range_bearing_pb2.RangeBearing.Datum.WGS84) -> None:
        self.log = logging.getLogger(__name__)
        
        self.coordinate_system = coordinate_system
        self.datum = datum

    def build(self, cordinates: location_pb2.Location | range_bearing_pb2.RangeBearing) -> detection_report_pb2.DetectionReport:
        """
        Build a detection report message.
        """
        
        self.log.info("Building detection report message")
        
        report = detection_report_pb2.DetectionReport()
        
        report.report_id = (str)(ulid.new())
        report.object_id =  report.report_id

        # report.task_id = "task_123"
        # report.state = "active"

        if cordinates is not None:
            if isinstance(cordinates, location_pb2.Location):
                location = location_pb2.Location()
                location.x = cordinates.x
                location.y = cordinates.y
                
                location.coordinate_system = self.coordinate_system
                location.datum = self.datum
                
                report.location.CopyFrom(location)

            elif isinstance(cordinates, range_bearing_pb2.RangeBearing):
                location = range_bearing_pb2.RangeBearing()
                location.elevation = 2
                location.azimuth = 3
                location.range = 4

                location.coordinate_system = self.coordinate_system
                location.datum = self.datum
                
                report.range_bearing.CopyFrom(location)

            else:
                raise ValueError("Invalid cordinates type. Must be Location or RangeBearing.")

        # report.detection_confidence = 0.9
        #track_object_info = detection_report_pb2.TrackObjectInfo()
        #track_object_info.object_type = detection_report_pb2.TrackObjectInfo.ObjectType.VEHICLE
        #track_object_info.value = "Car"
        #report.track_object_info.CopyFrom(track_object_info)    

        return report
    
if __name__ == "__main__":
    # Example usage of the DetectionReport class
    report = DetectionReport()
    detection_report_message = report.build()
    payload = detection_report_message.SerializeToString()

