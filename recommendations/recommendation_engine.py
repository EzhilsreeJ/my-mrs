from .models import Movie, Rating
from django.contrib.auth import get_user_model
from collections import defaultdict
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

User = get_user_model()

class RecommendationEngine:
    def __init__(self):
        self.users = User.objects.all()
        self.movies = Movie.objects.all()
        self.ratings = Rating.objects.all()
        self.user_item_matrix = None
        self.movie_ids = []
        self.user_ids = []
        self._build_matrix()

    def _build_matrix(self):
        """Builds the user-item rating matrix."""
        self.movie_ids = [movie.id for movie in self.movies]
        self.user_ids = [user.id for user in self.users]
        num_users = len(self.users)
        num_movies = len(self.movies)

        # Initialize matrix with zeros (or NaN if preferred, but zeros are simpler for this example)
        self.user_item_matrix = np.zeros((num_users, num_movies))

        # Map movie and user IDs to matrix indices
        movie_id_to_index = {movie_id: i for i, movie_id in enumerate(self.movie_ids)}
        user_id_to_index = {user_id: i for i, user_id in enumerate(self.user_ids)}

        # Populate the matrix with ratings
        for rating in self.ratings:
            try:
                user_idx = user_id_to_index[rating.user_id]
                movie_idx = movie_id_to_index[rating.movie_id]
                self.user_item_matrix[user_idx, movie_idx] = rating.score
            except KeyError:
                # This might happen if a user or movie was deleted after ratings were created
                # or if IDs are not contiguous. For this example, we'll ignore such cases.
                pass

    def get_user_recommendations(self, user_id, num_recommendations=5):
        """
        Generates movie recommendations for a specific user using collaborative filtering.
        """
        try:
            user_idx = self.user_ids.index(user_id)
        except ValueError:
            return [] # User not found

        # Get the row for the target user
        user_ratings = self.user_item_matrix[user_idx, :]

        # If the user has not rated any movies, we can't make personalized recommendations
        if np.all(user_ratings == 0):
            return []

        # Calculate similarity between the target user and all other users
        # We transpose the matrix for user-user similarity calculation
        user_similarities = cosine_similarity(self.user_item_matrix, np.atleast_2d(user_ratings))

        # Remove self-similarity
        user_similarities[user_idx] = -1 # Set self-similarity to a low value to exclude

        # Get the indices of the most similar users
        # We are interested in users who have rated some movies similarly
        # A more robust approach would filter users by having rated at least one common movie with the target user.
        # For simplicity here, we just take top K similar users.
        similar_user_indices = np.argsort(user_similarities.flatten())[::-1]

        # Get movies rated by the target user (to exclude them from recommendations)
        rated_movie_indices = np.where(user_ratings > 0)[0]

        recommendations = {}

        # Iterate through similar users and collect potential recommendations
        for sim_user_idx in similar_user_indices:
            # If we have enough recommendations, stop
            if len(recommendations) >= num_recommendations:
                break

            # Get movies rated by this similar user but NOT by the target user
            sim_user_ratings = self.user_item_matrix[sim_user_idx, :]
            unrated_movie_indices = np.where((sim_user_ratings > 0) & (~np.isin(np.arange(len(sim_user_ratings)), rated_movie_indices)))[0]

            for movie_idx in unrated_movie_indices:
                if len(recommendations) >= num_recommendations:
                    break

                # Calculate a predicted score for the unrated movie
                # This is a simplified approach: weighted average of similar users' ratings for this movie.
                # A more complex approach could consider only users with high similarity.
                # For now, we'll just add the movie if it's not already considered.
                movie_id = self.movie_ids[movie_idx]
                # We can use the similarity score as a weight for a more sophisticated prediction,
                # but for simply ranking potential recommendations, we can count how many similar users
                # rated this movie positively.
                # A simple approach: add movie to recommendations if not already rated by target user.
                recommendations[movie_id] = recommendations.get(movie_id, 0) + user_similarities[sim_user_idx, 0] # Using similarity score as a "boost"

        # Sort recommendations by their "boost" score
        sorted_recommendations = sorted(recommendations.items(), key=lambda item: item[1], reverse=True)

        # Get movie objects for the top recommendations
        recommended_movie_ids = [movie_id for movie_id, score in sorted_recommendations[:num_recommendations]]
        recommended_movies = Movie.objects.filter(id__in=recommended_movie_ids).order_by('title') # Order for consistency

        return recommended_movies

    def get_similar_movies(self, movie_id, num_similar=5):
        """
        Finds movies similar to a given movie using content-based or collaborative filtering.
        For simplicity, this example uses a simplified collaborative filtering approach:
        find movies that are often rated similarly by the same users.
        """
        try:
            movie_idx = self.movie_ids.index(movie_id)
        except ValueError:
            return []

        # Calculate similarity between movies based on user ratings
        # Transpose the matrix to get movie-movie similarity
        movie_similarities = cosine_similarity(self.user_item_matrix.T, np.atleast_2d(self.user_item_matrix[:, movie_idx]))

        # Remove self-similarity
        movie_similarities[movie_idx] = -1

        # Get the indices of the most similar movies
        similar_movie_indices = np.argsort(movie_similarities.flatten())[::-1]

        # Get movie objects for the most similar movies
        similar_movie_ids = [self.movie_ids[i] for i in similar_movie_indices[:num_similar]]
        similar_movies = Movie.objects.filter(id__in=similar_movie_ids).order_by('title')

        return similar_movies