"""
Sapient Client module for sending messages to a SAPIENT server.
This module provides a SapientClient class that can be used to send registration, status, detection
, and alert messages to a SAPIENT server. The client uses a work queue to manage the sending of messages and can be started and stopped as needed.
The SapientClient class is designed to be used in a multi-threaded environment, allowing for
    concurrent message sending and processing. The client also supports a timeout mechanism for the work queue, allowing for graceful handling of situations where the server is unresponsive.

Authors:
    - Iain Derrington

Company:
    - Analog Devices, Inc.

License:
    - This code is licensed under the Apache License, Version 2.0. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the` License for the specific language governing permissions and limitations under the License.       

"""
from dataclasses import dataclass, field
from enum import Enum, auto
import logging
import math
import queue
import threading

import time
from uuid import uuid4

from ulid import ULID

from sapient import config


from sapient.config import RadarConfig, SensorConfig
from sapient.detection_report import DetectionReportBuilder
from sapient.message import SapientMessageBuilder
from sapient.registration import RegistrationBuilder
from sapient.status_report import StatusReportBuilder
from sapient.transport import TCPTransport

from sapient_msg.bsi_flex_335_v2_0 import range_bearing_pb2, registration_pb2, sapient_message_pb2, status_report_pb2

class SapientMessageType(Enum):
    """
    An enumeration of SAPIENT message types.
    """
    DETECTION = auto()
    ALERT = auto()
    TASK = auto()
    STATUS = auto()
    REGISTRATION = auto()
    STOP = auto()


@dataclass
class DetectionPayload:
    """
    A class to represent a detection payload.
    Attributes:
        target_id (int): The ID of the detected target.
        range_m (float): The range to the detected target in meters.
        azimuth_deg (float): The azimuth angle to the detected target in
                             degrees. Default is 0.0.
        elevation_deg (float): The elevation angle to the detected target
                               in degrees. Default is 0.0.

        Spherical coordinates are used for the detection payload, with the range, azimuth, and elevation angles defining the position of the detected target relative to the sensor.    
    """
    target_id: int
    range_m: float
    azimuth_deg: float = 0.0
    elevation_deg: float = 0.0


