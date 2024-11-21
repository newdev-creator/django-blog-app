from django.test import TestCase
from django.urls import reverse
from ..models import Post
from django.utils import timezone
from django.contrib.auth.models import User


class PostSearchViewTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser', 
            password='12345'
        )
        
        # Create published posts
        self.post1 = Post.objects.create(
            title="Django Tutorial",
            slug="django-tutorial",
            author=self.user,
            body="Learn Django step by step.",
            status=Post.Status.PUBLISHED,
            publish=timezone.now()
        )
        self.post2 = Post.objects.create(
            title="Python Guide",
            slug="python-guide",
            author=self.user,
            body="Master Python programming.",
            status=Post.Status.PUBLISHED,
            publish=timezone.now()
        )

        # Create a draft post (should not appear in search results)
        self.draft_post = Post.objects.create(
            title="Draft Post",
            slug="draft-post",
            author=self.user,
            body="This is a draft post.",
            status=Post.Status.DRAFT,
            publish=timezone.now()
        )

    def test_search_form_rendered(self):
        """Ensure the search form renders correctly."""
        response = self.client.get(reverse('blog:post_search'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post/search.html')
        self.assertIn('form', response.context)
        self.assertEqual(response.context['query'], None)
        self.assertEqual(len(response.context['results']), 0)

    def test_valid_query_with_results(self):
        """Test a valid query that matches published posts."""
        response = self.client.get(reverse('blog:post_search'), {'query': 'Django'})
        self.assertEqual(response.status_code, 200)
        results = response.context['results']

        # Ensure only the matching published post is returned
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], self.post1)

    def test_valid_query_no_results(self):
        """Test a valid query that matches no posts."""
        response = self.client.get(reverse('blog:post_search'), {'query': 'Flask'})
        self.assertEqual(response.status_code, 200)
        results = response.context['results']

        # Ensure no results are returned for non-matching queries
        self.assertEqual(len(results), 0)

    def test_empty_query(self):
        """Test an empty query."""
        response = self.client.get(reverse('blog:post_search'), {'query': ''})
        self.assertEqual(response.status_code, 200)

        # Ensure no results are returned for empty queries
        self.assertEqual(response.context['query'], None)
        self.assertEqual(len(response.context['results']), 0)

    def test_draft_posts_excluded(self):
        """Test that draft posts are excluded from search results."""
        response = self.client.get(reverse('blog:post_search'), {'query': 'Draft'})
        self.assertEqual(response.status_code, 200)
        results = response.context['results']

        # Ensure draft posts are not returned
        self.assertEqual(len(results), 0)

    def test_case_insensitive_search(self):
        """Test that searches are case insensitive."""
        response = self.client.get(reverse('blog:post_search'), {'query': 'django'})
        self.assertEqual(response.status_code, 200)
        results = response.context['results']

        # Ensure the query matches regardless of case
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], self.post1)
