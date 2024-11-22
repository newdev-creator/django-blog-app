from django.core.management.base import BaseCommand
from blog.models import Post
from django.conf import settings
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from transformers import pipeline

class Command(BaseCommand):
    help = "Generate a new blog post using Hugging Face Transformers"

    def handle(self, *args, **kwargs):
        # Set up the Hugging Face text generation pipeline
        generator = pipeline("text-generation", model="gpt2")  # Use "distilgpt2" for lighter models

        # Generate title
        title_prompt = "Generate a creative and catchy title for a tech blog post:"
        title_result = generator(title_prompt, max_new_tokens=10, num_return_sequences=1, truncation=True)
        title = title_result[0]['generated_text'].strip()

        # Generate body content
        content_prompt = f"Write a detailed blog post about '{title}':"
        content_result = generator(content_prompt, max_new_tokens=100, num_return_sequences=1, truncation=True)
        body = content_result[0]['generated_text'].strip()

        # Generate tags
        tags_prompt = f"Suggest relevant tags for a blog post about '{title}':"
        tags_result = generator(tags_prompt, max_new_tokens=10, num_return_sequences=1, truncation=True)
        tags_text = tags_result[0]['generated_text'].strip()
        tags = [tag.strip()[:100] for tag in tags_text.split(',') if len(tag.strip()) <= 100]  # Filter and truncate tags

        # Get default author
        User = get_user_model()
        default_author = User.objects.first()
        if not default_author:
            self.stdout.write(self.style.ERROR("No user found to assign as author."))
            return

        # Create and save the post
        post = Post.objects.create(
            title=title,
            slug=slugify(title),
            author=default_author,
            body=body,
            publish=now(),
            status=Post.Status.DRAFT,  # Save as draft
        )
        post.tags.add(*tags)

        # Save the post
        post.save()

        # Output success message
        self.stdout.write(self.style.SUCCESS(f"New draft blog post created: {title}"))
