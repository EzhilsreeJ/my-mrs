from django.contrib import admin
from .models import Movie, Rating

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'genre', 'release_year')
    search_fields = ('title', 'genre')

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'score', 'created_at')
    list_filter = ('score', 'created_at')
    search_fields = ('user__username', 'movie__title')