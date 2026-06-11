from django.contrib import admin
from .models import Category, Author, AuthorProfile, Tag, Book

admin.site.register(Category)
admin.site.register(Author)
admin.site.register(AuthorProfile)
admin.site.register(Tag)
admin.site.register(Book)