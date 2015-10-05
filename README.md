HTU21D
======

Read temparature and humidity from an htu21d sensor chip

Properties
----------

Dependencies
------------

Commands
--------
None

Input
-----
Any list of signals.

Output
------
Each signal has a `temperature` and `humidity` attribute added to the input signal.

If the sensors fails to read from either sensors, the new attribute value will be `None`.
