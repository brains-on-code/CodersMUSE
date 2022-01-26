import logging
import os

from PySide6 import QtWidgets, QtGui
from PySide6.QtGui import QPixmap, QColor
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QLabel

from codersmuse import config


class EyeTrackingView(QtWidgets.QWidget):
    def __init__(self, main_window):
        QtWidgets.QWidget.__init__(self, main_window)

        self.main_window = main_window
        self.eyetracking_title = QLabel("Eye-Tracking Data")
        self.eyetracking_overlay = EyeTrackingOverlay(main_window)

    def create_view(self, parent_layout):
        self.eyetracking_title.setFont(QtGui.QFont("Times", 16, QtGui.QFont.Bold))
        parent_layout.addWidget(self.eyetracking_title)
        parent_layout.addWidget(self.eyetracking_overlay)

    def setConditionDataframe(self, selected_condition, selected_condition_dataframe):
        self.eyetracking_overlay.setConditionDataframe(selected_condition, selected_condition_dataframe)

    def setTime(self, time):
        self.eyetracking_overlay.setTime(time)


class EyeTrackingOverlay(QOpenGLWidget):
    def __init__(self, main_window):
        QOpenGLWidget.__init__(self, main_window)

        self.condition_dataframe = None
        self.image = None
        self.scale_factor = None

        self.current_time = 0

        self.main_window = main_window

    def setImage(self, parent, imagePath):
        calculated_width = config.WINDOW_WIDTH * 0.48
        calculated_height = config.WINDOW_WIDTH * 0.48 * 0.75

        logging.debug('eyetracking view: window width: %s', config.WINDOW_WIDTH)
        logging.debug('eyetracking view: calculated image width: %s', calculated_width)
        logging.debug('eyetracking view: calculated image height: %s', calculated_height)
        logging.debug('eyetracking view: image path: %s', imagePath)

        self.image = QPixmap(imagePath)
        original_size = self.image.size()

        self.image = self.image.scaledToWidth(calculated_width)
        scaled_size = self.image.size()

        self.scale_factor = scaled_size.height() / original_size.height()

        self.setFixedWidth(calculated_width)
        self.setFixedHeight(calculated_height)

        self.current_time = 0
        self.update()

    def setConditionDataframe(self, selected_condition, selected_condition_dataframe):
        self.condition_dataframe = selected_condition_dataframe
        image_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'sample', 'images', selected_condition)
        self.setImage(self, image_path)

    def setTime(self, time):
        self.current_time = time
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawPixmap(0, 0, self.image)

        if config.EYETRACKING_DRAW_MODE == 'saccades':
            self.drawSaccadesFixations(painter)
        else:
            self.drawGazePath(painter)

    def drawSaccadesFixations(self, painter):
        last_element = self.current_time

        # figure out which time frame to draw
        if self.current_time > len(self.condition_dataframe):
            last_element = len(self.condition_dataframe)

        if self.current_time > config.EYETRACKING_LENGTH_TRACE:
            first_element = last_element - config.EYETRACKING_LENGTH_TRACE
        else:
            first_element = 0

        self.fixations = self.condition_dataframe.loc[self.condition_dataframe['Gaze'] == 1]
        self.saccades = self.condition_dataframe.loc[self.condition_dataframe['Gaze'] == 0]

        # draw saccades
        saccade_color = QColor('yellow')
        saccade_pen = QtGui.QPen(saccade_color)
        painter.setPen(saccade_pen)

        path = QtGui.QPainterPath()
        path.moveTo(
            self.scale_factor * self.condition_dataframe['EyeTracking_X'][first_element],
            self.scale_factor * self.condition_dataframe['EyeTracking_Y'][first_element]
        )

        for i in range(first_element, last_element):
            if i in self.saccades.index:
                path.lineTo(
                    self.scale_factor * self.saccades['EyeTracking_X'][i],
                    self.scale_factor * self.saccades['EyeTracking_Y'][i]
                )
        painter.drawPath(path)

        # draw fixations
        fixation_color = QColor('green')
        fixation_pen = QtGui.QPen(fixation_color)
        painter.setPen(fixation_pen)

        for i in range(first_element, last_element):
            if i in self.fixations.index:
                painter.drawEllipse(
                    self.scale_factor * self.fixations['EyeTracking_X'][i],
                    self.scale_factor * self.fixations['EyeTracking_Y'][i],
                    15,
                    15
                )

    def drawGazePath(self, painter):
        color = QColor('yellow')
        pen = QtGui.QPen(color)
        painter.setPen(pen)

        path = QtGui.QPainterPath()

        last_element = self.current_time

        # figure out which time frame to draw
        if self.current_time > len(self.condition_dataframe):
            last_element = len(self.condition_dataframe)

        if self.current_time > config.EYETRACKING_LENGTH_TRACE:
            first_element = last_element - config.EYETRACKING_LENGTH_TRACE
        else:
            first_element = 0

        path.moveTo(
            self.scale_factor * self.condition_dataframe['EyeTracking_X'][first_element],
            self.scale_factor * self.condition_dataframe['EyeTracking_Y'][first_element]
        )

        for i in range(first_element, last_element):
            path.lineTo(
                self.scale_factor * self.condition_dataframe['EyeTracking_X'][i],
                self.scale_factor * self.condition_dataframe['EyeTracking_Y'][i]
            )
        painter.drawPath(path)
