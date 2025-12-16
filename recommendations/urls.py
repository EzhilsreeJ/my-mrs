from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    path('movies/', views.movie_list, name='movie_list'),
    path('movies/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('recommendations/', views.user_recommendations, name='user_recommendations'),
    path('similar-movies/<int:movie_id>/', views.similar_movies, name='similar_movies'),
]