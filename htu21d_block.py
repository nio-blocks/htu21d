from time import sleep
from nio.common.signal.base import Signal
from nio.common.discovery import Discoverable, DiscoverableType
from nio.metadata.properties import VersionProperty
from .i2c_base.i2c_base import I2CBase


@Discoverable(DiscoverableType.block)
class HTU21D(I2CBase):

    """ Read temparature and humidity from an htu21d sensor chip """

    version = VersionProperty('0.1.0')

    def process_signals(self, signals, input_id='default'):
        signals_to_notify = []
        for signal in signals:
            signals_to_notify.append(self._read_htu(signal))
        self.notify_signals(signals_to_notify, output_id='default')

    def _read_htu(self, signal):
        temperature = self._read_temperature()
        self._logger.debug("Temperature: {}".format(temperature))
        humidity = self._read_humidity()
        self._logger.debug("Humidity: {}".format(humidity))
        return self.get_output_signal({"temperature": temperature,
                                       "humidity": humidity},
                                      signal)

    def get_output_signal(self, value, signal):
        #TODO: move to mixin
        return Signal(value)

    def _read_temperature(self):
        self._i2c.write_list(0xE3, [])
        sleep(0.05)
        response = self._i2c.read_bytes(3)
        if not self._crc8check(response):
            return
        temphigh = response[0]
        templow = response[1]
        crc = response[2]
        _STATUS_LSBMASK = 0b11111100
        temp = (temphigh << 8) | (templow & _STATUS_LSBMASK)
        temperature = -46.85 + (175.72 * temp) / 2**16
        return temperature

    def _read_humidity(self):
        self._i2c.write_list(0xE5, [])
        sleep(0.05)
        response = self._i2c.read_bytes(3)
        if not self._crc8check(response):
            return
        humidhigh = response[0]
        humidlow = response[1]
        crc = response[2]
        _STATUS_LSBMASK = 0b11111100
        humid = (humidhigh << 8) | (humidlow & _STATUS_LSBMASK)
        humidity = -6 + (125.0 * humid) / 2**16
        return humidity

    def _crc8check(self, value):
        """Calulate the CRC8 for the data received"""
        try:
            # Ported from Sparkfun Arduino HTU21D Library: https://github.com/sparkfun/HTU21D_Breakout
            remainder = ( ( value[0] << 8 ) + value[1] ) << 8
            remainder |= value[2]
        except:
            self._logger.warning(
                "Temp/Humidy read bytes response is invalid: {}".format(value))
            return False
        # POLYNOMIAL = 0x0131 = x^8 + x^5 + x^4 + 1
        # divsor = 0x988000 is the 0x0131 polynomial shifted to farthest left of three bytes
        divsor = 0x988000
        for i in range(0, 16):
            if( remainder & 1 << (23 - i) ):
                remainder ^= divsor
            divsor = divsor >> 1
        if remainder == 0:
            return True
        else:
            self._logger.warning("Failed crc8 check: {}".format(value))
            return False
