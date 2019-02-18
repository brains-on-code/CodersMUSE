import logging
import os

from PySide2 import QtGui
from PySide2.QtWidgets import QLabel

from codersmuse import config


class fMRIRoiView():
    def __init__(self):
        self.title = QLabel("fMRI Data: ROI BA6")
        self.shift_label = QLabel("Highlighted area in red is shifted forward by " + str(config.FMRI_DELAY) + " seconds (" + str(int(config.FMRI_DELAY * config.FMRI_RESOLUTION)) + " scans)")
        self.roi_plot = QLabel("")

    def create_view(self, parent_layout, experiment_data):
        self.title.setFont(QtGui.QFont("Times", 16, QtGui.QFont.Bold))
        parent_layout.addWidget(self.title)
        parent_layout.addWidget(self.shift_label)

        plot_path = os.path.join('temp', 'fmri', experiment_data['participant'] + '_ROI_0.png')
        logging.info('fMRI plot path: %s', plot_path)

        self.roi_plot.setPixmap(QtGui.QPixmap(plot_path))
        self.roi_plot.show()
        parent_layout.addWidget(self.roi_plot)

    def update_data(self, experiment_data, current_scan):
        plot_path = os.path.join('temp', 'fmri', experiment_data['participant'] + '_ROI_' + str(current_scan) + '.png')
        logging.info('fMRI plot path: %s', plot_path)

        self.roi_plot.setPixmap(QtGui.QPixmap(plot_path))
        self.roi_plot.show()
