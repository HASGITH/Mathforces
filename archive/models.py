from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

class Problem(models.Model):
    title = models.CharField("Title", max_length=200)
    description = models.TextField("Problem Statement")
    correct_answer = models.CharField("Correct Answer", max_length=100)
    difficulty = models.IntegerField("Difficulty Rating", default=0)
    
    DIFFICULTY_CHOICES = [
        ('bg-info text-dark', 'Baby (Blue)'),
        ('bg-success', 'Easy (Green)'),
        ('bg-primary', 'Normal (Blue)'),
        ('bg-warning text-dark', 'Hard (Yellow)'),
        ('bg-danger', 'Legendary (Red)'),
        ('bg-dark', 'X-Level (Black)'),
    ]
    difficulty_level = models.CharField(
        "Color Level",
        max_length=50, 
        choices=DIFFICULTY_CHOICES, 
        default='bg-primary'
    )

    def __str__(self):
        return self.title

class Contest(models.Model):
    title = models.CharField("Contest Title", max_length=200)
    description = models.TextField("Description/Rules", blank=True)
    start_time = models.DateTimeField("Start Time")
    end_time = models.DateTimeField("End Time")
    problems = models.ManyToManyField(Problem, related_name='contests', blank=True)

    def is_active(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Contest"
        verbose_name_plural = "Contests"

class Submission(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    user_answer = models.CharField("User Answer", max_length=100)
    solution_text = models.TextField("Solution/Thinking", blank=True, null=True)
    is_correct = models.BooleanField("Is Correct?", default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username} - {self.problem.title} ({'OK' if self.is_correct else 'WA'})"

class Rank(models.Model):
    title = models.CharField("Rank Title", max_length=50)
    min_rating = models.IntegerField("Minimum Rating", default=0)
    color_code = models.CharField("Color (HEX)", max_length=7, default="#808080")

    class Meta:
        verbose_name = "Rank Setting"
        verbose_name_plural = "Rank Settings"
        ordering = ['min_rating']

    def __str__(self):
        return f"{self.title} (from {self.min_rating})"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_disqualified = models.BooleanField(default=False, verbose_name="Disqualified")
    reason = models.CharField(max_length=255, blank=True, verbose_name="Ban Reason")
    rating = models.IntegerField(default=0, verbose_name="Rating")
    friends = models.ManyToManyField(User, related_name='user_friends', blank=True)
    
    def __str__(self):
        return f"Profile: {self.user.username}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

class RatingHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rating_history')
    rating = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    contest = models.ForeignKey('Contest', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['date']