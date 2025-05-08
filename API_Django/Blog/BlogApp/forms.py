from django import forms

class TravelForm(forms.Form):
    destination = forms.CharField(label="Destination", max_length=100)
    experience = forms.CharField(label="Your Travel Experience", widget=forms.Textarea)
    recommendations = forms.CharField(label="Recommendations", widget=forms.Textarea)
    would_visit_again = forms.ChoiceField(
        label="Would you visit again?",
        choices=[('yes', 'Yes'), ('no', 'No')],
        widget=forms.RadioSelect
    )

class FoodForm(forms.Form):
    dish_name = forms.CharField(label="Dish Name", max_length=100)
    recipe = forms.CharField(label="Recipe", widget=forms.Textarea)
    ingredients = forms.CharField(label="Ingredients", widget=forms.Textarea)
    is_vegetarian = forms.ChoiceField(
        label="Is it vegetarian?",
        choices=[('yes', 'Yes'), ('no', 'No')],
        widget=forms.Select
    )

class BeautyForm(forms.Form):
    beauty_tips = forms.CharField(label="Beauty Tips", widget=forms.Textarea)
    product_recommendations = forms.CharField(label="Product Recommendations", widget=forms.Textarea)
    skincare_type = forms.ChoiceField(
        label="Skin Type", 
        choices=[('dry', 'Dry'), ('oily', 'Oily'), ('combination', 'Combination')],
        widget=forms.RadioSelect
    )

class PoliticsForm(forms.Form):
    political_issue = forms.CharField(label="Political Issue", max_length=100)
    opinion = forms.CharField(label="Your Opinion", widget=forms.Textarea)
    suggestions = forms.CharField(label="Suggestions for Change", widget=forms.Textarea)
    agree_with_policy = forms.ChoiceField(
        label="Do you agree with current policy?",
        choices=[('yes', 'Yes'), ('no', 'No')],
        widget=forms.Select
    )

class HealthyLifestyleForm(forms.Form):
    exercise_routine = forms.CharField(label="Exercise Routine", widget=forms.Textarea)
    healthy_meals = forms.CharField(label="Healthy Meals", widget=forms.Textarea)
    wellness_tips = forms.CharField(label="Wellness Tips", widget=forms.Textarea)
    sleeps_early = forms.ChoiceField(
        label="Do you sleep before 10 PM?",
        choices=[('yes', 'Yes'), ('no', 'No')],
        widget=forms.Select
    )
