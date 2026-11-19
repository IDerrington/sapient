from dataclasses import field
import logging

from sapient_msg.bsi_flex_335_v2_0 import registration_pb2, sapient_message_pb2
from google.protobuf.message import Message as ProtobufMessage

class Message():
    def __init__(self, 
                 node_id: str,
                 payload: ProtobufMessage,
                 destination_id: str = "00000000-0000-0000-0000-000000000000"):
       
       self.log = logging.getLogger(__name__)

       self.node_id = node_id
       self.destination_id = destination_id
       self.payload = payload

    def build(self):
        message = sapient_message_pb2.SapientMessage()

        message.timestamp.GetCurrentTime()
        message.node_id = self.node_id
       
        message.destination_id = self.destination_id

        for field in message.DESCRIPTOR.oneofs_by_name["content"].fields:
            if field.message_type == self.payload.DESCRIPTOR:
                getattr(message, field.name).CopyFrom(self.payload)
                break
        else:
            raise TypeError(f"Unsupported SAPIENT payload: {type(self.payload).__name__}")

        self.log.debug("SapientMessage built: %s", message)
       
        return message


if __name__ == "__main__":
    from sapient.registration import RegistrationBuilder
    from sapient.config import RadarConfig
    from uuid import uuid4


    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

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
    node_id = str(uuid4())
    
    # Build registration message for the radar sensor
    builder = RegistrationBuilder(radar)
    registration = builder.build()

    # Create a SAPIENT message with the registration payload
    message = Message(node_id=node_id, 
                      payload=registration)
    
    message = message.build()

    payload = message.SerializeToString()
    restored = sapient_message_pb2.SapientMessage.FromString(payload)
    assert restored == message

    from google.protobuf.json_format import MessageToJson
    print(MessageToJson(restored))