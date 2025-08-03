from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from videos.models import Video, Comment, VideoRating
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample data for testing'

    def handle(self, *args, **options):
        # Create sample users
        creator1, created = User.objects.get_or_create(
            username='creator1',
            defaults={
                'email': 'creator1@example.com',
                'user_type': 'creator'
            }
        )
        if created:
            creator1.set_password('testpass123')
            creator1.save()

        creator2, created = User.objects.get_or_create(
            username='creator2',
            defaults={
                'email': 'creator2@example.com',
                'user_type': 'creator'
            }
        )
        if created:
            creator2.set_password('testpass123')
            creator2.save()

        consumer1, created = User.objects.get_or_create(
            username='consumer1',
            defaults={
                'email': 'consumer1@example.com',
                'user_type': 'consumer'
            }
        )
        if created:
            consumer1.set_password('testpass123')
            consumer1.save()

        # Create sample videos
        sample_videos = [
            {
                'title': 'Introduction to Django',
                'description': 'A comprehensive tutorial on Django web framework',
                'genre': 'education',
                'age_rating': 'G',
                'creator': creator1,
            },
            {
                'title': 'Funny Cat Compilation',
                'description': 'Hilarious moments with cats',
                'genre': 'comedy',
                'age_rating': 'PG',
                'creator': creator1,
            },
            {
                'title': 'Latest Tech News',
                'description': 'Weekly roundup of technology news',
                'genre': 'news',
                'age_rating': 'G',
                'creator': creator2,
            },
            {
                'title': 'Cooking Masterclass',
                'description': 'Learn to cook like a professional chef',
                'genre': 'lifestyle',
                'age_rating': 'G',
                'creator': creator2,
            },
        ]

        for video_data in sample_videos:
            video, created = Video.objects.get_or_create(
                title=video_data['title'],
                defaults=video_data
            )
            if created:
                # Add random views and likes
                video.views = random.randint(100, 5000)
                video.likes = random.randint(10, 500)
                video.save()

                # Add sample comments
                for i in range(random.randint(1, 5)):
                    Comment.objects.create(
                        video=video,
                        user=random.choice([consumer1, creator1, creator2]),
                        content=f"Great video! Comment {i+1}"
                    )

                # Add sample ratings
                VideoRating.objects.create(
                    video=video,
                    user=consumer1,
                    rating=random.randint(3, 5)
                )

        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data')
        )
