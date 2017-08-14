from time import sleep

from nio.signal.base import Signal
from nio.util.discovery import discoverable
from nio.properties import VersionProperty

from .i2c_base.i2c_base import I2CBase


@discoverable
class HTU21D(I2CBase):

    """ Read temparature and humidity from an htu21d sensor chip """

    version = VersionProperty('0.1.0')

    def process_signals(self, signals):
        signals_to_notify = []
        for signal in signals:
            signals_to_notify.append(self._read_htu(signal))
        self.notify_signals(signals_to_notify)

    def _read_htu(self, signal):
        temperature = self._read_temperature()
        self.logger.debug("Temperature: {}".format(temperature))
        humidity = self._read_humidity()
        self.logger.debug("Humidity: {}".format(humidity))
        return self.get_output_signal({"temperature": temperature,
                                       "humidity": humidity},
                                      signal)

    def get_output_signal(self, value, signal):
        # TODO: move to mixin
        return Signal(value)

    def _read_temperature(self):
        try:
            high, low, crc = self._read_sensor(0xE3)
        except:
            # Catch _read_sensor exeptions amd whem it returns None
            self.logger.warning("Failed to read temperature", exc_info=True)
            return
        _STATUS_LSBMASK = 0b11111100
        temp = (high << 8) | (low & _STATUS_LSBMASK)
        temperature = -46.85 + (175.72 * temp) / 2**16
        return temperature

    def _read_humidity(self):
        try:
            high, low, crc = self._read_sensor(0xE5)
        except:
            # Catch _read_sensor exeptions amd whem it returns None
            self.logger.warning("Failed to read humidity", exc_info=True)
            return
        _STATUS_LSBMASK = 0b11111100
        humid = (high << 8) | (low & _STATUS_LSBMASK)
        humidity = -6 + (125.0 * humid) / 2**16
        return humidity

    def _read_sensor(self, write_register):
        self._i2c.write_list(write_register, [])
        sleep(0.05)
        response = self._i2c.read_bytes(3)
        if not self._crc8check(response):
            return
        return response[0], response[1], response[2]

    def _crc8check(self, value):
        """Calulate the CRC8 for the data received"""
        try:
            # Ported from Sparkfun Arduino HTU21D Library:
            # https://github.com/sparkfun/HTU21D_Breakout
            remainder = ((value[0] << 8) + value[1]) << 8
            remainder |= value[2]
        except:
            self.logger.warning(
                "Temp/Humidy read bytes response is invalid: {}".format(value))
            return False
        # POLYNOMIAL = 0x0131 = x^8 + x^5 + x^4 + 1
        # divsor = 0x988000 is the 0x0131 polynomial shifted to farthest
        # left of three bytes
        divsor = 0x988000
        for i in range(0, 16):
            if remainder & 1 << (23 - i):
                remainder ^= divsor
            divsor = divsor >> 1
        if remainder == 0:
            return True
        else:
            self.logger.warning("Failed crc8 check: {}".format(value))
            return False
