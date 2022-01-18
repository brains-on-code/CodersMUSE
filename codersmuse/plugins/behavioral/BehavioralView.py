import math

import pandas as pd
from PySide6 import QtGui, QtCore
from PySide6.QtWidgets import QHBoxLayout, QLabel


class BehavioralView:
    def __init__(self):
        self.title = QLabel("Behavioral Data")
        self.correctnessLabel = QLabel("")
        self.timeLabel = QLabel("")
        self.clickTimeLabel = QLabel("")

    def clean_behavioral_data(self, experiment_data):
        # behavioral data: find response for each condition
        for condition in experiment_data['conditions']:
            condition_dataframe = experiment_data['dataframe'][experiment_data['dataframe']['Condition'] == condition]

            response_df = condition_dataframe[~pd.isnull(condition_dataframe['Response'])]

            response = {
                'time': None,
                'answer': None,
                'clicktime': None
            }

            if len(response_df) > 0:
                response['time'] = response_df['Time'].iloc[0]
                response['answer'] = response_df['Response'].iloc[0]
                response['clicktime'] = response_df['Clicktime'].iloc[0]

            experiment_data['responses'][condition] = response

    def create_view(self, parent_layout):
        self.title.setFont(QtGui.QFont("Times", 16, QtGui.QFont.Bold))
        parent_layout.addWidget(self.title)

        self.correctnessLabel.setFont(QtGui.QFont("Times", 14, QtGui.QFont.Normal))
        self.timeLabel.setFont(QtGui.QFont("Times", 14, QtGui.QFont.Normal))
        self.clickTimeLabel.setFont(QtGui.QFont("Times", 14, QtGui.QFont.Normal))

        behavioralDataLayout = QHBoxLayout()
        behavioralDataLayout.addWidget(self.correctnessLabel)
        behavioralDataLayout.addWidget(self.timeLabel)
        behavioralDataLayout.addWidget(self.clickTimeLabel)
        behavioralDataLayout.addStretch()

        parent_layout.addLayout(behavioralDataLayout)

    def update_view(self, experiment_data, selected_condition, condition_start_pos):
        response_time = experiment_data['responses'][selected_condition]['time']

        if response_time is not None:
            response_time = response_time - condition_start_pos

            response_time_sec = math.floor(response_time / 100)
            response_time_msec = response_time % 100
            click_time_msec = experiment_data['responses'][selected_condition]['clicktime']

            self.correctnessLabel.setAutoFillBackground(True)
            self.timeLabel.setText(' | Response time: ' + str(response_time_sec).zfill(2) + "." + str(response_time_msec).zfill(2) + ' sec')
            self.clickTimeLabel.setText(' | Click time: ' + str(int(click_time_msec)).zfill(3) + ' msec')

            if experiment_data['responses'][selected_condition]['answer']:
                self.correctnessLabel.setText(" Left click ")
                self.correctnessLabel.setPalette(QtGui.QPalette(QtCore.Qt.green))
            else:
                self.correctnessLabel.setText(" Right click ")
                self.correctnessLabel.setPalette(QtGui.QPalette(QtCore.Qt.red))
        else:
            self.timeLabel.setText(' | Response time: --- ')
            self.clickTimeLabel.setText(' | Click time: --- ')
            self.correctnessLabel.setText(' None ')
            self.correctnessLabel.setPalette(QtGui.QPalette(QtCore.Qt.gray))
            self.correctnessLabel.setAutoFillBackground(True)
