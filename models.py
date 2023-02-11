from django.db import models


class StopType(models.Model):
    name = models.CharField(max_length=20, blank=False, null=False)

    def __str__(self) -> str:
        return self.name


class Stop(models.Model):
    stop_id = models.IntegerField(blank=False, null=False)
    latitude = models.FloatField(blank=False, null=False)
    longitude = models.FloatField(blank=False, null=False)
    stop_name = models.CharField(max_length=60, blank=False, null=False)
    stop_type = models.ForeignKey(
        StopType, on_delete=models.CASCADE, blank=False, null=False
    )

    def __str__(self) -> str:
        return f"{self.stop_type}, {self.stop_name}"

class DataPoint(models.Model):
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE, blank=False, null= False)
    delay = models.IntegerField(null = True)
    time = models.TimeField(auto_now=True)
    date = models.DateField(auto_now=True)
    skipped = models.BooleanField(default= False)