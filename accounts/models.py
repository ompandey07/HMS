from django.db import models
from django.utils import timezone
import pytz

KATHMANDU_TZ = pytz.timezone('Asia/Kathmandu')

class SubscriptionModel(models.Model):
    sub_owner_name = models.CharField(max_length=255)
    sub_address = models.TextField()
    sub_pan = models.CharField(max_length=50)
    sub_mobile_no = models.CharField(max_length=20)
    sub_email_address = models.EmailField()
    sub_is_active = models.BooleanField(default=False)
    sub_starting_at = models.DateTimeField(default=timezone.now)
    sub_ending_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if self.sub_starting_at:
            self.sub_starting_at = self.sub_starting_at.astimezone(KATHMANDU_TZ)
        if self.sub_ending_at:
            self.sub_ending_at = self.sub_ending_at.astimezone(KATHMANDU_TZ)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.sub_owner_name} - {self.sub_email_address}"
