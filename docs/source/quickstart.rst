Quickstart
==========

Set up the checkout
-------------------

Run these commands from the repository root with Python 3.12 or newer in your
active virtual environment. The submodule supplies the Protobuf schemas.

.. code-block:: bash

   git submodule update --init --recursive
   python -m pip install -e .
   python -m grpc_tools.protoc -I. --python_out=. sapient_msg/proto_options.proto sapient_msg/bsi_flex_335_v2_0/*.proto

Run the radar example
---------------------

Start the SAPIENT Test Harness with its sensor endpoint listening on
``localhost:14000``. Open ``src/examples/run_radar_client.py`` to see the radar
configuration. The example uses a fixed demonstration location, a five-second
status interval, and simulated range/bearing detections. Replace the position
with the radar's surveyed coordinates when testing a real installation.

.. code-block:: bash

   python -m src.examples.run_radar_client

In the harness, look for an accepted ``RegistrationAck`` followed by the
initial ``StatusReport`` with ``INFO_NEW``. During the run, expect
``DetectionReport`` messages interleaved with status reports marked
``INFO_UNCHANGED``. Verify that status reports continue after the simulated
detections stop.

If registration fails, check the startup log for the acknowledgement reason
or transport exception. The current client uses ``localhost:14000`` and a
five-second socket timeout internally.

Build this documentation
------------------------

With the generated Protobuf modules available, install the documentation
extra and build the HTML from the repository root.

.. code-block:: bash

   python -m pip install -e ".[docs]"
   python -m sphinx -M html docs/source docs/build

Open ``docs/build/html/index.html`` to preview the site.
