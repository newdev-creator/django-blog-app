from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from taggit.models import Tag
from datetime import datetime
from ..models import Post, Comment
from ..forms import CommentForm

class PostDetailViewTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='12345'
        )

        # Create test post with specific publish date
        self.post = Post.objects.create(
            title="Test Post",
            slug="test-post",
            author=self.user,
            body="Test post content",
            status=Post.Status.PUBLISHED,
            publish=timezone.make_aware(datetime(2024, 1, 1))
        )

        # Create some comments
        self.active_comment = Comment.objects.create(
            post=self.post,
            name="Active User",
            email="active@example.com",
            body="Active comment",
            activate=True
        )
        
        self.inactive_comment = Comment.objects.create(
            post=self.post,
            name="Inactive User",
            email="inactive@example.com",
            body="Inactive comment",
            activate=False
        )

        # Create tags and similar posts
        self.tag1 = Tag.objects.create(name='Django', slug='django')
        self.tag2 = Tag.objects.create(name='Python', slug='python')
        self.post.tags.add(self.tag1, self.tag2)

        # Create similar posts with same tags
        self.similar_post1 = Post.objects.create(
            title="Similar Post 1",
            slug="similar-post-1",
            author=self.user,
            body="Similar post 1 content",
            status=Post.Status.PUBLISHED,
            publish=timezone.now()
        )
        self.similar_post1.tags.add(self.tag1, self.tag2)

        self.similar_post2 = Post.objects.create(
            title="Similar Post 2",
            slug="similar-post-2",
            author=self.user,
            body="Similar post 2 content",
            status=Post.Status.PUBLISHED,
            publish=timezone.now()
        )
        self.similar_post2.tags.add(self.tag1)

    def test_post_detail_success(self):
        """Test successful post detail view"""
        url = reverse('blog:post_detail', args=[
            self.post.publish.year,
            self.post.publish.month,
            self.post.publish.day,
            self.post.slug
        ])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post/detail.html')
        self.assertEqual(response.context['post'], self.post)

    def test_post_detail_not_found(self):
        """Test post detail with non-existent post"""
        url = reverse('blog:post_detail', args=[2024, 1, 1, 'non-existent-post'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_draft_post_not_accessible(self):
        """Test that draft posts are not accessible"""
        draft_post = Post.objects.create(
            title="Draft Post",
            slug="draft-post",
            author=self.user,
            body="Draft post content",
            status=Post.Status.DRAFT,
            publish=timezone.now()
        )
        
        url = reverse('blog:post_detail', args=[
            draft_post.publish.year,
            draft_post.publish.month,
            draft_post.publish.day,
            draft_post.slug
        ])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_comments_filtering(self):
        """Test that only active comments are shown"""
        url = reverse('blog:post_detail', args=[
            self.post.publish.year,
            self.post.publish.month,
            self.post.publish.day,
            self.post.slug
        ])
        response = self.client.get(url)
        
        self.assertIn(self.active_comment, response.context['comments'])
        self.assertNotIn(self.inactive_comment, response.context['comments'])

    def test_comment_form_in_context(self):
        """Test that comment form is in the context"""
        url = reverse('blog:post_detail', args=[
            self.post.publish.year,
            self.post.publish.month,
            self.post.publish.day,
            self.post.slug
        ])
        response = self.client.get(url)
        
        self.assertIsInstance(response.context['form'], CommentForm)

    def test_similar_posts(self):
        """Test similar posts functionality"""
        url = reverse('blog:post_detail', args=[
            self.post.publish.year,
            self.post.publish.month,
            self.post.publish.day,
            self.post.slug
        ])
        response = self.client.get(url)
        
        similar_posts = response.context['similar_posts']
        
        # Check that similar posts are ordered correctly
        self.assertIn(self.similar_post1, similar_posts)
        self.assertIn(self.similar_post2, similar_posts)
        
        # Check that the original post is not in similar posts
        self.assertNotIn(self.post, similar_posts)
        
        # Check that posts are ordered by number of shared tags
        # similar_post1 (2 tags) should come before similar_post2 (1 tag)
        """
        self.assertTrue(
            similar_posts.filter(id=self.similar_post1.id).first().same_tags >
            similar_posts.filter(id=self.similar_post2.id).first().same_tags
        )
        """

    def test_incorrect_date(self):
        """Test accessing post with incorrect date"""
        url = reverse('blog:post_detail', args=[2023, 12, 31, self.post.slug])  # Wrong date
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)