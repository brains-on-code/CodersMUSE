import os

from PySide6 import QtGui
from PySide6.QtWidgets import QLabel


class PsychoPhysiologicalView:
    def __init__(self, data_type):
        self.data_type = data_type
        self.participant = None

        if data_type == 'HeartRate':
            self.data_type_readable = 'Heart Rate'
        elif data_type == 'Respiration':
            self.data_type_readable = 'Respiration'
        elif data_type == 'PupilDilation':
            self.data_type_readable = 'Pupil Dilation'

        self.title = QLabel(self.data_type_readable)
        self.plot = QLabel()

    def create_view(self, label_layout, plot_layout, participant):
        self.participant = participant
        self.title.setFont(QtGui.QFont("Times", 14, QtGui.QFont.Normal))
        label_layout.addWidget(self.title)

        path = os.path.join('temp', 'physio', participant + '_' + self.data_type + '_0.png')
        self.plot.setPixmap(QtGui.QPixmap(path))
        self.plot.show()

        plot_layout.addWidget(self.plot)

    def update_text(self, value):
        self.title.setText(self.data_type_readable + ': ' + str(value).zfill(4))

    def update_plot(self, time):
        path = os.path.join('temp', 'physio', self.participant + '_' + self.data_type + '_' + str(int(round(time, -2))) + '.png')
        self.plot.setPixmap(QtGui.QPixmap(path))
        self.plot.show()
