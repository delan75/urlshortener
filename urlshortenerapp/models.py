from django.db import models
from hashids import Hashids

def generateShortUrlFromId(id):
    return Hashids(salt="urlshortenerapp", min_length=5).encode(id)

class UrlModel(models.Model):
    longUrl = models.CharField(max_length=23000)
    shortUrl = models.CharField(max_length=10)
    visitorIp = models.GenericIPAddressField(blank=True, null=True)
    completeUrl = models.URLField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    
    def save(self, *args, **kwargs):
        if not self.pk: 
            super().save(*args, **kwargs)
        
        self.shortUrl = generateShortUrlFromId(self.id)
        
        kwargs.pop('force_insert', None)
        kwargs.pop('force_update', None)
        super().save(*args, **kwargs) 