#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: ECE 1896 Voice Detection from NBFM
# Author: adam-nichols
# GNU Radio version: 3.10.11.0

from gnuradio import analog
from gnuradio import audio
from gnuradio import blocks
from gnuradio import digital
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import iio
import fm_rx_epy_block_0_0 as epy_block_0_0  # embedded python block
import threading




class fm_rx(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "ECE 1896 Voice Detection from NBFM", catch_exceptions=True)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables
        ##################################################
        self.thresh = thresh = .5
        self.rf_gain = rf_gain = 40
        self.int_length = int_length = 8000
        self.carrier_freq = carrier_freq = int(sys.argv[1])
        self.audio_samp_rate = audio_samp_rate = 48000
        self.audio_gain = audio_gain = 1
        self.RF_samp_rate = RF_samp_rate = 480000

        ##################################################
        # Blocks
        ##################################################

        self.iio_pluto_source_0 = iio.fmcomms2_source_fc32('ip:192.168.2.1' if 'ip:192.168.2.1' else iio.get_pluto_uri(), [True, True], 32768)
        self.iio_pluto_source_0.set_len_tag_key('packet_len')
        self.iio_pluto_source_0.set_frequency(carrier_freq)
        self.iio_pluto_source_0.set_samplerate(RF_samp_rate)
        self.iio_pluto_source_0.set_gain_mode(0, 'manual')
        self.iio_pluto_source_0.set_gain(0, rf_gain)
        self.iio_pluto_source_0.set_quadrature(True)
        self.iio_pluto_source_0.set_rfdc(True)
        self.iio_pluto_source_0.set_bbdc(True)
        self.iio_pluto_source_0.set_filter_params('Auto', '', 0, 0)
        self.epy_block_0_0 = epy_block_0_0.save_mp3_on_trigger(sample_rate=48000)
        self.digital_costas_loop_cc_0 = digital.costas_loop_cc((2*3.1415/100), 2, False)
        self.digital_binary_slicer_fb_0 = digital.binary_slicer_fb()
        self.blocks_sub_xx_0 = blocks.sub_ff(1)
        self.blocks_repeat_0 = blocks.repeat(gr.sizeof_float*1, (int(int_length*audio_samp_rate/RF_samp_rate)))
        self.blocks_multiply_xx_2 = blocks.multiply_vff(1)
        self.blocks_multiply_xx_1 = blocks.multiply_vcc(1)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.blocks_multiply_const_vxx_1 = blocks.multiply_const_cc(thresh)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_ff(audio_gain)
        self.blocks_integrate_xx_0_0 = blocks.integrate_cc(int_length, 1)
        self.blocks_integrate_xx_0 = blocks.integrate_cc(int_length, 1)
        self.blocks_delay_0 = blocks.delay(gr.sizeof_gr_complex*1, 1)
        self.blocks_conjugate_cc_0_0 = blocks.conjugate_cc()
        self.blocks_conjugate_cc_0 = blocks.conjugate_cc()
        self.blocks_complex_to_mag_0_0 = blocks.complex_to_mag(1)
        self.blocks_complex_to_mag_0 = blocks.complex_to_mag(1)
        self.blocks_char_to_float_0 = blocks.char_to_float(1, 1)
        self.audio_sink_0_0 = audio.sink(audio_samp_rate, '', True)
        self.analog_nbfm_rx_0 = analog.nbfm_rx(
        	audio_rate=audio_samp_rate,
        	quad_rate=RF_samp_rate,
        	tau=(75e-6),
        	max_dev=5e3,
          )
        self.analog_agc_xx_0 = analog.agc_cc((1e-4), .5, 1.0, 256000)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_agc_xx_0, 0), (self.blocks_conjugate_cc_0, 0))
        self.connect((self.analog_agc_xx_0, 0), (self.blocks_conjugate_cc_0_0, 0))
        self.connect((self.analog_agc_xx_0, 0), (self.blocks_delay_0, 0))
        self.connect((self.analog_agc_xx_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.analog_nbfm_rx_0, 0), (self.blocks_multiply_xx_2, 0))
        self.connect((self.blocks_char_to_float_0, 0), (self.blocks_repeat_0, 0))
        self.connect((self.blocks_complex_to_mag_0, 0), (self.blocks_sub_xx_0, 1))
        self.connect((self.blocks_complex_to_mag_0_0, 0), (self.blocks_sub_xx_0, 0))
        self.connect((self.blocks_conjugate_cc_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.blocks_conjugate_cc_0_0, 0), (self.blocks_multiply_xx_1, 0))
        self.connect((self.blocks_delay_0, 0), (self.blocks_multiply_xx_1, 1))
        self.connect((self.blocks_integrate_xx_0, 0), (self.blocks_complex_to_mag_0_0, 0))
        self.connect((self.blocks_integrate_xx_0_0, 0), (self.blocks_multiply_const_vxx_1, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.audio_sink_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.epy_block_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_1, 0), (self.blocks_complex_to_mag_0, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.blocks_integrate_xx_0_0, 0))
        self.connect((self.blocks_multiply_xx_1, 0), (self.blocks_integrate_xx_0, 0))
        self.connect((self.blocks_multiply_xx_2, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_repeat_0, 0), (self.blocks_multiply_xx_2, 1))
        self.connect((self.blocks_repeat_0, 0), (self.epy_block_0_0, 1))
        self.connect((self.blocks_sub_xx_0, 0), (self.digital_binary_slicer_fb_0, 0))
        self.connect((self.digital_binary_slicer_fb_0, 0), (self.blocks_char_to_float_0, 0))
        self.connect((self.digital_costas_loop_cc_0, 0), (self.analog_agc_xx_0, 0))
        self.connect((self.digital_costas_loop_cc_0, 0), (self.analog_nbfm_rx_0, 0))
        self.connect((self.iio_pluto_source_0, 0), (self.digital_costas_loop_cc_0, 0))


    def get_thresh(self):
        return self.thresh

    def set_thresh(self, thresh):
        self.thresh = thresh
        self.blocks_multiply_const_vxx_1.set_k(self.thresh)

    def get_rf_gain(self):
        return self.rf_gain

    def set_rf_gain(self, rf_gain):
        self.rf_gain = rf_gain
        self.iio_pluto_source_0.set_gain(0, self.rf_gain)

    def get_int_length(self):
        return self.int_length

    def set_int_length(self, int_length):
        self.int_length = int_length
        self.blocks_repeat_0.set_interpolation((int(self.int_length*self.audio_samp_rate/self.RF_samp_rate)))

    def get_carrier_freq(self):
        return self.carrier_freq

    def set_carrier_freq(self, carrier_freq):
        self.carrier_freq = carrier_freq
        self.iio_pluto_source_0.set_frequency(self.carrier_freq)

    def get_audio_samp_rate(self):
        return self.audio_samp_rate

    def set_audio_samp_rate(self, audio_samp_rate):
        self.audio_samp_rate = audio_samp_rate
        self.blocks_repeat_0.set_interpolation((int(self.int_length*self.audio_samp_rate/self.RF_samp_rate)))

    def get_audio_gain(self):
        return self.audio_gain

    def set_audio_gain(self, audio_gain):
        self.audio_gain = audio_gain
        self.blocks_multiply_const_vxx_0.set_k(self.audio_gain)

    def get_RF_samp_rate(self):
        return self.RF_samp_rate

    def set_RF_samp_rate(self, RF_samp_rate):
        self.RF_samp_rate = RF_samp_rate
        self.blocks_repeat_0.set_interpolation((int(self.int_length*self.audio_samp_rate/self.RF_samp_rate)))
        self.iio_pluto_source_0.set_samplerate(self.RF_samp_rate)




def main(top_block_cls=fm_rx, options=None):
    tb = top_block_cls()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()
    tb.flowgraph_started.set()

    try:
        input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
