from django import forms
from .models import Rating

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['score'] # Only allow user to change the score

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize widget for score to be a radio button or select dropdown
        # For simplicity, using default IntegerField widget which is a number input.
        # A better UX would use stars or radio buttons.
        self.fields['score'].widget = forms.Select(choices=[(i, i) for i in range(1, 6)])