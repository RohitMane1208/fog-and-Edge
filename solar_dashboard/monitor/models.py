from django.db import models


class SolarReading(models.Model):

    panel_id = models.CharField(max_length=50)

    voltage = models.FloatField()
    current = models.FloatField()

    temperature = models.FloatField()
    light_intensity = models.IntegerField()
    humidity = models.FloatField()

    power_watt = models.FloatField()

    local_alert = models.BooleanField(default=False)

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.panel_id} - {self.power_watt}W"