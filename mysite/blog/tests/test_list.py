from django.test import TestCase
from django.urls import reverse
from taggit.models import Tag
from ..models import Post
from django.contrib.auth.models import User
from django.utils.text import slugify

class PostListViewTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser', 
            password='12345'
        )

        # Create sample Posts with the user as author
        self.post1 = Post.objects.create(
            title="Post 1", 
            body='body for post 1', 
            status='PB',
            author=self.user,
            slug=slugify("Post 1")
        )
        self.post2 = Post.objects.create(
            title="Post 2", 
            body='body for post 2', 
            status='PB',
            author=self.user,
            slug=slugify("Post 2")
        )
        self.post3 = Post.objects.create(
            title="Post 3", 
            body='body for post 3', 
            status='PB',
            author=self.user,
            slug=slugify("Post 3")
        )

        # Rest of the setup remains the same
        self.tag1 = Tag.objects.create(name='Django', slug='django')
        self.tag2 = Tag.objects.create(name='Python', slug='python')
        self.tag3 = Tag.objects.create(name='JavaScript', slug='javascript')
        self.post1.tags.add(self.tag1)
        self.post2.tags.add(self.tag1, self.tag2)
        self.post3.tags.add(self.tag2, self.tag3)

    def test_post_list_view_with_tag(self):
        # Test the post list view filtered by a specific tag
        response = self.client.get(reverse('blog:post_list_by_tag', args=['django']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Post 1")
        self.assertContains(response, "Post 2")
        self.assertContains(response, "Post 3")

    def test_post_list_pagination(self):
        # Test the post list view with pagination

        # Add additional posts
        for i in range(4, 10):
            Post.objects.create(
                title=f"Post {i}",
                body=f"Body for post {i}",
                status='PB',
                author=self.user,
                slug=slugify(f"Post {i}")
            )

        response = self.client.get(reverse('blog:post_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['posts']), 3)

    def test_post_list_invalid_page(self):
        # Test the post list view with an invalid page number
        response = self.client.get(reverse('blog:post_list') + '?page=999')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['posts']), 3)

    def test_post_list_invalid_tag(self):
        # Test the post list view with an invalid tag
        response = self.client.get(reverse('blog:post_list_by_tag', args=['nonexistent']))
        self.assertEqual(response.status_code, 404)