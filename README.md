HTU21D
======

Read temperature and humidity from an htu21d sensor chip.

Properties
----------
* **Platform**

Dependencies
------------
None

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
