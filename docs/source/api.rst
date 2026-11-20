API reference
=============

Client and configuration
------------------------

.. autoclass:: sapient.client.SapientClient
   :members: start, stop, send_detection

.. py:class:: sapient.client.DetectionPayload(target_id, range_m, azimuth_deg=0.0, elevation_deg=0.0)

   Holds a detection measurement in metres and degrees. The current client
   does not use ``target_id`` to derive the wire-level ``object_id``.

.. autoclass:: sapient.config.RadarConfig

.. autoclass:: sapient.config.Location

Message builders
----------------

.. autoclass:: sapient.registration.RegistrationBuilder
   :members: build

.. autoclass:: sapient.status_report.StatusReportBuilder

   .. py:method:: build(mode="NORMAL")

      Return a new Protobuf status report. Pass the registered mode name,
      such as ``"Default"``, when building the initial report.

.. autoclass:: sapient.detection_report.DetectionReportBuilder
   :members: build

.. autoclass:: sapient.message.SapientMessageBuilder
   :members: build

Transport
---------

.. autoclass:: sapient.transport.TCPTransport
   :members: connect, close, send, receive
