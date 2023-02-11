from django.shortcuts import render
from django.views import View
from vancouver_transit_analyzer.models import Stop, DataPoint
from vancouver_transit_analyzer.GTFSPoll import GTFSPoll
import json
import datetime
from collections import namedtuple
from django.db.models import Q
from scripts import load_stops
import django.http


class Map(View):
    _peak_hours = namedtuple(
        "peak_hours",
        "morning_peak_start morning_peak_end afternoon_peak_start afternoon_peak_end",
    )
    _PEAK_HOURS = _peak_hours(
        morning_peak_start=6,
        morning_peak_end=9,
        afternoon_peak_start=15,
        afternoon_peak_end=18,
    )

    def get(self, request):
        disp_data = request.GET.get("disp_data", "All")
        disp_times = request.GET.get("disp_times", "All")
        start_date = request.GET.get("start_date", "2023-01-01")
        end_date = request.GET.get("end_date", "2023-01-01")

        context = self.build_context(disp_data, disp_times, start_date, end_date)
        print(f"PROVIDING {len(context)} Datapoints")
        return render(
            request,
            "vancouver_transit_analyzer/map.html",
            {"data": json.dumps(context)},
        )

    def build_context(self, disp_data, disp_times, start_date, end_date):
        context = []
        datapoints_query = DataPoint.objects.all()

        if disp_data == "Between":
            # Limit between start/end dates
            datapoints_query = datapoints_query.filter(
                date__gte=datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
            )
            datapoints_query = datapoints_query.filter(
                date__lte=datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
            )

        if disp_times == "Peak":
            # Limit to weekdays
            # datapoints_query = datapoints_query.exclude(date__week_day=1)
            # datapoints_query = datapoints_query.exclude(date__week_day=7)

            # Limit to peak hours
            datapoints_query = datapoints_query.filter(
                (
                    (
                        Q(time__hour__gte=self._PEAK_HOURS.morning_peak_start)
                        & Q(time__hour__lte=self._PEAK_HOURS.morning_peak_end)
                    )
                    | (
                        Q(time__hour__gte=self._PEAK_HOURS.afternoon_peak_start)
                        & Q(time__hour__lte=self._PEAK_HOURS.afternoon_peak_end)
                    )
                )
            )

        for stop in Stop.objects.all():
            try:
                datapoints = datapoints_query.filter(stop=stop)
                if len(datapoints) == 0:
                    continue
                context.append(
                    {
                        "Lat": stop.latitude,
                        "Lon": stop.longitude,
                        "Name": stop.stop_name,
                        "Type": stop.stop_type.name,
                        "Value": self.average_delay(datapoints),
                    }
                )
            except DataPoint.DoesNotExist:
                # TODO: Pull new data, maybe translink has added a stop
                # This stop is not in the dataset
                #load_stops.run(False)
                print("Loaded Further Stops")
                continue
        return context

    def average_delay(self, datapoints):
        """Computes the arithmetic mean of the delay of a list of model.DataPoint

        Args:
            datapoints ([DataPoint]): List of model.DataPoint

        Returns:
            float: Arithmetic mean delay
        """
        delay_sum = 0
        count = 0
        for datapoint in datapoints:
            if datapoint.delay is None:
                continue
            delay_sum += datapoint.delay
            count += 1

        return None if count == 0 else delay_sum / len(datapoints)
