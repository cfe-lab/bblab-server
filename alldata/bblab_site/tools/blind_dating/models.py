from django.conf import settings
from django.db import models
import os

# Create your models here.

class DatingOutput(models.Model):
    script = models.FileField(upload_to=settings.DATING_OUT)

    @property
    def script_path(self):
        return os.path.basename(self.script.name)