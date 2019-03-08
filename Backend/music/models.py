from django.db import models

# Create your models here.
class Album(models.Model):
    Title = models.CharField(max_length=50)
    Artist = models.CharField(max_length=30)
    Year = models.IntegerField()

    def __str__(self):
        return self.Artist


class Song(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    file_type = models.CharField(max_length=10)
    def __str__(self):
        return self.title