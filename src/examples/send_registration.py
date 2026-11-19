import logging
from uuid import uuid4

from sapient import transport
from sapient.config import RadarConfig, Location
from sapient.message import Message
from sapient.status_report import StatusReport
from sapient.registration import RegistrationBuilder
from sapient.transport import TCPTransport
from sapient_msg.bsi_flex_335_v2_0 import sapient_message_pb2

def main() -> None:
    # Create radar configuration and node_id.
    # Build the registration and SapientMessage envelope.
    # Connect, send, and close using try/finally.

    # Ideally we get the location from GPS or some other source, 
    # but for this example we will hardcode it.
    location = Location(latitude=37.7749, longitude=-122.4194, altitude=10.0)
    
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
        location=location
    )

    node_id = str(uuid4())
    
    # Build registration message for the radar sensor
    builder = RegistrationBuilder(radar)
    registration = builder.build()

    # Create a SAPIENT message with the registration payload
    message = Message(node_id=node_id, 
                      payload=registration)
    
    message = message.build()

    payload = message.SerializeToString()

    transport = TCPTransport(host="localhost", port=14000, timeout=5.0)
    try:
        transport.connect()
        transport.send(payload)
        rx_payload = transport.receive()
    except Exception as e:
        logging.error("Error during transport: %s", e)
        transport.close()
        

    # create a sapient message to hold received payload
    rx_message = sapient_message_pb2.SapientMessage()

    # parse the received payload into the sapient message
    rx_message.ParseFromString(rx_payload)
    
    # we're expecting the content of the received message to be a 
    # registration response

    reply_type = rx_message.WhichOneof("content")

    if reply_type == "registration_ack":
        ack = rx_message.registration_ack
        if ack.acceptance:
            logging.info("Registration accepted")
        else:
            logging.warning("Registration rejected: %s",
                        ", ".join(ack.ack_response_reason))
            exit(1)
    elif reply_type == "error":
        logging.error("Registration error: %s",
                  ", ".join(rx_message.error.error_message))
        exit(1) 
    else:
        logging.warning("Unexpected registration reply: %s", reply_type)
        exit(1)

    logging.info("Received message: %s", rx_message)

    # Create a status report message for the radar sensor
    status = StatusReport()
    status_report = status.build(mode=registration.mode_definition[0].mode_name)
    
    # Create a SAPIENT message with the status report payload
    message = Message(node_id=node_id, 
                      payload=status_report)
    
    message = message.build()
    payload = message.SerializeToString()

    try:
        transport.send(payload)
    except Exception as e:
        logging.error("Error during transport: %s", e)
        transport.close()
    finally:
        transport.close()
    

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logging.info("Starting registration example")
    main()
    logging.info("Finished registration example")