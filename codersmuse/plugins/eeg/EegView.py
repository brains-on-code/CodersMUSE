import math
import os

from PySide6 import QtGui
from PySide6.QtWidgets import QLabel


class EegView:
    def __init__(self, data_type):
        self.data_type = data_type
        self.data_type_readable = data_type
        self.participant = None

        self.title = QLabel('EEG')
        self.plot = QLabel()

    def create_view(self, label_layout, plot_layout, participant):
        self.participant = participant
        self.title.setFont(QtGui.QFont("Times", 14, QtGui.QFont.Normal))
        label_layout.addWidget(self.title)

        path = os.path.join('temp', 'eeg', participant + '_eeg_' + '0.png')
        print("eeg link: " + path)
        self.plot.setPixmap(QtGui.QPixmap(path))
        self.plot.show()

        plot_layout.addWidget(self.plot)

    def update_text(self, value):
        self.title.setText(self.data_type_readable + ': ' + str(value).zfill(4))

    def update_plot(self, time):
        path = os.path.join('temp', 'eeg', self.participant + '_eeg_' + str(math.floor(time/100)) + '.png')
        print("eeg data, showing frame: " + path)
        self.plot.setPixmap(QtGui.QPixmap(path))
        self.plot.show()
