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
    name = "v(m/s)"
    df[name] = 0.0

    for index, row in df.iterrows():
        if index == 0:
            continue
        old_distance = df.iloc[index - 1]["Abstand(m)"]
        delta_distance = row["Abstand(m)"] - old_distance
        own_velocity = (df.iloc[index - 1]["Eigengeschwindigkeit(m/s)"] + row["Eigengeschwindigkeit(m/s)"]) / 2
        df.loc[index, name] = round(own_velocity + (delta_distance / dt), 2)

    df.loc[0, name] = df.loc[1, name]

    # In km/h
    df[F"v(km/h)"] = round(df[name] * 3.6, 2)


def get_acceleration(df: pd.DataFrame, model):
    df["a(km/h^2)"] = model.deriv()(df["t"])


def save_data_dict(data_dict: dict, folder: Path):
    for path, df in data_dict.items():
        p = folder.joinpath(F"{path}.csv")
        df.to_csv(p, sep=";")