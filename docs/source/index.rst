SAPIENT Sensor
==============

SAPIENT Sensor is a Python radar edge-node implementation using the BSI Flex
335 v2.0 Protobuf messages. It registers with a SAPIENT endpoint, sends an
initial status report, and publishes periodic status and radar detections over
the same TCP connection.

Start with the radar example to see these messages in the SAPIENT Test Harness.
Use the implementation guide to understand how the client, builders, and
transport fit together.

.. toctree::
   :maxdepth: 2
   :caption: Contents

   quickstart
   implementation
   api
