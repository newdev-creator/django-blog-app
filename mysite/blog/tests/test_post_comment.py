from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Post, Comment
from django.utils import timezone

class PostCommentViewTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='12345'
        )

        # Create a published post
        self.post = Post.objects.create(
            title="Test Post",
            slug="test-post",
            author=self.user,
            body="Test post content",
            status=Post.Status.PUBLISHED,
            publish=timezone.now()
        )

        # Create a draft post
        self.draft_post = Post.objects.create(
            title="Draft Post",
            slug="draft-post",
            author=self.user,
            body="Draft content",
            status=Post.Status.DRAFT,
            publish=timezone.now()
        )

    def test_post_comment_success(self):
        """Test posting a valid comment successfully."""
        url = reverse('blog:post_comment', args=[self.post.id])  # Assuming you've named the URL
        data = {
            'name': 'Commenter',
            'email': 'commenter@example.com',
            'body': 'Nice post!'
        }

        response = self.client.post(url, data)

        # Check that the comment was created
        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.first()
        self.assertEqual(comment.name, 'Commenter')
        self.assertEqual(comment.email, 'commenter@example.com')
        self.assertEqual(comment.body, 'Nice post!')

        # Check that the correct template was used
        self.assertTemplateUsed(response, 'blog/post/comment.html')
        self.assertEqual(response.context['post'], self.post)
        self.assertEqual(response.context['comment'], comment)

    def test_post_comment_invalid_form(self):
        """Test posting an invalid comment (missing body)."""
        url = reverse('blog:post_comment', args=[self.post.id])
        data = {
            'name': 'Commenter',
            'email': 'commenter@example.com',
            'body': ''  # Invalid: empty body
        }

        response = self.client.post(url, data)

        # Check that the comment was NOT created
        self.assertEqual(Comment.objects.count(), 0)

        # Check that the form with errors is provided in context
        self.assertFormError(response, 'form', 'body', 'This field is required.')

        # Check that the correct template was used
        self.assertTemplateUsed(response, 'blog/post/comment.html')
        self.assertEqual(response.context['post'], self.post)

    def test_post_comment_on_draft_post(self):
        """Test that posting a comment on a draft post returns 404."""
        url = reverse('blog:post_comment', args=[self.draft_post.id])
        data = {
            'name': 'Commenter',
            'email': 'commenter@example.com',
            'body': 'Nice post!'
        }

        response = self.client.post(url, data)

        # The draft post should not be accessible, so we expect a 404
        self.assertEqual(response.status_code, 404)

    def test_post_comment_on_nonexistent_post(self):
        """Test that posting a comment on a non-existent post returns 404."""
        url = reverse('blog:post_comment', args=[999])  # Assuming 999 does not exist
        data = {
            'name': 'Commenter',
            'email': 'commenter@example.com',
            'body': 'Nice post!'
        }

        response = self.client.post(url, data)

        # The non-existent post should return 404
        self.assertEqual(response.status_code, 404)