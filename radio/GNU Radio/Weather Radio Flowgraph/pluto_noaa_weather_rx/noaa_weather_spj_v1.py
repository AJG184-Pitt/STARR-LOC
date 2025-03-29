#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: NOAA Weather Radio
# Author: Steve Jacobs
# GNU Radio version: 3.10.11.0

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import analog
from gnuradio import audio
from gnuradio import blocks
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import iio
import sip
import threading



class noaa_weather_spj_v1(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "NOAA Weather Radio", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("NOAA Weather Radio")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "noaa_weather_spj_v1")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables
        ##################################################
        self.RF_samp_rate = RF_samp_rate = int(2e6)
        self.LPF_decimation = LPF_decimation = 10
        self.carrier_freq = carrier_freq = 162.55e6
        self.audio_samp_rate = audio_samp_rate = int(16e3)
        self.audio_gain = audio_gain = 0.02
        self.LPF_transition = LPF_transition = int(500e3)
        self.LPF_samp_rate = LPF_samp_rate = int(RF_samp_rate/LPF_decimation)
        self.LPF_cutoff = LPF_cutoff = int(50e3)

        ##################################################
        # Blocks
        ##################################################

        self._carrier_freq_range = qtgui.Range(161e6, 164e6, 25e3, 162.55e6, 100)
        self._carrier_freq_win = qtgui.RangeWidget(self._carrier_freq_range, self.set_carrier_freq, "'carrier_freq'", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._carrier_freq_win)
        self._audio_gain_range = qtgui.Range(0, 1, 0.01, 0.02, 100)
        self._audio_gain_win = qtgui.RangeWidget(self._audio_gain_range, self.set_audio_gain, "'audio_gain'", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._audio_gain_win)
        self.rational_resampler_xxx_0_0 = filter.rational_resampler_fff(
                interpolation=(int(audio_samp_rate/8e3)),
                decimation=(int(LPF_samp_rate/8e3)),
                taps=[],
                fractional_bw=0)
        self.qtgui_time_sink_x_0_0_0 = qtgui.time_sink_f(
            1024, #size
            audio_samp_rate, #samp_rate
            "Audio Signal", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0_0_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0_0_0.set_y_axis(-1, 2)

        self.qtgui_time_sink_x_0_0_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0_0_0.enable_tags(False)
        self.qtgui_time_sink_x_0_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0_0_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0_0_0.enable_grid(True)
        self.qtgui_time_sink_x_0_0_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_0_0.enable_control_panel(True)
        self.qtgui_time_sink_x_0_0_0.enable_stem_plot(False)


        labels = ['m(t)', 'Imags(t)}', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0_0_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0_0_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_0_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_0_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_0_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_0_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_0_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0_0_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_0_0_win)
        self.qtgui_freq_sink_x_0_0_0_0_0_0 = qtgui.freq_sink_f(
            1024, #size
            window.WIN_BLACKMAN, #wintype
            0, #fc
            int(audio_samp_rate), #bw
            "Audio Spectrum", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_0_0_0_0_0_0.set_update_time(0.05)
        self.qtgui_freq_sink_x_0_0_0_0_0_0.set_y_axis((-80), 0)
        self.qtgui_freq_sink_x_0_0_0_0_0_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0_0_0_0_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0_0_0_0_0_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0_0_0_0_0_0.enable_grid(True)
        self.qtgui_freq_sink_x_0_0_0_0_0_0.set_fft_average(1.0)
        self.qtgui_freq_sink_x_0_0_0_0_0_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0_0_0_0_0_0.enable_control_panel(True)
        self.qtgui_freq_sink_x_0_0_0_0_0_0.set_fft_window_normalized(False)


        self.qtgui_freq_sink_x_0_0_0_0_0_0.set_plot_pos_half(not True)

        labels = ['M(f)', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0_0_0_0_0_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0_0_0_0_0_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0_0_0_0_0_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0_0_0_0_0_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0_0_0_0_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_0_0_0_0_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0_0_0_0_0_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_freq_sink_x_0_0_0_0_0_0_win)
        self.low_pass_filter_0 = filter.fir_filter_ccf(
            LPF_decimation,
            firdes.low_pass(
                1,
                RF_samp_rate,
                LPF_cutoff,
                LPF_transition,
                window.WIN_HAMMING,
                6.76))
        self.iio_pluto_source_0 = iio.fmcomms2_source_fc32('192.168.2.4' if '192.168.2.4' else iio.get_pluto_uri(), [True, True], 32768)
        self.iio_pluto_source_0.set_len_tag_key('packet_len')
        self.iio_pluto_source_0.set_frequency(int(carrier_freq))
        self.iio_pluto_source_0.set_samplerate(RF_samp_rate)
        self.iio_pluto_source_0.set_gain_mode(0, 'manual')
        self.iio_pluto_source_0.set_gain(0, 52)
        self.iio_pluto_source_0.set_quadrature(True)
        self.iio_pluto_source_0.set_rfdc(True)
        self.iio_pluto_source_0.set_bbdc(True)
        self.iio_pluto_source_0.set_filter_params('Auto', '', 0, 0)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_ff(audio_gain)
        self.audio_sink_0 = audio.sink(16000, '', True)
        self.analog_nbfm_rx_0 = analog.nbfm_rx(
        	audio_rate=LPF_samp_rate,
        	quad_rate=LPF_samp_rate,
        	tau=(75e-6),
        	max_dev=5e3,
          )


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_nbfm_rx_0, 0), (self.rational_resampler_xxx_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.audio_sink_0, 0))
        self.connect((self.iio_pluto_source_0, 0), (self.low_pass_filter_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.analog_nbfm_rx_0, 0))
        self.connect((self.rational_resampler_xxx_0_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.rational_resampler_xxx_0_0, 0), (self.qtgui_freq_sink_x_0_0_0_0_0_0, 0))
        self.connect((self.rational_resampler_xxx_0_0, 0), (self.qtgui_time_sink_x_0_0_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "noaa_weather_spj_v1")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_RF_samp_rate(self):
        return self.RF_samp_rate

    def set_RF_samp_rate(self, RF_samp_rate):
        self.RF_samp_rate = RF_samp_rate
        self.set_LPF_samp_rate(int(self.RF_samp_rate/self.LPF_decimation))
        self.iio_pluto_source_0.set_samplerate(self.RF_samp_rate)
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.RF_samp_rate, self.LPF_cutoff, self.LPF_transition, window.WIN_HAMMING, 6.76))

    def get_LPF_decimation(self):
        return self.LPF_decimation

    def set_LPF_decimation(self, LPF_decimation):
        self.LPF_decimation = LPF_decimation
        self.set_LPF_samp_rate(int(self.RF_samp_rate/self.LPF_decimation))

    def get_carrier_freq(self):
        return self.carrier_freq

    def set_carrier_freq(self, carrier_freq):
        self.carrier_freq = carrier_freq
        self.iio_pluto_source_0.set_frequency(int(self.carrier_freq))

    def get_audio_samp_rate(self):
        return self.audio_samp_rate

    def set_audio_samp_rate(self, audio_samp_rate):
        self.audio_samp_rate = audio_samp_rate
        self.qtgui_freq_sink_x_0_0_0_0_0_0.set_frequency_range(0, int(self.audio_samp_rate))
        self.qtgui_time_sink_x_0_0_0.set_samp_rate(self.audio_samp_rate)

    def get_audio_gain(self):
        return self.audio_gain

    def set_audio_gain(self, audio_gain):
        self.audio_gain = audio_gain
        self.blocks_multiply_const_vxx_0.set_k(self.audio_gain)

    def get_LPF_transition(self):
        return self.LPF_transition

    def set_LPF_transition(self, LPF_transition):
        self.LPF_transition = LPF_transition
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.RF_samp_rate, self.LPF_cutoff, self.LPF_transition, window.WIN_HAMMING, 6.76))

    def get_LPF_samp_rate(self):
        return self.LPF_samp_rate

    def set_LPF_samp_rate(self, LPF_samp_rate):
        self.LPF_samp_rate = LPF_samp_rate

    def get_LPF_cutoff(self):
        return self.LPF_cutoff

    def set_LPF_cutoff(self, LPF_cutoff):
        self.LPF_cutoff = LPF_cutoff
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.RF_samp_rate, self.LPF_cutoff, self.LPF_transition, window.WIN_HAMMING, 6.76))




def main(top_block_cls=noaa_weather_spj_v1, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()
    tb.flowgraph_started.set()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
