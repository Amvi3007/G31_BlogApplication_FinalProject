from django import forms
from .models import Blog

class BlogForm(forms.ModelForm):
    CATEGORY_CHOICES = [
        ('Food', 'Food'),
        ('Beauty', 'Beauty'),
        ('Politics', 'Politics'),
        ('Travel', 'Travel'),
        ('Lifestyle', 'Lifestyle'),
    ]

    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    upload_image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control-file',
        })
    )

    class Meta:
        model = Blog
        fields = ['title', 'content', 'upload_image', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # No custom template is set now


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)


from django import forms

# Choices for dropdown and checkboxes
CATEGORY_CHOICES = [
    ('bug', 'Bug Report'),
    ('feature', 'Feature Request'),
    ('general', 'General Feedback'),
    ('ui/ux feedback','UI/UX Feedback'),
    ('other','Other')
]

INTEREST_CHOICES = [
    ('travel', 'Travel'),
    ('politics', 'Politics'),
    ('healthy_lifestyle', 'Healthy Lifestyle'),
    ('beauty', 'Beauty'),
    ('food', 'Food'),
]

class FeedbackForm(forms.Form):
    feedback_category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        label='Feedback Category'
    )
    improvement = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        label='What can we improve?'
    )
    topic_interest = forms.MultipleChoiceField(
        choices=INTEREST_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label='Topics you are interested in'
    )
    
    # Updated "Would you recommend us?" to be a radio button
    recommend = forms.ChoiceField(
        choices=[('yes', 'Yes'), ('no', 'No')],
        widget=forms.RadioSelect,
        required=False,
        label='Would you recommend us?'
    )

    user_experience = forms.IntegerField(
        min_value=1,
        max_value=10,
        label='Rate your experience (1–10)'
    )
