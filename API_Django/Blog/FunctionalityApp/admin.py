from django.contrib import admin
from .models import Blog, Comment

class BlogAdmin(admin.ModelAdmin):
    list_display = ('blog_id', 'title', 'category','upload_image', 'like_count_display', 'created_at')

    def like_count_display(self, obj):
        return obj.liked_by.count()
    like_count_display.short_description = 'Like Count'

class CommentAdmin(admin.ModelAdmin):
    list_display = ('blog', 'user', 'content', 'timestamp')


admin.site.register(Blog, BlogAdmin)
admin.site.register(Comment, CommentAdmin)