#!/usr/bin/env python
import logging
import os
import sys

import matplotlib

# Make sure that we are using QT5 for matplotlibs
matplotlib.use('Qt5Agg')

import pandas as pd
from PySide2 import QtWidgets, QtCore
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import (QAction, QApplication, QMainWindow, QMessageBox)

from codersmuse.plugins.behavioral import BehavioralView
from codersmuse.plugins.eyetracking import EyeTrackingData
from codersmuse.plugins.fmri import fMRIData
from codersmuse.plugins.psychophysio import PsychoPhysiologicalData
from codersmuse.DataExplorationView import DataView
from codersmuse import config

OPEN_SAMPLE_DATA_ON_START = True

# logging.basicConfig(filename='example.log', filemode='w', level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setup_menubar()

        if OPEN_SAMPLE_DATA_ON_START:
            self.prepare_and_display_data(
                behavioral_file=os.path.join(os.path.dirname(__file__), '..', 'sample', 'data', 'p01_behavioral.csv'),
                eyetracking_file=os.path.join(os.path.dirname(__file__), '..', 'sample', 'data', 'p01_eyetracking.csv'),
                physio_file=os.path.join(os.path.dirname(__file__), '..', 'sample', 'data', 'p01_physio.csv'),
                fmri_roi_file=os.path.join(os.path.dirname(__file__), '..', 'sample', 'data', 'p01_roi.csv'),
                fmri_nifti_file=os.path.join(os.path.dirname(__file__), '..', 'sample', 'data', 'p01.nii')
            )

    def setup_menubar(self):
        experiment_menu = self.menuBar().addMenu("Experiment Data")
        brain_icon = QIcon(os.path.join(os.path.dirname(__file__), "icon_brain.png"))
        self.open_data = QAction(brain_icon,
                                 "Open Data",
                                 self,
                                 shortcut=QtCore.Qt.CTRL + QtCore.Qt.Key_O,
                                 triggered=self.select_open_file)
        experiment_menu.addAction(self.open_data)
        self.show_sample_data = QAction(brain_icon,
                                        "Show Sample Data",
                                        self,
                                        shortcut=QtCore.Qt.CTRL + QtCore.Qt.Key_T,
                                        triggered=self.prepare_and_display_data)
        experiment_menu.addAction(self.show_sample_data)

        settings_action = QAction("Settings", self, triggered=self.settings)
        experiment_menu.addAction(settings_action)

        # TODO fix the icon on windows/mac
        exit_action = QAction(QIcon.fromTheme("application-exit"), "Exit",
                              self, shortcut=QtCore.Qt.CTRL + QtCore.Qt.Key_Q, triggered=self.close)
        experiment_menu.addAction(exit_action)

        about_menu = self.menuBar().addMenu("About")
        about_tool_action = QAction("Tool Information", self, triggered=self.about_tool)
        about_menu.addAction(about_tool_action)

    def select_open_file(self):
        behavioral_data_file = QtWidgets.QFileDialog.getOpenFileName(self, "Open Behavioral File", QtCore.QDir.currentPath(), "CSV Files (*.csv)")[0]
        if not behavioral_data_file:
            return
        self.check_file(behavioral_data_file)

        eyetracking_data_file = QtWidgets.QFileDialog.getOpenFileName(self, "Open Eye-Tracking File", QtCore.QDir.currentPath(), "CSV Files (*.csv)")[0]
        if not eyetracking_data_file:
            return
        self.check_file(eyetracking_data_file)

        physio_data_file = QtWidgets.QFileDialog.getOpenFileName(self, "Open Phsyio File", QtCore.QDir.currentPath(), "CSV Files (*.csv)")[0]
        if not physio_data_file:
            return
        self.check_file(physio_data_file)

        fmri_roi_file = QtWidgets.QFileDialog.getOpenFileName(self, "Open fMRI ROI File", QtCore.QDir.currentPath(), "CSV Files (*.csv)")[0]
        if not fmri_roi_file:
            return
        self.check_file(fmri_roi_file)

        fmri_nifti_file = QtWidgets.QFileDialog.getOpenFileName(self, "Open fMRI Nifti File", QtCore.QDir.currentPath(), "Nifti Files (*.nii)")[0]
        if not fmri_nifti_file:
            return
        self.check_file(fmri_nifti_file)

        self.prepare_and_display_data(behavioral_data_file, eyetracking_data_file, physio_data_file, fmri_roi_file, fmri_nifti_file)

    def check_file(self, selected_file):
        in_file = QtCore.QFile(selected_file)
        if not in_file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            QtWidgets.QMessageBox.warning(self,
                                          "Open Data File",
                                          "Cannot read file %s:\n%s." % (selected_file, in_file.errorString()))

    def prepare_and_display_data(self, behavioral_file, eyetracking_file, physio_file, fmri_roi_file, fmri_nifti_file, participant='p01'):
        # TODO allow optional data files
        # merge csv files into one dataframe
        df_behavioral = pd.read_csv(behavioral_file, sep=',')
        df_eyetracking = pd.read_csv(eyetracking_file, sep=',')
        df_physio = pd.read_csv(physio_file, sep=',')

        df_merged = df_behavioral.merge(df_eyetracking, on='Time', how='left')
        df_merged = df_merged.merge(df_physio, on='Time', how='left')

        print(df_merged.head(5))

        # TODO change both input csv files to , separated files
        self.experiment_data = {
            'participant': participant,
            'dataframe': df_merged,
            'fmri': pd.read_csv(fmri_roi_file, sep=';'),
            'nifti_path': fmri_nifti_file,
            'conditions': None,
            'responses': {}
        }

        # figure out a list of conditions
        self.experiment_data['conditions'] = self.experiment_data['dataframe']['Condition'].unique()

        # clean & preprocess eye-tracking/physio/fMRI data
        if config.PLUGIN_BEHAVORIAL_ACTIVE:
            BehavioralView.BehavioralView().clean_behavioral_data(self.experiment_data)

        if config.PLUGIN_EYETRACKING_ACTIVE:
            EyeTrackingData.clean_eyetracking_data(self.experiment_data)

        if config.PLUGIN_PHYSIO_ACTIVE:
            PsychoPhysiologicalData.preprocess_psychophysio_data(self.experiment_data)

        if config.PLUGIN_FMRI_ACTIVE:
            fMRIData.preprocess_fMRI_ROI(self.experiment_data)
            fMRIData.preprocess_fmri_fullbrain(self.experiment_data)

        data_view = DataView(self, self.experiment_data)
        self.setCentralWidget(data_view)

    def settings(self):
        msg_box = QMessageBox()
        msg_box.setText("In-application settings will be added in the future. For now, change values directly in the config.py")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def about_tool(self):
        msg_box = QMessageBox()
        msg_box.setText("This tool is a prototype developed by Norman Peitek. More information on our website: https://github.com/brains-on-code/codersmuse")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    mainWin = MainWindow()

    # TODO find a smarter way to set window size dynamically depending on screen size (instead of hard coding in pixels)
    #  available_geometry = app.desktop().availableGeometry(mainWin)
    #  mainWin.resize(availableGeometry.width() * 0.8, availableGeometry.height() * 0.5)

    mainWin.resize(config.WINDOW_WIDTH, config.WINDOW_WIDTH * 0.6)

    mainWin.setWindowTitle('CodersMUSE (fMRI and Eye-Tracking Data Exploration Tool) | v0.1.0')
    mainWin.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), 'images', 'icon_brain.png')))
    mainWin.show()

    sys.exit(app.exec_())
