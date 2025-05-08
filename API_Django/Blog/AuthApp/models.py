from django.db import models
from django.contrib.auth.models import User

CATEGORY_CHOICES = [
    ('food', 'Food'),
    ('beauty', 'Beauty'),
    ('politics', 'Politics'),
    ('travel', 'Travel'),
    ('lifestyle', 'Lifestyle'),
]

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='auth_profile')
    categories = models.CharField(max_length=255, blank=True)  # Stored as comma-separated values
    image = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_categories_display(self):
        selected = self.categories.split(",")
        labels = dict(CATEGORY_CHOICES)
        return ", ".join([labels.get(cat.strip(), cat.strip()) for cat in selected if cat.strip()])

    def __str__(self):
        return f"{self.user.username}'s Profile"
