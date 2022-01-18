import logging
import math
import os

import matplotlib.pyplot as plt
import nibabel
import numpy
from nilearn import plotting

from codersmuse import config

OVERWRITE_ROI_PLOTS = False  # True
OVERWRITE_EPI_PLOTS = False  # True
MAXIMUM_EPI_PLOTS = 75


def preprocess_fmri_fullbrain(experiment_data):
    # prepare the full-brain fMRI activation plots
    # http://nilearn.github.io/plotting/index.html
    fmri_data = nibabel.load(experiment_data['nifti_path'])
    fmri_data_slices = nibabel.four_to_three(fmri_data)
    for i in range(MAXIMUM_EPI_PLOTS):
        output_file_cond = os.path.join(os.path.dirname(__file__), '..', '..', 'temp', 'fmri', experiment_data['participant'] + '_fMRIfull_' + str(i) + '.png')

        # TODO make the cut slice configurable directly from the UI
        if OVERWRITE_EPI_PLOTS or not os.path.exists(output_file_cond):
            plotting.plot_img(
                fmri_data_slices[i],
                output_file=output_file_cond,
                title='Scan ' + str(i),
                cut_coords=(config.FMRI_CUT_SLICE_X, config.FMRI_CUT_SLICE_Y, config.FMRI_CUT_SLICE_Z),
                annotate=True,
                draw_cross=True,
                black_bg=True,
                cmap=plt.cm.nipy_spectral)


def preprocess_fMRI_ROI(experiment_data):
    for condition in experiment_data['conditions']:
        condition_dataframe = experiment_data['dataframe'][experiment_data['dataframe']['Condition'] == condition]

        logging.info('Preprocessing fMRI ROI data for condition: %s', condition)

        # TODO smarter check whether files already exist and whether to overwrite them
        if not OVERWRITE_ROI_PLOTS:
            logging.info('--> use preprocessed files')
            continue

        # cycle through all physio data types
        condition_start_pos = condition_dataframe['Time'].iloc[0]
        condition_end_pos = condition_dataframe['Time'].iloc[-1]
        condition_dataframe.reset_index(inplace=True, drop=True)

        draw_fMRI_ROI(experiment_data, 'BA6', condition_start_pos, condition_end_pos)


def draw_fMRI_ROI(experiment_data, roi, start_pos, end_pos, span=15, highlight_span=0.5):
    roi_data = experiment_data['fmri']['Average']

    start_pos = math.floor((start_pos / 100) * config.FMRI_RESOLUTION)
    end_pos = math.ceil((end_pos / 100) * config.FMRI_RESOLUTION)

    plt.figure(figsize=(8, 3), dpi=80)

    current_time = start_pos

    logging.info('drawing ROI plot, start pos %s', start_pos)
    logging.info('drawing ROI plot, end pos %s', end_pos)

    for i in range(end_pos - start_pos):
        # draw one plot per second for each frame within one condition
        plt.clf()

        current_time = start_pos + i

        logging.info('drawing ROI plot for %s', current_time)

        minimum = current_time - span
        maximum = current_time + span
        if minimum < 0:
            minimum = 0

        plot_y_values = roi_data[minimum:maximum]
        y_values_mask = numpy.isfinite(plot_y_values)

        if len(plot_y_values) < (maximum - minimum):
            maximum = len(plot_y_values) + minimum

        x_axis = numpy.arange(minimum, maximum, 1)

        plt.plot(x_axis[y_values_mask], plot_y_values[y_values_mask])

        # todo evaluate adding a horizontal line for average condition and/or average of entire session

        # add backgrounds for condition visualization
        task_start = minimum
        if start_pos > minimum:
            task_start = start_pos

        task_end = maximum
        if maximum > end_pos:
            task_end = end_pos

        plt.axvspan(task_start, task_end, color='blue', alpha=0.05)

        # highlight current time
        plt.axvspan(current_time - highlight_span, current_time + highlight_span, color='grey', alpha=0.2)

        # highlight shifted time
        plt.axvspan(config.FMRI_DELAY + current_time - highlight_span, config.FMRI_DELAY + current_time + highlight_span, color='red', alpha=0.2)

        plt.gca().set_ylim(min(roi_data), max(roi_data))

        # save plot as pngs
        file_name = experiment_data['participant'] + '_ROI_' + str(current_time) + '.png'
        plt.savefig(os.path.join('temp', 'fmri', file_name), bbox_inches='tight')
