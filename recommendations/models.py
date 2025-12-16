from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Movie(models.Model):
    title = models.CharField(max_length=200)
    genre = models.CharField(max_length=100, blank=True, null=True)
    release_year = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    poster_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title

class Rating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='ratings')
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie') # A user can only rate a movie once
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.movie.title} ({self.score})"