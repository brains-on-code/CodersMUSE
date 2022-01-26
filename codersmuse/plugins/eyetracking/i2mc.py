import I2MC


def classify_data(df_eyetracking):
    opt = dict()
    # General variables for eye-tracking data
    # maximum value of horizontal resolution in pixels
    opt['xres'] = 1920.0
    opt['yres'] = 1080.0  # maximum value of vertical resolution in pixels
    # missing value for horizontal position in eye-tracking data (example data uses -xres). used throughout
    # internal_helpers as signal for data loss
    opt['missingx'] = -opt['xres']
    # missing value for vertical position in eye-tracking data (example data uses -yres). used throughout
    # internal_helpers as signal for data loss
    opt['missingy'] = -opt['yres']
    # sampling frequency of data (check that this value matches with values actually obtained from measurement!)
    opt['freq'] = 250.0

    # Variables for the calculation of visual angle
    # These values are used to calculate noise measures (RMS and BCEA) of
    # fixations. The may be left as is, but don't use the noise measures then.
    # If either or both are empty, the noise measures are provided in pixels
    # instead of degrees.
    # screen size in cm
    opt['scrSz'] = [55.0, 32.5]
    # distance to screen in cm.
    opt['disttoscreen'] = 65.0

    df_eyetracking["time"] = df_eyetracking["time"].astype(float)
    df_eyetracking["time"] = df_eyetracking["time"] - df_eyetracking["time"].iloc[0]

    df_eyetracking["l_display_x"] = df_eyetracking["l_display_x"].astype(float) * opt["xres"]
    df_eyetracking["l_display_y"] = df_eyetracking["l_display_y"].astype(float) * opt["yres"]
    df_eyetracking["r_display_x"] = df_eyetracking["r_display_x"].astype(float) * opt["xres"]
    df_eyetracking["r_display_y"] = df_eyetracking["r_display_y"].astype(float) * opt["yres"]
    df_eyetracking["l_valid"] = df_eyetracking["l_valid"].astype(int)
    df_eyetracking["r_valid"] = df_eyetracking["r_valid"].astype(int)

    df_eyetracking["l_miss_x"] = df_eyetracking.apply(lambda row: row["l_display_x"] < -opt["xres"] or row["l_display_x"] > 2 * opt["xres"], axis=1)
    df_eyetracking["l_miss_y"] = df_eyetracking.apply(lambda row: row["l_display_y"] < -opt["yres"] or row["l_display_y"] > 2 * opt["yres"], axis=1)
    df_eyetracking["r_miss_x"] = df_eyetracking.apply(lambda row: row["r_display_x"] < -opt["xres"] or row["r_display_x"] > 2 * opt["xres"], axis=1)
    df_eyetracking["r_miss_y"] = df_eyetracking.apply(lambda row: row["r_display_y"] < -opt["yres"] or row["r_display_y"] > 2 * opt["yres"], axis=1)

    df_eyetracking["l_miss"] = df_eyetracking.apply(lambda row: row["l_miss_x"] or row["l_miss_y"] or not row["l_valid"] >= 1, axis=1)
    df_eyetracking["r_miss"] = df_eyetracking.apply(lambda row: row["r_miss_x"] or row["r_miss_y"] or not row["r_valid"] >= 1, axis=1)

    df_eyetracking.loc[df_eyetracking["l_miss"], "l_display_x"] = opt["missingx"]
    df_eyetracking.loc[df_eyetracking["l_miss"], "l_display_y"] = opt["missingy"]
    df_eyetracking.loc[df_eyetracking["r_miss"], "r_display_x"] = opt["missingx"]
    df_eyetracking.loc[df_eyetracking["r_miss"], "r_display_y"] = opt["missingy"]

    df_eyetracking = df_eyetracking.drop(columns=["l_miss_x", "l_miss_y", "r_miss_x", "r_miss_y", "l_miss", "r_miss"])

    df_eyetracking.rename(columns={"l_display_x": "L_X",
                                   "l_display_y": "L_Y",
                                   "r_display_x": "R_X",
                                   "r_display_y": "R_Y",
                                   "l_valid" : "LValidity",
                                   "r_valid" : "RValidity"}, inplace=True)

    data = {}
    data["L_X"] = df_eyetracking["L_X"].to_numpy()
    data["L_Y"] = df_eyetracking["L_Y"].to_numpy()
    data["R_X"] = df_eyetracking["R_X"].to_numpy()
    data["R_Y"] = df_eyetracking["R_Y"].to_numpy()
    data["LValidity"] = df_eyetracking["LValidity"].to_numpy()
    data["RValidity"] = df_eyetracking["RValidity"].to_numpy()
    data["time"] = df_eyetracking["time"].to_numpy()

    fix, data, par = I2MC.I2MC(data, opt, logging=False)

    return fix, data, par
