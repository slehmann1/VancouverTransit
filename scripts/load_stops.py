import os
from dotenv import load_dotenv
from dataclasses import dataclass
import shutil
import urllib.request
import zipfile
import pandas as pd
from vancouver_transit_analyzer.models import StopType, Stop
from django.db import transaction

_TEMP_LOC = "/temp"

_DOWNLOAD_LINK = (
    "https://gtfs-static.translink.ca/gtfs/History/2023-02-10/google_transit.zip"
)
_ZIP_NAME = "google_transit.zip"
_KEEP_NAME = "stops.txt"
_CSV_NAME = "stops.csv"
_STOP_TYPES = ["Bus", "SkyTrain", "West Coast Express", "SeaBus"]
_stop_types_dict = {}
# TODO: VERIFY THESE IDS
_SEABUS_IDS = [12034, 99958]


def run(should_clear_database=True):
    if should_clear_database:
        clear_database()
    build_stop_types()
    df = get_stops_df()
    build_stops(df)


def clear_database():
    Stop.objects.all().delete()
    StopType.objects.all().delete()


def build_stop_types():
    global _stop_types_dict
    _stop_types_dict = {
        stop_type: StopType(name=stop_type) for stop_type in _STOP_TYPES
    }
    StopType.objects.bulk_create(_stop_types_dict.values())
    print("Built Stop Types")


def build_stops(df):
    global _stop_types_dict
    stops_list = []
    for _, row in df.iterrows():
        if row["zone_id"] == "BUS ZN":
            stop_type = _stop_types_dict["Bus"]
        elif "WCE" in row["zone_id"]:
            stop_type = _stop_types_dict["West Coast Express"]
        elif row["stop_id"] in _SEABUS_IDS:
            stop_type = _stop_types_dict["SeaBus"]
        else:
            stop_type = _stop_types_dict["SkyTrain"]

        stops_list.append(
            Stop(
                stop_id=row["stop_id"],
                latitude=row["stop_lat"],
                longitude=row["stop_lon"],
                stop_name=row["stop_name"],
                stop_type=stop_type,
            )
        )
    update_database(stops_list)


@transaction.atomic
def update_database(stops_list):
    for stop in stops_list:
        Stop.objects.get_or_create(
            stop_id=stop.stop_id,
            latitude=stop.latitude,
            longitude=stop.longitude,
            stop_name=stop.stop_name,
            stop_type=stop.stop_type,
        )

    print(f"Built {len(stops_list)} Stops")


def int_or_none(row, column):
    """Checks a dataframe at the column specified for an integer value. If a non-integer value is found, None is returned

    Args:
        row (pd.Dataframe): A row of a pandas dataframe
        column (str): The name of the column containing the desired value

    Returns:
        None or int: If the value is an int, it is returned. If it is not an int, None is returned.
    """
    try:
        return int(row[column])
    except ValueError:
        return None


def get_stops_df():
    """Downloads a stops csv file and returns it as a dataframe

    Returns:
        PD.DataFrame: A stops.csv file as a dataframe
    """
    # Delete csv if it already exists
    if os.path.isfile(_CSV_NAME):
        os.remove(_CSV_NAME)

    download_csv(
        _DOWNLOAD_LINK,
        _ZIP_NAME,
        _KEEP_NAME,
        _CSV_NAME,
        False,
    )
    return pd.read_csv(_CSV_NAME)


def download_csv(url, zip_filename, keep_file, filename, remove_first_line=False):
    """
    Downloads a CSV file from statistics canada
    :param url: The URL of the csv file to download
    :param zip_filename: The name of the zip file to extract from
    :param keep_file: The file that should be kept from the zip file
    :param filename: The final filename that the csv should be saved as
    :param remove_first_line: Should the first line of the CSV be removed? Some CSVs have an additional header text
    :return: None
    """
    # Create a temporary directory
    loc = os.path.join(os.getcwd() + _TEMP_LOC + "/")
    os.mkdir(loc)

    # Download the file as a zip file and extract it
    print(f"Start file download at this URL: {url}")
    urllib.request.urlretrieve(url, loc + zip_filename)
    print("Download complete")
    with zipfile.ZipFile(loc + zip_filename, "r") as zip_ref:
        zip_ref.extractall(loc)

    # Rename/move the file of interest and delete the temporary directory
    shutil.move(loc + keep_file, os.getcwd() + "/" + filename)
    shutil.rmtree(loc)

    # Sometimes the first line has to be removed due to additional header text
    if remove_first_line:
        with open(filename, "r") as fin:
            data = fin.read().splitlines(True)
        with open(filename, "w") as fout:
            fout.writelines(data[1:])