@dataclass
class AlertPayload:
    """
    A class to represent an alert payload.
    Attributes:
        severity (int): The severity level of the alert.
        description (str): A description of the alert.
    """ 
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
        self.destination_id = None

        self.work_queue = queue.Queue()

    def start(self, config: SensorConfig, 
              host: str = "localhost", 
              port: int = 14000,
              timeout: float = 5.0
              ):
        """
        Start the SAPIENT client with the given configuration.
        
        :param config: SensorConfig object containing the sensor configuration.
        :param host: Hostname or IP address of the SAPIENT server.
        :param port: Port number of the SAPIENT server.
        :param timeout: Timeout for the TCP connection in seconds.

        :returns: None
        """

        status_interval_s = config.status_interval_s
        
        if not math.isfinite(status_interval_s) or status_interval_s <= 0:
            raise ValueError("Status interval must be finite and positive")

        self.host = host
        self.port = port
        self.timeout = timeout

        self.log.info("Starting SAPIENT client...")

        # Create a TCP transport and send the registration message
        self.transport = TCPTransport(host="localhost", port=14000, timeout=5.0)
        
        try:
            self.transport.connect()
            self._send_registration(config)
        except Exception as e:
            self.log.error("Error during transport: %s", e)
            self.transport.close()
            raise


        # Create a status report
        sts_builder = StatusReportBuilder(config)
        self.status_report = sts_builder.build(mode=self.registration.mode_definition[0].mode_name)
        
        # Send the initial status report to the SAPIENT server
        self._send_status_report(new_info=True)

        self.log.info("Starting work queue thread...")

        self.worker_thread = threading.Thread(
            target=self._run,
            args=(status_interval_s,),
        )
        self.worker_thread.start()

        self.log.info("SAPIENT client started successfully.")
        
    def stop(self):
        """
        Stop the SAPIENT client.
        
        :returns: None

        """
        self.log.info("Stopping SAPIENT client...")
        self.work_queue.put(SapientQueItem(message=SapientMessageType.STOP))
        
    def send_detection(self, detection: DetectionPayload):
        """
        Send a detection message to the SAPIENT server.
        
        :param detection: DetectionPayload object containing the detection data.
        :returns: None
        """

        self.log.debug("Sending detection: %s", detection)
        self.work_queue.put(detection)

    def _send_registration(self, config: SensorConfig):
        """
        Send a registration message to the SAPIENT server.
        
        :param config: SensorConfig object containing the sensor configuration.
        :returns: None
        """
        self.log.info("Sending registration message...")
        
        # Build registration message for the radar sensor
        reg_builder = RegistrationBuilder(config)
        self.registration = reg_builder.build()

        # Create a SAPIENT message with the registration payload
        msg_builder = SapientMessageBuilder(node_id=self.node_id)
        message = msg_builder.build(payload=self.registration)
        payload = message.SerializeToString()

        # Transmit playload to the SAPIENT server using the TCP transport
        self.transport.send(payload)
        rx_payload = self.transport.receive()

        rx_message = sapient_message_pb2.SapientMessage()

        # parse the received payload into the sapient message
        rx_message.ParseFromString(rx_payload)

        self.log.debug("Received message: %s", rx_message)

        # check that the received message is a registration ack and that it 
        # was addressed to this node
        if rx_message.destination_id != self.node_id:
            raise RuntimeError("Registration reply was addressed to another node")

        reply_type = rx_message.WhichOneof("content")

        if reply_type == "error":
            reason = ", ".join(rx_message.error.error_message) or "No details provided"
            raise RuntimeError(f"Registration error: {reason}")

        if reply_type != "registration_ack":
            raise RuntimeError(f"Expected RegistrationAck, got {reply_type}")

        ack = rx_message.registration_ack
        if not ack.acceptance:
            reason = ", ".join(ack.ack_response_reason) or "No reason provided"
            raise RuntimeError(f"Registration rejected: {reason}")

        self.destination_id = rx_message.node_id
        self.log.info("Registration accepted")

    def _send_status_report(self, new_info: bool = False):
        """
        Send a status report message to the SAPIENT server.
        
        :param new_info: Boolean indicating whether the status report contains new information.
        :returns: None
        """
        self.log.info("Sending status report message...")
        
        # Update the status report timestamp and report_id
        
        info = status_report_pb2.StatusReport.Info
        self.status_report.info = info.INFO_NEW if new_info else info.INFO_UNCHANGED
        
        self.status_report.report_id = str(ULID())

        # Create a SAPIENT message with the status report payload
        msg_builder = SapientMessageBuilder(node_id=self.node_id)
        message = msg_builder.build(destination_id=self.destination_id, 
                                    payload=self.status_report)
    
        payload = message.SerializeToString()

        try:
            self.transport.send(payload)
        except Exception as e:
            self.log.error("Error during transport: %s", e)

    def _send_detection(self, detection: DetectionPayload):
        """
        Send a detection message to the SAPIENT server.
        
        :param detection: DetectionPayload object containing the detection data.
        :returns: None
        """

        detection_builder = DetectionReportBuilder()
        detection_payload = detection_builder.build(coordinates = range_bearing_pb2.RangeBearing(
                                                    elevation = detection.elevation_deg,
                                                    azimuth = detection.azimuth_deg,
                                                    range = detection.range_m,
                                                    coordinate_system = range_bearing_pb2.RANGE_BEARING_COORDINATE_SYSTEM_DEGREES_M,
                                                    datum = range_bearing_pb2.RANGE_BEARING_DATUM_TRUE
                                            ))
        
        # Create a SAPIENT message with the detection payload
        msg_builder = SapientMessageBuilder(node_id=self.node_id)
        message = msg_builder.build(destination_id=self.destination_id, 
                                    payload=detection_payload)
        payload = message.SerializeToString()

        self.log.debug("Sending detection message: %s", detection_payload)

        try:
            self.transport.send(payload)
        except Exception as e:
            self.log.error("Error during transport: %s", e)

    def _run(self, status_interval_s: float) -> None:
        """
        Run the SAPIENT client work queue.
        This method processes items in the work queue and sends them to the SAPIENT server.
        
        :param status_interval_s: Interval in seconds between status reports.
        :returns: None
        """
        next_status_at = time.monotonic() + status_interval_s

        while True:
            remaining = next_status_at - time.monotonic()
            
            if remaining <= 0:
                self._send_status_report(new_info=False)
                
                # Skip missed intervals if a socket write delayed the worker.
                elapsed = time.monotonic() - next_status_at
                intervals = int(elapsed // status_interval_s) + 1
                next_status_at += intervals * status_interval_s
                continue

            try:
                item = self.work_queue.get(timeout=remaining)
            except queue.Empty:
                continue

            try:
                match item.message:
                    case SapientMessageType.DETECTION:
                        self.log.info("Sending detection message...")
                        self._send_detection(item.payload)

                    case SapientMessageType.ALERT:
                        self.log.info("Sending detection message...")

                    case SapientMessageType.STATUS:
                        self.log.info("Sending status message...")

                    case SapientMessageType.REGISTRATION:
                        self.log.info("Sending registration message...")

                    case SapientMessageType.STOP:
                        self.log.info("Stopping SAPIENT client...")
                        break
            finally:
                self.work_queue.task_done()

                
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
                                                         velocity_mps=10.0,
                                                        ))

    for i in range(5):
        sapient.send_detection(detection)
        time.sleep(1.0)
        detection.payload.range_m += 10

    time.sleep(10.0)

    sapient.stop()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logging.info("Starting registration example")
    main()
    logging.info("Finished registration example")
