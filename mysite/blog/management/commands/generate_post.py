from django.core.management.base import BaseCommand
from blog.models import Post
from django.conf import settings
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from openai import OpenAI

class Command(BaseCommand):
    help = "Generate a new blog post using AI"

    def handle(self, *args, **kwargs):
        # Set up OpenAI API client
        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        # Generate title using ChatGPT
        title_prompt = "Generate a creative and catchy title for a tech blog post."
        title_response = client.chat.completions.create(
            messages=[{"role": "user", "content": title_prompt}],
            max_tokens=10,
            model="gpt-3.5-turbo",
        )
        title = title_response.choices[0].message.content.strip()

        # Generate body content
        content_prompt = f"Write a detailed blog post about '{title}'."
        content_response = client.chat.completions.create(
            messages=[{"role": "user", "content": content_prompt}],
            max_tokens=100,
            model="gpt-3.5-turbo",
        )
        body = content_response.choices[0].message.content.strip()

        # Generate tags
        tags_prompt = f"Suggest relevant tags for a blog post about '{title}'."
        tags_response = client.chat.completions.create(
            messages=[{"role": "user", "content": tags_prompt}],
            max_tokens=10,
            model="gpt-3.5-turbo",
        )
        tags_text = tags_response.choices[0].message.content.strip()
        tags = [tag.strip() for tag in tags_text.split(',')]

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
