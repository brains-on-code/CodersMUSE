import numpy
import pandas as pd


def clean_eyetracking_data(experiment_data):
    # eye-tracking data: clean eye-tracking data (e.g., DIV/0!)
    experiment_data['dataframe']['EyeTracking_X'] = experiment_data['dataframe']['EyeTracking_X'].apply(pd.to_numeric, errors='coerce')
    experiment_data['dataframe']['EyeTracking_Y'] = experiment_data['dataframe']['EyeTracking_Y'].apply(pd.to_numeric, errors='coerce')

    if 'PupilDilation' in experiment_data['dataframe']:
        experiment_data['dataframe']['PupilDilation'] = experiment_data['dataframe']['PupilDilation'].apply(pd.to_numeric, errors='coerce')
        experiment_data['dataframe']['PupilDilation'] = experiment_data['dataframe']['PupilDilation'].replace({0: numpy.nan})

    if 'Gaze' in experiment_data['dataframe']:
        experiment_data['dataframe']['Gaze'] = experiment_data['dataframe']['Gaze'].apply(pd.to_numeric, errors='coerce')
