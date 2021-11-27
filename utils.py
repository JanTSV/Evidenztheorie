import pandas as pd
from pathlib import Path


def load_data(paths: list):
    ret = {}

    for path in paths:
        if not (issubclass(type(path), Path) or isinstance(type(path), Path)):
            raise Exception("pathlib.Path objects needed.")
        ret.update({path.stem: pd.read_csv(str(path), delimiter=";", encoding='unicode_escape')})

    return ret


def comma_string_to_float(df: pd.DataFrame, key: str):
    df[key] = (df[key].str.replace(",", ".")).astype(float)


def change_data(data_dict: dict):
    for _, df in data_dict.items():
        # t als floats
        comma_string_to_float(df, "t")

        # Eigengeschwindigkeit(m/s) to floats
        comma_string_to_float(df, "Eigengeschwindigkeit(m/s)")

        # Abstand als float
        comma_string_to_float(df, "Abstand(m)")


def get_velocity(df: pd.DataFrame, dt=0.1):
    """
    Zeitabstand: 100ms
    Eigengeschwindigkeit
    Abstand
    """
    df["v(m/s)"] = 0.0

    for index, row in df.iterrows():
        if index == 0:
            continue
        old_distance = df.iloc[index - 1]["Abstand(m)"]
        delta_distance = row["Abstand(m)"] - old_distance
        df.loc[index, "v(m/s)"] = round(row["Eigengeschwindigkeit(m/s)"] + (delta_distance / dt), 2)
        
    df.loc[0, "v(m/s)"] = df.loc[1, "v(m/s)"]

    # In km/h
    df["v(km/h)"] = round(df["v(m/s)"] * 3.6, 2)


def get_acceleration(df: pd.DataFrame, dt=0.1):
    df["a(m/s^2)"] = 0.0

    for index, row in df.iterrows():
        if index == 0:
            continue
        delta_velocity = row["v(m/s)"] - df.iloc[index - 1]["v(m/s)"]
        print(row["v(m/s)"], df.iloc[index - 1]["v(m/s)"], delta_velocity)
        df.loc[index, "a(m/s^2)"] = round(delta_velocity / dt, 2)