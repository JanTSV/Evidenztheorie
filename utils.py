from pathlib import Path

import pandas as pd
import numpy as np


def check_dataframe(df: pd.DataFrame, keys: list, name: str = ""):
    """
    Check if df contains all keys as columns.
    
    Args:
        df: Dataframe to check.
        keys: List of keys to check df for.
    """
    if not all([x in df.columns for x in keys]):
        raise KeyError(F"{keys} not defined in DataFrame {name}")


def load_data(paths: list) -> dict:
    """
    Load CSV data from a list of paths and merge them into a dict.
    
    Args:
        paths (list): List of paths to CSV files.
       
    Returns:
        dict: Dict containing all read CSV files.
    """
    ret = {}

    for path in paths:
        if not (issubclass(type(path), Path) or isinstance(type(path), Path)):
            raise Exception("pathlib.Path objects needed.")
        ret.update({path.stem: pd.read_csv(str(path), delimiter=";", encoding='unicode_escape')})

    return ret


def comma_string_to_float(df: pd.DataFrame, key: str):
    """
    Convert a string to a float. Replace German ',' with a '.'.
    
    Args:
        df (pd.DataFrame): Dataframe of sensor data.
    """
    check_dataframe(df, [key])
    df[key] = (df[key].str.replace(",", ".")).astype(float)


def change_data(data_dict: dict):
    """
    Convert the following string-valued columns to floats:
        * t
        * Eigengeschwindigkeit(m/s)
        * Abstand(m)
    
    Args:
        data_dict (dict): Data dict with all sensor data.
    """
    for name, df in data_dict.items(): 
        check_dataframe(df, ["t", "Eigengeschwindigkeit(m/s)", "Abstand(m)"], name)
                    
        # Convert t
        comma_string_to_float(df, "t")

        # Convert Eigengeschwindigkeit(m/s)
        comma_string_to_float(df, "Eigengeschwindigkeit(m/s)")

        # Convert Abstand(m)
        comma_string_to_float(df, "Abstand(m)")


def get_velocity(df: pd.DataFrame):
    """
    Calculate velocity in km/h of vehicle measured by sensors.
    The following method is applied:
        1. Derive distance over time -> distance_model.
        2. Calculate velocity_model with distance_model and "Eigengeschwindigkeit(m/s)"
        
    Notice:
        If own vehicle accelerates more, float(np.mean(df["Eigengeschwindigkeit(m/s)"])) has to be updated.
        
    Args:
        df : Dataframe with sensor data.
    """
    velocity_key = "v(km/h)"
    distance_model = np.poly1d(np.polyfit(df["t"], df["Abstand(m)"], 3))

    df[velocity_key] = distance_model.deriv()(df["t"].copy())
    # Optimize calculated velocity, as it is scattered
    velocity_model = np.poly1d(np.polyfit(df["t"].copy(), df[velocity_key], 3))
    own_velocity = float(np.mean(df["Eigengeschwindigkeit(m/s)"]))
    for index, row in df.iterrows():
        df.loc[index, velocity_key] += own_velocity
        df.loc[index, velocity_key] = df[velocity_key][index] * 3.6
        
    return velocity_model, distance_model
    

def get_acceleration(df: pd.DataFrame, model):
    """
    Calculate the acceleration in km/h^2 of a dataframe by deriving the model for its velocity.
    
    Args:
        df: Dataframe containing sensor data.
        model: Model of velocity.
    """
    check_dataframe(df, ["t"])
    df["a(km/h^2)"] = model.deriv()(df["t"])


def save_data_dict(data_dict: dict, folder: Path):
    """
    Save all data of data_dict to a folder as CSV files.
    
    Args:
        data_dict: Dict with all data.
        folder: Parent folder to save files too.
    """
    for path, df in data_dict.items():
        p = folder.joinpath(F"{path}.csv")
        df.to_csv(p, sep=";")


def get_dimensions(df: pd.DataFrame):
    """
    Calculate dimensions (width and height) of the measured vehicle.
    With the formulae: width = (distance + measured width) / 2 a value proportional to meters is calculated.
    
    Args:
        df: Dataframe with sensor data.
    """
    check_dataframe(df, ["Abstand(m)", "Bbox_Breite", "Bbox_Höhe"])
    df["width"] = (df["Abstand(m)"] + (df["Bbox_Breite"] / 2)) / 100
    df["height"] = (df["Abstand(m)"] + (df["Bbox_Höhe"] / 2)) / 100
    
    
def get_max_range_by_criterion(arr: list, criterion):
    """
    Get maximal number of elements fullfilling criterion in arr in a row.
    """
    scope = 0
    return_value = 0
    left_selected = False
    for element in arr:
        if criterion(element):
            scope += 1
            left_selected = True
        if (not criterion(element)) and left_selected:
            if scope > return_value:
                return_value = scope
            left_selected = False
    if scope > return_value:
                return_value = scope
    return return_value


def get_acceleration_limit(data_dict: dict, limit: float):
    """
    Determines upper and lower limit of acceleration values, to
    check whether a vehicle has a high acceleration
    """
    all_accelerations = []
    for _, df in data_dict.items():
        df_a = df["a(km/h^2)"]
        for acc in df_a.iloc[:]:
            if acc > 85:
                print(_)
            # append absolute value of acceleration to acceleration list
            all_accelerations.append(abs(acc))
    # return the requested percentile
    return np.percentile(sorted(all_accelerations), [limit*100])[0]


def calculate_weighted_ratio(heights, widths, distances) -> float:
    """
    Calculate mean ratio of height and width with weighing in distances.
    Method:
        * < 33%     -> 0.5
        * 33% < 66% -> 0.3
        * > 66%     -> 0.2
        
    
    Args:
        heights: Heights.
        Widths: Widths.
        distances: Distances.
        
    Returns:
        float: Wighted ratio.
    """
    
    # Percentiles of distances
    lower, upper = np.percentile(sorted(distances), [33, 66])
    
    # lower, middle, high distances
    weighted_widths = [[], [], []]
    weighted_heights = [[], [], []]
    for ix, distance in enumerate(distances):
        if distance < lower:
            weighted_widths[0].append(widths.iloc[ix])
            weighted_heights[0].append(heights.iloc[ix])
        elif distance > lower and distance < upper:
            weighted_widths[1].append(widths.iloc[ix])
            weighted_heights[1].append(heights.iloc[ix])
        else:
            weighted_widths[2].append(widths.iloc[ix])
            weighted_heights[2].append(heights.iloc[ix])
            
    width = np.mean(weighted_widths[0]) * 0.5 + np.mean(weighted_widths[1]) * 0.3 + np.mean(weighted_widths[2]) * 0.2
    height = np.mean(weighted_heights[0]) * 0.5 + np.mean(weighted_heights[1]) * 0.3 + np.mean(weighted_heights[2]) * 0.2
    return height / width
    
        