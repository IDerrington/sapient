from dataclasses import field
import logging

from sapient_msg.bsi_flex_335_v2_0 import registration_pb2, sapient_message_pb2
from google.protobuf.message import Message as ProtobufMessage

class SapientMessageBuilder():
    """
    A class to represent a SAPIENT message.

    Sapient messages are used for communication between nodes in the SAPIENT network. 
    Each message contains a payload, which is a Protobuf message, and metadata such as the node ID and destination ID.

    Based on BSI Flex 335 v2.0:2024-03, table 1.

    :param node_id: UUID of the sender, reused across messages.
    """
    def __init__(self, node_id: str) -> None:
       self.log = logging.getLogger(__name__)
       self.node_id = node_id

    def build(self,
              payload: ProtobufMessage,
              destination_id: str = "00000000-0000-0000-0000-000000000000")-> sapient_message_pb2.SapientMessage:
        """Wrap a payload in a new SAPIENT envelope.

        :param payload: Protobuf message to place in the envelope's content field.
        :returns: The envelope, ready to serialize.
        :raises TypeError: If the envelope does not support the payload type.
        """
        # Create a new SAPIENT message
        message = sapient_message_pb2.SapientMessage()

        # Populate the message fields
        message.timestamp.GetCurrentTime()
        message.node_id = self.node_id
        message.destination_id = destination_id

        for field in message.DESCRIPTOR.oneofs_by_name["content"].fields:
            if field.message_type == payload.DESCRIPTOR:
                getattr(message, field.name).CopyFrom(payload)
                break
        else:
            raise TypeError(f"Unsupported SAPIENT payload: {type(payload).__name__}")

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
    msg_builder  = SapientMessageBuilder(node_id=node_id)
    message = msg_builder.build(payload=registration)
    payload = message.SerializeToString()


    restored = sapient_message_pb2.SapientMessage.FromString(payload)
    assert restored == message

    from google.protobuf.json_format import MessageToJson
    print(MessageToJson(restored))