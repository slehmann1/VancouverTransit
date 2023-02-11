import unittest
import io, os
from vancouver_transit_analyzer.GTFSPoll import GTFSPoll, NextStop

DIR_PREPENDUM = f"{os.getcwd()}\\vancouver_transit_analyzer\\tests\\"


class test_GTFSPoll(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.load_files()

    def load_files(self):
        self.normal_trip_text = self._read_str_file(f"{DIR_PREPENDUM}tripsample.txt")
        self.cancelled_trip_text = self._read_str_file(
            f"{DIR_PREPENDUM}cancelledtripsample.txt", "utf-8"
        )
        self.poll_sample_text = self._read_str_file(f"{DIR_PREPENDUM}pollsample.txt")

    def _read_str_file(self, filename, encoding="utf-16"):
        f = io.open(filename, mode="r", encoding=encoding)
        result = f.read()
        f.close()
        return result

    def test_str_between_bounds(self):
        self.assertEqual(
            GTFSPoll.str_between_bounds("0123456789", "2", "5"), ("34", "6789")
        )
        self.assertEqual(
            GTFSPoll.str_between_bounds('"trip_id: "13373020"', '"trip_id: "', '"'),
            ("13373020", ""),
        )
        self.assertEqual(
            GTFSPoll.str_between_bounds('  route_id: "10232"', '  route_id: "', '"'),
            ("10232", ""),
        )
        self.assertEqual(
            GTFSPoll.str_between_bounds("Hello How Are You?", "Hello ", " Are You?"),
            ("How", "Are You?"),
        )
        self.assertEqual(
            GTFSPoll.str_between_bounds(self.normal_trip_text, 'trip_id: "', '"')[0],
            "13373020",
        )
        self.assertEqual(
            GTFSPoll.str_between_bounds(
                "Hello How Are You? I am well.", "Hello ", " Are You?"
            ),
            ("How", "Are You? I am well."),
        )
        with self.assertRaises(IndexError):
            GTFSPoll.str_between_bounds(
                "Hello How Are You?", "Hello ", "Cheese Crumpets"
            )

    def test_parse_trip(self):
        self.assertEqual(
            GTFSPoll.parse_trip(self.normal_trip_text),
            NextStop(
                trip_id=13373020,
                route_id=10232,
                stop_id=4491,
                delay=0,
                time=1675477260,
                skipped_stop=False,
            ),
        )

    def test_is_next_stop_skipped(self):
        self.assertEqual(GTFSPoll.is_next_stop_skipped(self.normal_trip_text), False)
        self.assertEqual(GTFSPoll.is_next_stop_skipped(self.cancelled_trip_text), True)

    def test_parse_poll(self):
        stops = GTFSPoll.parse_poll(self.poll_sample_text)
        self.assertEqual(len(stops), 4)

        self.assertEqual(
            stops[0],
            NextStop(
                trip_id=13373020,
                route_id=10232,
                stop_id=4491,
                delay=0,
                time=1675477260,
                skipped_stop=False,
            ),
        )
        self.assertEqual(
            stops[1],
            NextStop(
                trip_id=13344784,
                route_id=6620,
                stop_id=11251,
                delay=None,
                time=None,
                skipped_stop=True,
            ),
        )
        self.assertEqual(
            stops[2],
            NextStop(
                trip_id=13351500,
                route_id=11201,
                stop_id=11051,
                delay=126,
                time=1675477088,
                skipped_stop=False,
            ),
        )
        self.assertEqual(
            stops[3],
            NextStop(
                trip_id=13351590,
                route_id=11201,
                stop_id=11050,
                delay=175,
                time=1675477110,
                skipped_stop=False,
            ),
        )
