from dataclasses import dataclass, field
from enum import Enum, auto
import logging
import queue
import threading

import time
from uuid import uuid4

from sapient import config
from sapient import message
from sapient import transport
from sapient import registration
from sapient import status_report

from sapient.config import RadarConfig, SensorConfig
from sapient.detection_report import DetectionReport
from sapient.message import Message
from sapient.registration import RegistrationBuilder
from sapient.status_report import StatusReport
from sapient.transport import TCPTransport

from sapient_msg.bsi_flex_335_v2_0 import range_bearing_pb2, registration_pb2, sapient_message_pb2

class SapientMessageType(Enum):
    DETECTION = auto()
    ALERT = auto()
    TASK = auto()
    STATUS = auto()
    REGISTRATION = auto()
    STOP = auto()


@dataclass
class DetectionPayload:
    target_id: int
    range_m: float
    velocity_mps: float


@dataclass
class AlertPayload:
    severity: int
    description: str


@dataclass
class SapientQueItem:
    """
    A class to represent an item in the SAPIENT work queue.
    
    Attributes:
        detection: The detection data to be sent.
        timestamp: The timestamp of the detection.
    """
    message: SapientMessageType
    payload: DetectionPayload | AlertPayload | None = None


class SapientClient():
    """
    A class to represent a SAPIENT client that can send messages to a SAPIENT server.
    """
    def __init__(self):
        self.log = logging.getLogger(__name__)
        
        self.host = None
        self.port = None
        self.timeout = None
        self.node_id = str(uuid4())

        self.work_queue = queue.Queue()

    def start(self, config: SensorConfig, 
              host: str = "localhost", 
              port: int = 14000,
              timeout: float = 5.0
              ):
        """
        Start the SAPIENT client with the given configuration.
        
        args:
            config: SensorConfig object containing the sensor configuration.
            host: Hostname or IP address of the SAPIENT server.
            port: Port number of the SAPIENT server.
            timeout: Timeout for the TCP connection in seconds.

        returns:
            None
        """

        self.host = host
        self.port = port
        self.timeout = timeout

        self.log.info("Starting SAPIENT client...")
        
        self._send_registration(config)
        self._send_status_report(config)

        self.log.info("Starting work queue thread...")
        
        self.worker_thread = threading.Thread(target=self._run)
        self.worker_thread.start()

        self.log.info("SAPIENT client started successfully.")
        
    def stop(self):
        """
        Stop the SAPIENT client.
        """
        self.log.info("Stopping SAPIENT client...")
        self.work_queue.put(SapientQueItem(message=SapientMessageType.STOP))
        
    def send_detection(self, detection: DetectionPayload):
        """
        Send a detection message to the SAPIENT server.
        """

        self.log.debug("Sending detection: %s", detection)
        self.work_queue.put(detection)

    def _send_registration(self, config: SensorConfig):
        """
        Send a registration message to the SAPIENT server.
        
        args:
            config: SensorConfig object containing the sensor configuration.

        returns:
            None
        """
        self.log.info("Sending registration message...")
        
        # Build registration message for the radar sensor
        builder = RegistrationBuilder(config)
        self.registration = builder.build()

        # Create a SAPIENT message with the registration payload
        message = Message(node_id=self.node_id, 
                          payload=self.registration)
    
        message = message.build()
        payload = message.SerializeToString()

        # Create a TCP transport and send the registration message
        self.transport = TCPTransport(host="localhost", port=14000, timeout=5.0)
        
        try:
            self.transport.connect()
            self.transport.send(payload)
            rx_payload = self.transport.receive()

        except Exception as e:
            self.log.error("Error during transport: %s", e)


        # create a sapient message to hold received payload
        rx_message = sapient_message_pb2.SapientMessage()

        # parse the received payload into the sapient message
        rx_message.ParseFromString(rx_payload)

        self.log.debug("Received message: %s", rx_message)
    
        # we're expecting the content of the received message to be a 
        # registration response

        reply_type = rx_message.WhichOneof("content")

        if reply_type == "registration_ack":
            ack = rx_message.registration_ack
            
            if ack.acceptance:
                self.log.info("Registration accepted")
            else:
                self.log.warning("Registration rejected: %s",
                        ", ".join(ack.ack_response_reason))
                
        elif reply_type == "error":
            self.log.error("Registration error: %s",
                  ", ".join(rx_message.error.error_message))
            
        else:
            self.log.warning("Unexpected registration reply: %s", reply_type)

    def _send_status_report(self, config: SensorConfig):
        """
        Send a status report message to the SAPIENT server.
        
        args:
            config: SensorConfig object containing the sensor configuration.

        returns:
            None
        """
        self.log.info("Sending status report message...")

        # Create a status report message for the radar sensor
        status = StatusReport()
        status_report = status.build(mode=self.registration.mode_definition[0].mode_name)
    
        # Create a SAPIENT message with the status report payload
        message = Message(node_id=self.node_id, 
                          payload=status_report)
    
        message = message.build()
        payload = message.SerializeToString()

        try:
            self.transport.send(payload)
        except Exception as e:
            self.log.error("Error during transport: %s", e)

    def _send_detection(self, detection: DetectionPayload):
        """
        Send a detection message to the SAPIENT server.
        
        args:
            detection: DetectionPayload object containing the detection data.

        returns:
            None
        """
        self.log.info("Building detection message...")

        detetion_msg = DetectionReport( coordinate_system=range_bearing_pb2.RangeBearing.CoordinateSystem.SPHERICAL,
                                        datum=range_bearing_pb2.RangeBearing.Datum.WGS84)
        
        detection_payload = detetion_msg.build(cordinates = range_bearing_pb2.RangeBearing(
                                                    elevation = detection.velocity_mps,
                                                    azimuth = 0.0,
                                                    range = detection.range_m,
                                            ))
        
        # Create a SAPIENT message with the detection payload
        message = Message(node_id=self.node_id, 
                          payload=detection_payload)
    
        message = message.build()
        payload = message.SerializeToString()

        try:
            self.transport.send(payload)
        except Exception as e:
            self.log.error("Error during transport: %s", e)

    def _run(self):
        """
        Run the SAPIENT client work queue.
        This method processes items in the work queue and sends them to the SAPIENT server.
        """

        while True:
            try:
                item = self.work_queue.get(timeout=self.timeout)
                
                match item.message:
                    case SapientMessageType.DETECTION:
                        self.log.debug("Processing detection: %s", item.payload)
                        self._send_detection(item.payload)

                    case SapientMessageType.ALERT:
                        self.log.debug("Processing alert: %s", item.payload)

                    case SapientMessageType.STATUS:
                        self.log.debug("Processing status: %s", item.payload)

                    case SapientMessageType.REGISTRATION:
                        self.log.debug("Processing registration: %s", item.payload) 

                    case SapientMessageType.STOP:
                        self.log.info("Stopping SAPIENT client...")
                        self.work_queue.task_done()
                        break       

                self.work_queue.task_done()

            except queue.Empty:
                self.log.info("Work queue timed out, calling on_timeout()`")
                
def main() -> None:
    # Create radar configuration and node_id.
    # Build the registration and SapientMessage envelope.
    # Connect, send, and close using try/finally.
    
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

    sapient = SapientClient()
    sapient.start(config=radar, 
                  host="localhost", 
                  port=14000, 
                  timeout=5.0)
    

    detection = SapientQueItem(message=SapientMessageType.DETECTION, 
                               payload =DetectionPayload(target_id=1, 
                                                         range_m=100.0, 
                                                         velocity_mps=10.0)   )
   
    for i in range(5):
        sapient.send_detection(detection)
        time.sleep(1.0)

    sapient.stop()

    

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logging.info("Starting registration example")
    main()
    logging.info("Finished registration example")