from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from videos.models import Video, VideoRating, Comment

User = get_user_model()

class VideoSharingPlatformTests(TestCase):
    """Basic tests for the VideoShare platform"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test users
        self.creator = User.objects.create_user(
            username='testcreator',
            email='creator@test.com',
            password='testpass123',
            user_type='creator'
        )
        
        self.consumer = User.objects.create_user(
            username='testconsumer',
            email='consumer@test.com',
            password='testpass123',
            user_type='consumer'
        )
        
        # Create test video
        self.video = Video.objects.create(
            title='Test Video',
            description='A test video for testing',
            creator=self.creator,
            genre='education',
            age_rating='G',
            external_url='https://example.com/test.mp4'
        )
    
    def test_homepage_loads(self):
        """Test that homepage loads successfully"""
        response = self.client.get(reverse('videos:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'VideoShare')
    
    def test_video_detail_view(self):
        """Test video detail page"""
        response = self.client.get(
            reverse('videos:video_detail', kwargs={'video_id': self.video.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.video.title)
    
    def test_user_registration(self):
        """Test user registration"""
        response = self.client.post(reverse('users:register'), {
            'username': 'newuser',
            'email': 'new@test.com',
            'user_type': 'consumer',
            'password1': 'testpass123456',
            'password2': 'testpass123456'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_user_login(self):
        """Test user login"""
        response = self.client.post(reverse('users:login'), {
            'username': 'testconsumer',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful login
    
    def test_creator_can_upload_video(self):
        """Test that creators can access upload page"""
        self.client.login(username='testcreator', password='testpass123')
        response = self.client.get(reverse('videos:creator_upload'))
        self.assertEqual(response.status_code, 200)
    
    def test_consumer_cannot_upload_video(self):
        """Test that consumers cannot access upload page"""
        self.client.login(username='testconsumer', password='testpass123')
        response = self.client.get(reverse('videos:creator_upload'))
        self.assertEqual(response.status_code, 302)  # Redirect because not allowed
    
    def test_video_rating(self):
        """Test video rating functionality"""
        self.client.login(username='testconsumer', password='testpass123')
        response = self.client.post(
            reverse('videos:rate_video', kwargs={'video_id': self.video.id}),
            {'rating': 5}
        )
        self.assertEqual(response.status_code, 200)
        
        # Check if rating was created
        rating = VideoRating.objects.get(video=self.video, user=self.consumer)
        self.assertEqual(rating.rating, 5)
    
    def test_video_comment(self):
        """Test video commenting functionality"""
        self.client.login(username='testconsumer', password='testpass123')
        response = self.client.post(
            reverse('videos:video_detail', kwargs={'video_id': self.video.id}),
            {'content': 'Great video!'}
        )
        self.assertEqual(response.status_code, 302)  # Redirect after comment
        
        # Check if comment was created
        comment = Comment.objects.get(video=self.video, user=self.consumer)
        self.assertEqual(comment.content, 'Great video!')
    
    def test_search_functionality(self):
        """Test video search"""
        response = self.client.get(reverse('videos:dashboard'), {
            'query': 'Test'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.video.title)
    
    def test_api_videos_endpoint(self):
        """Test API endpoint"""
        response = self.client.get(reverse('videos:api_videos'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
    
    def test_profile_pages(self):
        """Test profile related pages"""
        self.client.login(username='testconsumer', password='testpass123')
        
        # Test profile view
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 200)
        
        # Test edit profile
        response = self.client.get(reverse('users:edit_profile'))
        self.assertEqual(response.status_code, 200)
        
        # Test subscriptions page
        response = self.client.get(reverse('users:subscriptions'))
        self.assertEqual(response.status_code, 200)
