from collections import defaultdict
from unittest.mock import patch
from nio.block.terminals import DEFAULT_TERMINAL
from nio.signal.base import Signal
from nio.testing.block_test_case import NIOBlockTestCase
from ..htu21d_block import HTU21D
from ..i2c_base.i2c_base import I2CBase, I2CDevice, RaspberryPi_I2CDevice


class TestHTU21D(NIOBlockTestCase):

    @patch(I2CBase.__module__ + ".RaspberryPi_I2CDevice",
           spec=RaspberryPi_I2CDevice)
    def test_defaults(self, mock_i2c):
        blk = HTU21D()
        self.configure_block(blk, {})
        blk._i2c.read_bytes.return_value = bytearray((0x00, 0x00, 0x00))
        blk.start()
        blk.process_signals([Signal()])
        blk.stop()
        self.assert_num_signals_notified(1)
        # The fake read data of b'\x00\x00\x00' ends up being the following
        self.assertDictEqual(self.last_notified[DEFAULT_TERMINAL][0].to_dict(),
                             {"temperature": -46.85,
                              "humidity": -6.0})

    @patch(I2CBase.__module__ + ".RaspberryPi_I2CDevice",
           spec=RaspberryPi_I2CDevice)
    def test_bad_read_bytes(self, mock_i2c):
        """ Test when _i2c.read_bytes fails """
        blk = HTU21D()
        self.configure_block(blk, {})
        blk._i2c.read_bytes.side_effect = Exception()
        blk.start()
        blk.process_signals([Signal()])
        blk.stop()
        self.assert_num_signals_notified(1)
        self.assertDictEqual(self.last_notified[DEFAULT_TERMINAL][0].to_dict(),
                             {"temperature": None,
                              "humidity": None})

    @patch(I2CBase.__module__ + ".RaspberryPi_I2CDevice",
           spec=RaspberryPi_I2CDevice)
    def test_invalid_read_bytes_response(self, mock_i2c):
        """ Test when response returns less that three bytes """
        blk = HTU21D()
        self.configure_block(blk, {})
        # Response should be three bytes so test with only 2
        blk._i2c.read_bytes.return_value = bytearray((0x01, 0x02))
        blk.start()
        blk.process_signals([Signal()])
        blk.stop()
        self.assert_num_signals_notified(1)
        self.assertDictEqual(self.last_notified[DEFAULT_TERMINAL][0].to_dict(),
                             {"temperature": None,
                              "humidity": None})

    @patch(I2CBase.__module__ + ".RaspberryPi_I2CDevice",
           spec=RaspberryPi_I2CDevice)
    def test_crc8_check(self, mock_i2c):
        """ Test when crc8 check fails """
        blk = HTU21D()
        self.configure_block(blk, {})
        blk._i2c.read_bytes.return_value = bytearray((0x01, 0x02, 0x03))
        blk.start()
        blk.process_signals([Signal()])
        blk.stop()
        self.assert_num_signals_notified(1)
        self.assertDictEqual(self.last_notified[DEFAULT_TERMINAL][0].to_dict(),
                             {"temperature": None,
                              "humidity": None})
