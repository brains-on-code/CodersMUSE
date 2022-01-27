#!/usr/bin/env python
import logging
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np

import pandas as pd
from PySide6 import QtWidgets, QtCore
from PySide6.QtGui import (QAction, QIcon)
from PySide6.QtWidgets import (QApplication, QMainWindow, QMessageBox)

from codersmuse.plugins.behavioral import BehavioralView
from codersmuse.plugins.eyetracking import EyeTrackingData, i2mc
from codersmuse.plugins.eeg import EegData
from codersmuse.plugins.fmri import fMRIData
from codersmuse.plugins.psychophysio import PsychoPhysiologicalData
from codersmuse.DataExplorationView import DataView
from codersmuse import config

OPEN_SAMPLE_DATA_ON_START = False

# logging.basicConfig(filename='example.log', filemode='w', level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setup_menubar()

        if OPEN_SAMPLE_DATA_ON_START:
            self.open_sample_data()

    def open_sample_data(self):
        if True:
            self.prepare_and_display_data_dagstuhl(
                eyetracking_file=os.path.join(os.path.dirname(__file__), '..', 'sample', 'data', 'p02_eyetracking.csv'),
                eeg_file=os.path.join(os.path.dirname(__file__), '..', 'sample', 'data', 'p02_raw.fif'),
            )
        else:
            self.prepare_and_display_data(
                behavioral_file=os.path.join(os.path.dirname(__file__), '..', 'sample', 'data', 'p01_behavioral.csv'),
                eyetracking_file=os.path.join(os.path.dirname(__file__), '..', 'sample', 'data', 'p01_eyetracking.csv'),
                physio_file=os.path.join(os.path.dirname(__file__), '..', 'sample', 'data', 'p01_physio.csv'),
                eeg_file=os.path.join(os.path.dirname(__file__), '..', 'sample', 'data', 'p01_eeg.csv'),  # TODO change to real EEG data once available
                fif_file=os.path.join(os.path.dirname(__file__), '..', 'sample', 'data', 'p01.fif'),  # TODO change to real EEG data once available
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

        self.open_dagstuhl_data = QAction(brain_icon,
                                 "Open Dagstuhl Data",
                                 self,
                                 triggered=self.select_open_file_dagstuhl)
        experiment_menu.addAction(self.open_dagstuhl_data)

        self.show_sample_data = QAction(brain_icon,
                                        "Show Sample Data",
                                        self,
                                        shortcut=QtCore.Qt.CTRL + QtCore.Qt.Key_T,
                                        triggered=self.open_sample_data)
        experiment_menu.addAction(self.show_sample_data)

        settings_action = QAction("Settings", self, triggered=self.settings)
        experiment_menu.addAction(settings_action)

        # TODO fix the icon on windows/mac
        #exit_action = QAction(QIcon.fromTheme("application-exit"), "Exit",
        #                      self, shortcut=QtCore.Qt.CTRL + QtCore.Qt.Key_Q, triggered=self.close)
        #experiment_menu.addAction(exit_action)

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

        physio_data_file = QtWidgets.QFileDialog.getOpenFileName(self, "Open Physio File", QtCore.QDir.currentPath(), "CSV Files (*.csv)")[0]
        if not physio_data_file:
            return
        self.check_file(physio_data_file)

        eeg_data_file = QtWidgets.QFileDialog.getOpenFileName(self, "Open EEG File", QtCore.QDir.currentPath(), "CSV Files (*.csv)")[0]
        if not eeg_data_file:
            return
        self.check_file(eeg_data_file)

        fmri_roi_file = QtWidgets.QFileDialog.getOpenFileName(self, "Open fMRI ROI File", QtCore.QDir.currentPath(), "CSV Files (*.csv)")[0]
        if not fmri_roi_file:
            return
        self.check_file(fmri_roi_file)

        fmri_nifti_file = QtWidgets.QFileDialog.getOpenFileName(self, "Open fMRI Nifti File", QtCore.QDir.currentPath(), "Nifti Files (*.nii)")[0]
        if not fmri_nifti_file:
            return
        self.check_file(fmri_nifti_file)

        self.prepare_and_display_data(behavioral_data_file, eyetracking_data_file, physio_data_file, eeg_file, fmri_roi_file, fmri_nifti_file)

    def select_open_file_dagstuhl(self):
        eyetracking_data_file = QtWidgets.QFileDialog.getOpenFileName(self, "Open Eye-Tracking File", QtCore.QDir.currentPath(), "CSV File (*.csv)")[0]
        if not eyetracking_data_file:
            return
        self.check_file(eyetracking_data_file)

        eeg_file = QtWidgets.QFileDialog.getOpenFileName(self, "Open EEG File", QtCore.QDir.currentPath(), "EEG File (*.fif)")[0]
        if not eeg_file:
            return
        self.check_file(eeg_file)

        self.prepare_and_display_data_dagstuhl(eyetracking_data_file, eeg_file)

    def check_file(self, selected_file):
        in_file = QtCore.QFile(selected_file)
        if not in_file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            QtWidgets.QMessageBox.warning(self,
                                          "Open Data File",
                                          "Cannot read file %s:\n%s." % (selected_file, in_file.errorString()))

    def prepare_and_display_data_dagstuhl(self, eyetracking_file, eeg_file, participant='DagstuhlUser'):
        # TODO allow optional data files
        # merge csv files into one dataframe
        df_eyetracking = pd.read_csv(eyetracking_file, sep=',')
        df_eyetracking = df_eyetracking.drop(columns=["l_gaze_point_in_user_coordinate_system_x",
                                                      "l_gaze_point_in_user_coordinate_system_y",
                                                      "l_gaze_point_in_user_coordinate_system_z",
                                                      "r_gaze_point_in_user_coordinate_system_x",
                                                      "r_gaze_point_in_user_coordinate_system_y",
                                                      "r_gaze_point_in_user_coordinate_system_z",
                                                      "l_gaze_origin_in_user_coordinate_system_x",
                                                      "l_gaze_origin_in_user_coordinate_system_y",
                                                      "l_gaze_origin_in_user_coordinate_system_z",
                                                      "r_gaze_origin_in_user_coordinate_system_x",
                                                      "r_gaze_origin_in_user_coordinate_system_y",
                                                      "r_gaze_origin_in_user_coordinate_system_z"])

        df_eyetracking['EyeTracking_X'] = df_eyetracking.apply(lambda row: 1920 * row['l_display_x'], axis=1)
        df_eyetracking['EyeTracking_Y'] = df_eyetracking.apply(lambda row: 1080 * row['l_display_y'], axis=1)

        df_eyetracking['Time'] = np.arange(df_eyetracking.shape[0])
        df_eyetracking['Condition'] = 'Task1'
        df_eyetracking['Gaze'] = '0'

        print(df_eyetracking.head(5))

        print('classifying eye-tracking data')
        df_eyetracking["time"] = df_eyetracking["time"].astype(float) * 1000.0  # don't move this, necessary for i2mc
        fix, data, par = i2mc.classify_data(df_eyetracking)
        print('classifying eye-tracking data done')

        for i in range(len(fix['startT'])):
            start_time = fix['startT'][i]
            end_time = fix['endT'][i]

            df_eyetracking.loc[(df_eyetracking['time'] > start_time) & (df_eyetracking['time'] < end_time), 'Gaze'] = 1
            df_eyetracking.loc[(df_eyetracking['EyeTracking_X'] > start_time) & (df_eyetracking['time'] < end_time), 'Gaze'] = fix['xpos'][i]
            df_eyetracking.loc[(df_eyetracking['EyeTracking_Y'] > start_time) & (df_eyetracking['time'] < end_time), 'Gaze'] = fix['ypos'][i]

        # TODO change both input csv files to , separated files
        self.experiment_data = {
            'participant': participant,
            'dataframe': df_eyetracking,
            'fmri': None,
            'nifti_path': None,
            'fif_path': eeg_file,
            'conditions': None,
            'responses': {}
        }

        # figure out a list of conditions
        self.experiment_data['conditions'] = ['Task1']

        self.initialize_view()

    def prepare_and_display_data(self, behavioral_file, eyetracking_file, physio_file, eeg_file, fif_file, fmri_roi_file, fmri_nifti_file, participant='p01'):
        # TODO allow optional data files
        # merge csv files into one dataframe
        df_behavioral = pd.read_csv(behavioral_file, sep=',')
        df_eyetracking = pd.read_csv(eyetracking_file, sep=',')
        df_physio = pd.read_csv(physio_file, sep=',')
        df_eeg = pd.read_csv(eeg_file, sep=',')

        df_merged = df_behavioral.merge(df_eyetracking, on='Time', how='left')
        df_merged = df_merged.merge(df_physio, on='Time', how='left')
        df_merged = df_merged.merge(df_eeg, on='Time', how='left')

        print(df_merged.head(5))

        # TODO change both input csv files to , separated files
        self.experiment_data = {
            'participant': participant,
            'dataframe': df_merged,
            'fmri': pd.read_csv(fmri_roi_file, sep=';'),
            'nifti_path': fmri_nifti_file,
            'fif_path': fif_file,
            'conditions': None,
            'responses': {}
        }

        # figure out a list of conditions
        self.experiment_data['conditions'] = self.experiment_data['dataframe']['Condition'].unique()

        self.initialize_view()

    def initialize_view(self):
        # clean & preprocess eye-tracking/physio/fMRI data
        if config.PLUGIN_BEHAVORIAL_ACTIVE:
            BehavioralView.BehavioralView().clean_behavioral_data(self.experiment_data)

        if config.PLUGIN_EYETRACKING_ACTIVE:
            EyeTrackingData.clean_eyetracking_data(self.experiment_data)


        if config.PLUGIN_PHYSIO_ACTIVE:
            PsychoPhysiologicalData.preprocess_psychophysio_data(self.experiment_data)

        if config.PLUGIN_EEG_ACTIVE:
            EegData.preprocess_eeg_data(self.experiment_data)

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

    mainWin.setWindowTitle('CodersMUSE (fMRI and Eye-Tracking Data Exploration Tool) | v0.3.0')
    mainWin.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), 'images', 'icon_brain.png')))
    mainWin.show()

    sys.exit(app.exec())
