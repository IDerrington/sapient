Implementation
==============

Session lifecycle
-----------------

``SapientClient.start()`` connects and sends the registration built from
``RadarConfig``. The client checks that the reply is addressed to its node ID,
requires an accepted ``RegistrationAck``, and saves the acknowledgement sender
as the destination for later messages. Connection and registration failures
are raised to the caller after the transport is closed.

After registration, the client creates a status payload, sends the initial
report, and starts a worker. The worker uses a monotonic deadline based on
``status_interval_s`` and waits on the work queue only until the next heartbeat
is due. It serializes heartbeat and detection writes on the same connection.

The current send handlers log transport failures. ``stop()`` queues a stop
request for the worker. Joining the worker, closing the transport at shutdown,
and reconnecting after a link failure are outstanding lifecycle work.

Message construction
--------------------

* ``RegistrationBuilder`` builds the radar registration, including its
  identity, capabilities, status interval, and default operating mode.
* ``StatusReportBuilder`` initializes the status payload from the operating
  mode and configured position. The client reuses that payload and assigns a
  new report ULID before each send. The position is expressed in decimal
  degrees with longitude in ``x``, latitude in ``y``, and altitude in metres
  above the WGS84 ellipsoid in ``z``.
* ``DetectionReportBuilder`` selects the location or range/bearing branch in the
  detection payload. The client uses metres and degrees, with azimuth
  referenced to true north. It generates a fresh ULID for each detection and
  uses that value for both ``report_id`` and ``object_id``. Successive
  detections are reported independently.
* ``SapientMessageBuilder`` creates an envelope with the sender node ID,
  destination ID, and UTC timestamp. It uses the Protobuf schema to pick the
  appropriate field in the ``content`` oneof.
* ``TCPTransport`` frames the serialized envelope with a four-byte
  little-endian payload length and reads incoming frames using the same
  format.

Detection submission
--------------------

The worker currently expects a ``SapientQueItem`` containing a
``DetectionPayload`` with message type ``DETECTION``. The radar example shows
this call shape. Create a new item for each measurement so a queued item
retains its values until the worker sends it. The current envelope timestamp
is set when the worker builds the message. Carrying the sensor capture time
through the queue remains to be implemented.
