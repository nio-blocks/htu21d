from collections import defaultdict
from unittest.mock import patch, MagicMock
from nio.common.signal.base import Signal
from nio.util.support.block_test_case import NIOBlockTestCase
from ..htu21d_block import HTU21D 
from ..i2c_base.i2c_base import I2CBase, I2CDevice, FT232H_I2CDevice


class TestHTU21D(NIOBlockTestCase):

    def setUp(self):
        super().setUp()
        # This will keep a list of signals notified for each output
        self.last_notified = defaultdict(list)

    def signals_notified(self, signals, output_id='default'):
        self.last_notified[output_id].extend(signals)

    #@patch(I2CBase.__module__ + ".FT232H_I2CDevice", spec=FT232H_I2CDevice)
    @patch(I2CBase.__module__ + ".I2CDevice", spec=I2CDevice)
    def test_htu21d(self, mock_i2c):
        blk = HTU21D()
        blk.crc8check = MagicMock() # Allow crc check to pass with mocked data
        self.configure_block(blk, {})
        blk._i2c.read_bytes.return_value = bytearray((0x11)) # Some fake read
        blk.start()
        blk.process_signals([Signal()])
        blk.stop()
        self.assert_num_signals_notified(1)
        # The fake read data of 0x11 ends up calculating to the following
        self.assertDictEqual(self.last_notified['default'][0].to_dict(),
                             {"temperature": -46.85,
                              "humidity": -6.0})
