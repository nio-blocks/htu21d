HTU21D
======

Read temparature and humidity from an htu21d sensor chip

Properties
----------
- **address**: I2C Address
- **platform**: Development platform

Inputs
------

Any list of signals.

Outputs
-------

Each signal has a `temperature` and `humidity` attribute added to the input signal.
If the sensors fails to read from either sensors, the new attribute value will be `None`.

Commands
--------

Dependencies
------------
None
