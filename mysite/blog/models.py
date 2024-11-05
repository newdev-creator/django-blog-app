from django.db import models
from django.utils import timezone


class Blog(models.Model):
    
    class Status(models.IntegerChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250)
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=2,
        choices=Status,
        default=Status.DRAFT,
    )

    class Meta:
        ordering = ('-publish',)
        Indexes = [
            models.Index(fields=['-publish']),
        ]

    def __str__(self):
        return self.title

