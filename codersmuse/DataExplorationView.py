import math

from PySide6 import QtGui, QtCore, QtWidgets
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QMessageBox, QComboBox

from codersmuse import config
from codersmuse.plugins.behavioral.BehavioralView import BehavioralView
from codersmuse.plugins.eeg.EegView import EegView
from codersmuse.plugins.eyetracking.EyeTrackingView import EyeTrackingView
from codersmuse.plugins.fmri.fMRIFullView import fMRIFullView
from codersmuse.plugins.fmri.fMRIRoiView import fMRIRoiView
from codersmuse.plugins.psychophysio.PsychoPhysiologicalView import PsychoPhysiologicalView

SHIFT_FMRI_SCAN = 3


class DataView(QWidget):
    def __init__(self, main_window, experiment_data):
        super(DataView, self).__init__()

        self.file_name = None
        self.main_window = main_window
        self.experiment_data = experiment_data
        self.condition_dataframe = None
        self.maximum_time_sec = None
        self.maximum_time_msec = None
        self.timer = QTimer(self)

        self.behavioralView = BehavioralView()
        self.eyetrackingView = EyeTrackingView(main_window)
        self.physioRespiration = PsychoPhysiologicalView('Respiration')
        self.physioHeartRate = PsychoPhysiologicalView('HeartRate')
        self.physioPupilDilation = PsychoPhysiologicalView('PupilDilation')
        self.fMRIRoiView = fMRIRoiView()
        self.fMRIFullView = fMRIFullView()
        self.eegView = EegView('ch1')

        self.create_layout()

        # initialize view
        self.stimuli_changed(0)

    def create_layout(self):
        left_layout = self.create_layout_left()
        right_layout = self.create_layout_right()
        bottom_layout = self.create_layout_bottom()

        center_layout = QHBoxLayout()
        center_layout.addLayout(left_layout)
        center_layout.addLayout(right_layout)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(center_layout)
        main_layout.addLayout(bottom_layout)

    def create_layout_left(self):
        left_layout = QVBoxLayout()
        self.participant_label = QLabel("Participant: " + self.experiment_data['participant'])
        self.participant_label.setFont(QtGui.QFont("Times", 16, QtGui.QFont.Bold))
        self.participant_label.setTextInteractionFlags(Qt.TextBrowserInteraction)

        left_layout.addWidget(self.participant_label)
        left_stimuli_layout = QHBoxLayout()
        stimuli_label = QLabel("Stimuli: ")
        stimuli_label.setFont(QtGui.QFont("Times", 16, QtGui.QFont.Bold))
        left_stimuli_layout.addWidget(stimuli_label)

        self.stimuli_selection_box = QComboBox()
        self.stimuli_selection_box.setFont(QtGui.QFont("Times", 14, QtGui.QFont.Normal))
        for condition in self.experiment_data['conditions']:
            self.stimuli_selection_box.addItem(condition)

        self.stimuli_selection_box.currentIndexChanged[int].connect(self.stimuli_changed)
        left_stimuli_layout.addWidget(self.stimuli_selection_box)
        left_stimuli_layout.addStretch()
        left_layout.addLayout(left_stimuli_layout)
        left_layout.addStretch()

        if config.PLUGIN_EYETRACKING_ACTIVE:
            self.eyetrackingView.create_view(left_layout)
            left_layout.addStretch()

        if config.PLUGIN_BEHAVORIAL_ACTIVE:
            self.behavioralView.create_view(left_layout)

        return left_layout

    def create_layout_bottom(self):
        bottomLayout = QHBoxLayout()
        self.time = 0
        self.timeLabel = QLabel("0:00.00 / 0:00.00")
        self.timeLabel.setFont(QtGui.QFont("Times", 14, QtGui.QFont.Normal))

        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(0, 99)
        self.slider.setValue(0)
        self.slider.setTickInterval(100)
        self.slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.slider.setToolTip("Time")
        self.slider.sliderMoved.connect(self.set_time)

        self.playButton = QPushButton("Play")
        self.playButton.clicked.connect(self.play_data)
        self.isPlaying = False

        bottomLayout.addStretch()
        bottomLayout.addWidget(self.playButton)
        playerLayout = QVBoxLayout()
        timeLayout = QHBoxLayout()
        timeLayout.addStretch()
        timeLayout.addWidget(self.timeLabel)
        timeLayout.addStretch()

        playerLayout.addLayout(timeLayout)
        playerLayout.addWidget(self.slider)
        bottomLayout.addLayout(playerLayout)
        bottomLayout.addStretch()

        return bottomLayout

    def create_layout_right(self):
        right_layout = QVBoxLayout()

        if config.PLUGIN_PHYSIO_ACTIVE:
            physio_label = QLabel("Psycho-Physiological Data")
            physio_label.setFont(QtGui.QFont("Times", 16, QtGui.QFont.Bold))
            right_layout.addWidget(physio_label)

            physio_label_layout = QHBoxLayout()
            physio_plot_layout = QHBoxLayout()

            self.physioHeartRate.create_view(physio_label_layout, physio_plot_layout, self.experiment_data['participant'])
            self.physioRespiration.create_view(physio_label_layout, physio_plot_layout, self.experiment_data['participant'])
            self.physioPupilDilation.create_view(physio_label_layout, physio_plot_layout, self.experiment_data['participant'])

            right_layout.addLayout(physio_label_layout)
            right_layout.addLayout(physio_plot_layout)

        if config.PLUGIN_FMRI_ACTIVE:
            self.fMRIRoiView.create_view(right_layout, self.experiment_data)
            self.fMRIFullView.create_view(right_layout, self.experiment_data)

        if config.PLUGIN_EEG_ACTIVE:
            eeg_label = QLabel("EEG Data")
            eeg_label.setFont(QtGui.QFont("Times", 16, QtGui.QFont.Bold))

            eeg_label_layout = QHBoxLayout()
            eeg_plot_layout = QHBoxLayout()

            self.eegView.create_view(eeg_label_layout, eeg_plot_layout, self.experiment_data['participant'])

            right_layout.addWidget(eeg_label)
            right_layout.addLayout(eeg_plot_layout)

        right_layout.addStretch(1)

        return right_layout

    def set_time(self, time):
        self.time = time
        self.update_data(force_update=True)

    def stimuli_changed(self, index):
        selected_condition = self.experiment_data['conditions'][index]

        self.condition_dataframe = self.experiment_data['dataframe'][self.experiment_data['dataframe']['Condition'] == selected_condition]
        self.condition_start_pos = self.condition_dataframe['Time'].iloc[0]
        self.condition_end_pos = self.condition_dataframe['Time'].iloc[-1]
        self.condition_dataframe.reset_index(inplace=True, drop=True)

        self.maximum_time_sec = math.floor(len(self.condition_dataframe) / 100)
        self.maximum_time_msec = len(self.condition_dataframe) % 100

        self.time = 0
        self.shifted_scan = None
        self.slider.setMaximum(self.maximum_time_sec * 100 + self.maximum_time_msec)
        self.slider.setValue(0)

        self.timeLabel.setText("0:00.00 / 0:" + str(self.maximum_time_sec).zfill(2) + "." + str(self.maximum_time_msec).zfill(2))

        # update plug-in views
        if config.PLUGIN_BEHAVORIAL_ACTIVE:
            self.behavioralView.update_view(self.experiment_data, selected_condition, self.condition_start_pos)

        if config.PLUGIN_EYETRACKING_ACTIVE:
            self.eyetrackingView.setConditionDataframe(selected_condition, self.condition_dataframe)

        self.update_data()

    def play_data(self):
        if self.isPlaying:
            self.isPlaying = False
            self.timer.stop()
            self.playButton.setText('Play')
        else:
            self.timer.setTimerType(QtCore.Qt.TimerType.PreciseTimer)
            self.timer.timeout.connect(self.update_data)
            self.timer.start(10)
            self.isPlaying = True
            self.playButton.setText('Stop')

    def update_data(self, force_update=False):
        # check if timer should stop
        if self.time >= (self.maximum_time_sec * 100 + self.maximum_time_msec):
            self.timer.stop()
            self.isPlaying = False
            self.playButton.setText('Play')
        else:
            self.slider.setValue(self.time)
            self.timeLabel.setText("0:" + str(math.floor(self.time / 100)).zfill(2) + "." + str(self.time % 100).zfill(2) + " / 0:" + str(self.maximum_time_sec).zfill(2) + "." + str(self.maximum_time_msec).zfill(2))

            if config.PLUGIN_PHYSIO_ACTIVE:
                # psycho-physiological data
                if force_update or self.time % 10 == 0:
                    self.physioRespiration.update_text(self.condition_dataframe['Respiration'][self.time])
                    self.physioHeartRate.update_text(self.condition_dataframe['HeartRate'][self.time])
                    self.physioPupilDilation.update_text(self.condition_dataframe['PupilDilation'][self.time])

                # only update plots every second instead of every millisecond (for performance)
                # use preprocessed plots and just switch image for faster speeds
                if force_update or self.time % 100 == 0:
                    self.physioRespiration.update_plot(self.time)
                    self.physioHeartRate.update_plot(self.time)
                    self.physioPupilDilation.update_plot(self.time)

            if config.PLUGIN_EYETRACKING_ACTIVE:
                # eye-tracking data
                self.eyetrackingView.setTime(self.time)

            # eeg data
            if config.PLUGIN_EEG_ACTIVE:
                self.eegView.update_text(self.condition_dataframe['eeg'][self.time])
                self.eegView.update_plot(self.time)

            # fMRI data
            if config.PLUGIN_FMRI_ACTIVE:
                current_scan = math.floor(((self.condition_start_pos + self.time) / 100) * config.FMRI_RESOLUTION)
                shifted_scan = current_scan + SHIFT_FMRI_SCAN

                if self.shifted_scan != shifted_scan:
                    self.fMRIRoiView.update_data(self.experiment_data, current_scan)
                    self.fMRIFullView.update_data(self.experiment_data, shifted_scan)

                    self.shifted_scan = shifted_scan

            # todo: it should only add 1ms per tick, for now artificially jump a few ms to fix slow replay time
            self.time += 4  # my Macbook is really slow
            # self.time += 2  # windows PC is faster
