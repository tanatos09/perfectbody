from django import forms
from products.models import ProductReview, TrainerReview

class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ['rating', 'comment']

class TrainerReviewForm(forms.ModelForm):
    class Meta:
        model = TrainerReview
        fields = ['rating', 'comment']
