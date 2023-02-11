import pandas as pd
from vancouver_transit_analyzer.models import Stop, StopType
from scripts import load_stops
from django.test import TestCase
import os


class test_GTFSPoll(TestCase):
    _TEMP_LOC = "\\temp"
    DIR_PREPENDUM = f"{os.getcwd()}\\vancouver_transit_analyzer\\tests\\"

    _DOWNLOAD_LINK = (
        "https://gtfs-static.translink.ca/gtfs/History/2023-02-03/google_transit.zip"
    )

    def test_clear_database(self):
        StopType.objects.create(name="Dummy")
        load_stops.clear_database()
        self.assertEqual(len(StopType.objects.all()), 0)

    def test_int_or_none(self):
        df = pd.DataFrame.from_dict({"Fruit": [1], "Vegetables": [5.2], "Meat": [""]})
        self.assertEqual(load_stops.int_or_none(df, "Fruit"), 1)
        self.assertEqual(load_stops.int_or_none(df, "Vegetables"), 5)
        self.assertEqual(load_stops.int_or_none(df, "Meat"), None)

    def test_download_csv(self):
        # Delete csv if it already exists
        if os.path.isfile("stops.csv"):
            os.remove("stops.csv")

        load_stops.download_csv(
            self._DOWNLOAD_LINK, "google_transit.zip", "stops.txt", "stops.csv"
        )
        df = pd.read_csv("stops.csv")
        self.assertEqual(df.iloc[0, 1], 50001)
        self.assertEqual(df.iloc[1, 2], "Northbound No. 5 Rd @ McNeely Dr")
        os.remove("stops.csv")

    def test_build_stop_types(self):
        load_stops.clear_database()
        load_stops.build_stop_types()
        self.assertEqual(len(StopType.objects.all()), len(load_stops._STOP_TYPES))

        for stop_type in load_stops._STOP_TYPES:
            self.assertEqual(StopType.objects.get(name=stop_type).name, stop_type)
            self.assertEqual(load_stops._stop_types_dict[stop_type].name, stop_type)

    def test_build_stops(self):
        load_stops.clear_database()
        df = pd.read_csv(f"{self.DIR_PREPENDUM}samplestops.csv")
        load_stops.build_stop_types()
        load_stops.build_stops(df)
        self.assertEqual(len(Stop.objects.all()), 8)
        self.assertEqual(
            Stop.objects.get(latitude=49.286458).stop_name,
            "Westbound Davie St @ Bidwell St",
        )
        self.assertEqual(Stop.objects.get(latitude=49.179962).stop_id, 10000)
        self.assertEqual(Stop.objects.get(longitude=-123.091448).stop_code, 59324)
        self.assertEqual(
            Stop.objects.get(stop_name="Southbound No. 5 Rd @ Cambie Rd").stop_type,
            StopType.objects.get(name="Bus"),
        )
        self.assertEqual(
            Stop.objects.get(stop_name="King George Station").stop_type,
            StopType.objects.get(name="SkyTrain"),
        )
        self.assertEqual(
            Stop.objects.get(stop_name="Mission City Station").stop_type,
            StopType.objects.get(name="West Coast Express"),
        )
        self.assertEqual(
            Stop.objects.get(stop_name="Lonsdale Quay Station").stop_type,
            StopType.objects.get(name="SeaBus"),
        )
