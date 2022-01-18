import logging
import os

import matplotlib
import matplotlib.pyplot as plt
import numpy

OVERWRITE_EEG_PLOTS = True

width = 6
height = 3
dpi = 40

matplotlib.rcParams.update({'font.size': 8})


def preprocess_eeg_data(experiment_data):
    # split experiment data by condition
    for i, condition in enumerate(experiment_data['conditions']):
        condition_dataframe = experiment_data['dataframe'][experiment_data['dataframe']['Condition'] == condition]

        # print(condition_dataframe.head(5))

        logging.info('Preprocessing eeg data for condition: %s', condition)

        # TODO check whether files already exist and whether to overwrite them
        if not OVERWRITE_EEG_PLOTS:
            logging.info('--> use preprocessed files')
            continue

        # cycle through all physio data types
        condition_start_pos = condition_dataframe['Time'].iloc[0]
        condition_end_pos = condition_dataframe['Time'].iloc[-1]
        condition_dataframe.reset_index(inplace=True, drop=True)

        draw_eeg_data(experiment_data, condition_start_pos, condition_end_pos)

        # todo change code in other places to use preprocessed pngs


def draw_eeg_data(experiment_data, start_pos, end_pos, span=1200, highlight_span=50, full_plot=False):
    eeg_data = experiment_data['dataframe']['eeg']

    plt.figure(figsize=(width, height), dpi=dpi)

    for i in range(end_pos - start_pos):
        if i % 100 != 0:
            continue

        # draw one plot per second for each frame within one condition
        plt.clf()

        current_time = i

        y_values_mask = numpy.isfinite(eeg_data)
        x_axis = numpy.arange(0, len(eeg_data), 1)

        minimum = start_pos + current_time - span
        maximum = start_pos + current_time + span
        if minimum < 0:
            minimum = 0

        plot_y_values = eeg_data[minimum:maximum]
        y_values_mask = numpy.isfinite(plot_y_values)

        if len(plot_y_values) < (maximum - minimum):
            maximum = len(plot_y_values) + minimum

        x_axis = numpy.arange(minimum, maximum, 1)

        plt.plot(x_axis[y_values_mask], plot_y_values[y_values_mask])

        # todo add horizontal line for average condition and/or average of entire session

        # add backgrounds for condition visualization
        task_start = minimum
        if start_pos > minimum:
            task_start = start_pos

        task_end = maximum
        if maximum > end_pos:
            task_end = end_pos

        plt.axvspan(task_start, task_end, color='blue', alpha=0.05)

        # highlight current time
        plt.axvspan(start_pos + current_time - highlight_span, start_pos + current_time + highlight_span, color='red', alpha=0.2)
        plt.gca().set_ylim(min(eeg_data), max(eeg_data))

        # save plot as pngs
        file_name = experiment_data['participant'] + '_' + 'eeg' + '_' + str(current_time) + '.png'
        plt.savefig(os.path.join('temp', 'physio', file_name), bbox_inches='tight')
