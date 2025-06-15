from django.db import models

class ShortURL(models.Model):
    code = models.CharField(max_length=20, unique=True)
    target_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code
