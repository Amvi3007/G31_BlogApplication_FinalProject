from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Blog(models.Model):
    blog_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    upload_image = models.ImageField(upload_to='FunctionalityApp/static/', blank=True, null=True)
    category = models.CharField(max_length=100)
    liked_by = models.ManyToManyField(User, related_name='liked_blogs', blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def like_count(self):
        return self.liked_by.count()

    def __str__(self):
        return self.title

class Comment(models.Model):
    blog = models.ForeignKey(Blog, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} on {self.blog.title}'
