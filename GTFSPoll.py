from google.transit import gtfs_realtime_pb2
import urllib.request
import os
from dotenv import load_dotenv
from dataclasses import dataclass
from vancouver_transit_analyzer.models import DataPoint, Stop
from scripts import load_stops

load_dotenv()
API_KEY = os.environ["TRANSIT_API_KEY"]
DEBUG = os.environ["DEBUG"]
SKIP_POLL = False


class GTFSPoll:
    def __init__(self) -> None:
        print("Polling Data")
        self.poll()

    def poll(self):
        if not SKIP_POLL:
            feed = gtfs_realtime_pb2.FeedMessage()
            response = urllib.request.urlopen(
                f"https://gtfs.translink.ca/v2/gtfsrealtime?apikey={API_KEY}"
            )
            feed.ParseFromString(response.read())
            text = str(feed.entity)
        else:
            with open("gtfs_poll.txt", "r") as text_file:
                text = text_file.read()
        if DEBUG:
            with open("gtfs_poll.txt", "w") as text_file:
                text_file.write(text)

        self.stops = self.parse_poll(text)

    def build_model(self):
        """Updates the database with the self.stops objects
        """
        datapoints = []
        for next_stop in self.stops:
            try:
                stop = Stop.objects.get(stop_id=next_stop.stop_id)
                datapoints.append(
                    DataPoint(
                        stop=stop, delay=next_stop.delay, skipped=next_stop.skipped_stop
                    )
                )
            except Stop.DoesNotExist:
                # Update the stops
                load_stops.run(should_clear_database=False)


        print(f"Built {len(datapoints)} Datapoints")
        DataPoint.objects.bulk_create(datapoints)

    @staticmethod
    def parse_poll(text):
        """Parses text from a poll into a list of stops, where each stop is the next in each trip

        Args:
            text (strint): The text to be converted into ma list of stops

        Returns:
            list[Stop]: A list of stops where each stop is the next in each trip
        """
        trips = text.split("trip {")
        # First is blank
        trips = trips[1:]

        return [GTFSPoll.parse_trip(trip) for trip in trips]


    @staticmethod
    def parse_trip(trip_text):
        """Identifies the next stop in each trip

        Args:
            trip_text (string): Text representing a trip

        Returns:
            Stop: The next stop in the trip
        """
        trip_id, trip_text = GTFSPoll.str_between_bounds(trip_text, 'trip_id: "', '"')
        if not GTFSPoll.is_next_stop_skipped(trip_text):
            route_id, trip_text = GTFSPoll.str_between_bounds(
                trip_text, 'route_id: "', '"'
            )
            delay, trip_text = GTFSPoll.str_between_bounds(trip_text, "delay: ", "\n")
            time, trip_text = GTFSPoll.str_between_bounds(trip_text, "time: ", "\n")
            stop_id, _ = GTFSPoll.str_between_bounds(trip_text, 'stop_id: "', '"')
            return NextStop(
                int(trip_id), int(route_id), int(stop_id), int(delay), int(time)
            )
        else:
            route_id, trip_text = GTFSPoll.str_between_bounds(
                trip_text, 'route_id: "', '"'
            )
            stop_id, _ = GTFSPoll.str_between_bounds(trip_text, 'stop_id: "', '"')
            return NextStop(
                trip_id=int(trip_id),
                route_id=int(route_id),
                stop_id=int(stop_id),
                skipped_stop=True,
            )

    @staticmethod
    def is_next_stop_skipped(trip_text):
        """Identifies whether the next stop in the trip is skipped

        Args:
            trip_text (string): Text representing a trip

        Raises:
            ValueError: If the trip_text does not follow an expected format

        Returns:
            bool: True if the next stop is skipped
        """
        _, trip_text = GTFSPoll.str_between_bounds(trip_text, "stop_time_update {", "}")

        if "schedule_relationship: " not in trip_text:
            return False

        status, _ = GTFSPoll.str_between_bounds(
            trip_text, "schedule_relationship: ", "\n"
        )

        if status == "SKIPPED":
            return True

        raise ValueError("Unexpected text following schedule relationship")

    @staticmethod
    def str_between_bounds(text, left_delimiter, right_delimiter):
        """Returns the string between a left and a right delimiter

        Args:
            text (String): The text to be searched
            left_delimiter (String): The left delimiter
            right_delimiter (String): The right delimiter

        Raises:
            IndexError: If one of the left or right delimiters is not found

        Returns:
            [String: Text between the left and the right delimiters String: Text beyond the right delimiter]
        """

        l_index = text.find(left_delimiter) + len(left_delimiter)
        r_index = text[l_index:].find(right_delimiter) + l_index

        if l_index < len(left_delimiter) - 1 or r_index < l_index:
            text = f"Delimeters {left_delimiter}, index {l_index}, {right_delimiter}, index {r_index} not found within text"
            print(f"{l_index - len(left_delimiter)}, {len(left_delimiter)}")
            print(r_index - l_index)
            raise IndexError(text)

        return text[l_index:r_index], text[r_index + 1 :]


@dataclass
class NextStop:
    trip_id: int
    route_id: int
    stop_id: int
    delay: int = None
    time: int = None
    skipped_stop: bool = False