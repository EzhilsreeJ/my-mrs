from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Movie, Rating
from .recommendation_engine import RecommendationEngine
from .forms import RatingForm

def movie_list(request):
    """Displays a list of all available movies."""
    movies = Movie.objects.all().order_by('title')
    return render(request, 'recommendations/movie_list.html', {'movies': movies})

def movie_detail(request, movie_id):
    """Displays details of a specific movie and allows users to rate it."""
    movie = get_object_or_404(Movie, id=movie_id)
    rating = None
    if request.user.is_authenticated:
        try:
            rating = Rating.objects.get(user=request.user, movie=movie)
        except Rating.DoesNotExist:
            pass

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('users:login') # Redirect to login if not authenticated

        form = RatingForm(request.POST, instance=rating)
        if form.is_valid():
            rating_instance = form.save(commit=False)
            rating_instance.user = request.user
            rating_instance.movie = movie
            rating_instance.save()
            messages.success(request, 'Your rating has been saved!')
            return redirect('recommendations:movie_detail', movie_id=movie_id)
    else:
        form = RatingForm(instance=rating)

    context = {
        'movie': movie,
        'rating_form': form,
        'current_rating': rating.score if rating else None,
    }
    return render(request, 'recommendations/movie_detail.html', context)

@login_required
def user_recommendations(request):
    """Displays personalized movie recommendations for the logged-in user."""
    engine = RecommendationEngine()
    recommendations = engine.get_user_recommendations(request.user.id)

    if not recommendations:
        messages.info(request, "Not enough rating data to generate recommendations yet. Rate more movies!")
        # Optionally, suggest popular movies or new releases
        popular_movies = Movie.objects.order_by('-id')[:10] # Simple placeholder for now
        return render(request, 'recommendations/no_recommendations.html', {'popular_movies': popular_movies})


    context = {
        'recommendations': recommendations
    }
    return render(request, 'recommendations/user_recommendations.html', context)

def similar_movies(request, movie_id):
    """Displays movies similar to a given movie."""
    movie = get_object_or_404(Movie, id=movie_id)
    engine = RecommendationEngine()
    similar = engine.get_similar_movies(movie_id)

    context = {
        'movie': movie,
        'similar_movies': similar
    }
    return render(request, 'recommendations/similar_movies.html', context)