import logging
import os

from PySide2 import QtGui
from PySide2.QtWidgets import QLabel

from codersmuse import config


class fMRIFullView:
    def __init__(self):
        self.title = QLabel("fMRI Data: Full Brain")
        self.shift_label = QLabel("Highlighted area in red is shifted forward by " + str(config.FMRI_DELAY) + " seconds (" + str(int(config.FMRI_DELAY * config.FMRI_RESOLUTION)) + " scans)")
        self.full_brain_image = QLabel("")

    def create_view(self, parent_layout, experiment_data):
        self.title.setFont(QtGui.QFont("Times", 16, QtGui.QFont.Bold))
        parent_layout.addWidget(self.title)
        parent_layout.addWidget(self.shift_label)

        self.full_brain_image.setPixmap(QtGui.QPixmap(os.path.join('temp', 'fmri', experiment_data['participant'] + '_fMRIfull_0.png')))
        self.full_brain_image.show()

        parent_layout.addWidget(self.full_brain_image)

    def update_data(self, experiment_data, shifted_scan):
        scan_image = os.path.join('temp', 'fmri', experiment_data['participant'] + '_fMRIfull_' + str(shifted_scan) + '.png')
        logging.info('showing fMRI full-brain data: current scan: %s', scan_image)

        self.full_brain_image.setPixmap(QtGui.QPixmap(scan_image))
        self.full_brain_image.show()
