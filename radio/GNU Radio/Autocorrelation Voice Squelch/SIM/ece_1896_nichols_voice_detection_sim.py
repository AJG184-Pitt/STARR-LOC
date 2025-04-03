#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Voice Detection Simulation
# Author: adam-nichols
# GNU Radio version: 3.10.11.0

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import analog
from gnuradio import audio
from gnuradio import blocks
from gnuradio import digital
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import sip
import threading



class ece_1896_nichols_voice_detection_sim(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Voice Detection Simulation", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Voice Detection Simulation")
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

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "ece_1896_nichols_voice_detection_sim")

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
        self.thresh = thresh = .5
        self.noise_gain = noise_gain = .1
        self.int_length = int_length = 24000
        self.audio_samp_rate = audio_samp_rate = 48000
        self.audio_gain = audio_gain = 1

        ##################################################
        # Blocks
        ##################################################

        self._thresh_range = qtgui.Range(0, 1, .01, .5, 200)
        self._thresh_win = qtgui.RangeWidget(self._thresh_range, self.set_thresh, "'thresh'", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._thresh_win)
        self._noise_gain_range = qtgui.Range(0, 5, .01, .1, 200)
        self._noise_gain_win = qtgui.RangeWidget(self._noise_gain_range, self.set_noise_gain, "'noise_gain'", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._noise_gain_win)
        self._audio_gain_range = qtgui.Range(0, 5, .01, 1, 200)
        self._audio_gain_win = qtgui.RangeWidget(self._audio_gain_range, self.set_audio_gain, "'audio_gain'", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._audio_gain_win)
        self.qtgui_time_sink_x_1 = qtgui.time_sink_f(
            (3*int(audio_samp_rate/int_length)), #size
            audio_samp_rate/int_length, #samp_rate
            "", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_1.set_update_time(0.10)
        self.qtgui_time_sink_x_1.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_1.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_1.enable_tags(True)
        self.qtgui_time_sink_x_1.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_1.enable_autoscale(False)
        self.qtgui_time_sink_x_1.enable_grid(False)
        self.qtgui_time_sink_x_1.enable_axis_labels(True)
        self.qtgui_time_sink_x_1.enable_control_panel(False)
        self.qtgui_time_sink_x_1.enable_stem_plot(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
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
                self.qtgui_time_sink_x_1.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_1.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_1.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_1.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_1.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_1.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_1.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_1_win = sip.wrapinstance(self.qtgui_time_sink_x_1.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_1_win)
        self.qtgui_time_sink_x_0 = qtgui.time_sink_f(
            1024, #size
            audio_samp_rate, #samp_rate
            "Raw Audio Message", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0.enable_tags(True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0.enable_grid(False)
        self.qtgui_time_sink_x_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0.enable_control_panel(True)
        self.qtgui_time_sink_x_0.enable_stem_plot(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
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
                self.qtgui_time_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_win)
        self.digital_binary_slicer_fb_0 = digital.binary_slicer_fb()
        self.blocks_wavfile_source_0 = blocks.wavfile_source('/home/adam-nichols/Documents/Pitt/ECE 1896/ECE1472 Lab1 speech files/Fessenden_long_clip_fs48000_mono.wav', True)
        self.blocks_sub_xx_0 = blocks.sub_ff(1)
        self.blocks_multiply_xx_1 = blocks.multiply_vff(1)
        self.blocks_multiply_xx_0 = blocks.multiply_vff(1)
        self.blocks_multiply_const_vxx_1 = blocks.multiply_const_ff(thresh)
        self.blocks_multiply_const_vxx_0_0 = blocks.multiply_const_ff(audio_gain)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_ff(noise_gain)
        self.blocks_integrate_xx_0_0 = blocks.integrate_ff(int_length, 1)
        self.blocks_integrate_xx_0 = blocks.integrate_ff(int_length, 1)
        self.blocks_delay_0 = blocks.delay(gr.sizeof_float*1, 1)
        self.blocks_char_to_float_0 = blocks.char_to_float(1, 1)
        self.blocks_add_xx_0 = blocks.add_vff(1)
        self.audio_sink_0 = audio.sink(audio_samp_rate, '', True)
        self.analog_noise_source_x_0 = analog.noise_source_f(analog.GR_GAUSSIAN, 1, 0)
        self.analog_agc_xx_0 = analog.agc_ff((1e-4), .5, 1.0, 65536)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_agc_xx_0, 0), (self.audio_sink_0, 0))
        self.connect((self.analog_agc_xx_0, 0), (self.blocks_delay_0, 0))
        self.connect((self.analog_agc_xx_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.analog_agc_xx_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.analog_agc_xx_0, 0), (self.blocks_multiply_xx_1, 0))
        self.connect((self.analog_agc_xx_0, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.analog_noise_source_x_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.analog_agc_xx_0, 0))
        self.connect((self.blocks_char_to_float_0, 0), (self.qtgui_time_sink_x_1, 0))
        self.connect((self.blocks_delay_0, 0), (self.blocks_multiply_xx_1, 1))
        self.connect((self.blocks_integrate_xx_0, 0), (self.blocks_sub_xx_0, 1))
        self.connect((self.blocks_integrate_xx_0_0, 0), (self.blocks_multiply_const_vxx_1, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.blocks_multiply_const_vxx_1, 0), (self.blocks_sub_xx_0, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.blocks_integrate_xx_0_0, 0))
        self.connect((self.blocks_multiply_xx_1, 0), (self.blocks_integrate_xx_0, 0))
        self.connect((self.blocks_sub_xx_0, 0), (self.digital_binary_slicer_fb_0, 0))
        self.connect((self.blocks_wavfile_source_0, 0), (self.blocks_multiply_const_vxx_0_0, 0))
        self.connect((self.digital_binary_slicer_fb_0, 0), (self.blocks_char_to_float_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "ece_1896_nichols_voice_detection_sim")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_thresh(self):
        return self.thresh

    def set_thresh(self, thresh):
        self.thresh = thresh
        self.blocks_multiply_const_vxx_1.set_k(self.thresh)

    def get_noise_gain(self):
        return self.noise_gain

    def set_noise_gain(self, noise_gain):
        self.noise_gain = noise_gain
        self.blocks_multiply_const_vxx_0.set_k(self.noise_gain)

    def get_int_length(self):
        return self.int_length

    def set_int_length(self, int_length):
        self.int_length = int_length
        self.qtgui_time_sink_x_1.set_samp_rate(self.audio_samp_rate/self.int_length)

    def get_audio_samp_rate(self):
        return self.audio_samp_rate

    def set_audio_samp_rate(self, audio_samp_rate):
        self.audio_samp_rate = audio_samp_rate
        self.qtgui_time_sink_x_0.set_samp_rate(self.audio_samp_rate)
        self.qtgui_time_sink_x_1.set_samp_rate(self.audio_samp_rate/self.int_length)

    def get_audio_gain(self):
        return self.audio_gain

    def set_audio_gain(self, audio_gain):
        self.audio_gain = audio_gain
        self.blocks_multiply_const_vxx_0_0.set_k(self.audio_gain)




def main(top_block_cls=ece_1896_nichols_voice_detection_sim, options=None):

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
