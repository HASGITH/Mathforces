from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

class Problem(models.Model):
    title = models.CharField("Название", max_length=200)
    description = models.TextField("Условие задачи")
    correct_answer = models.CharField("Правильный ответ", max_length=100)
    difficulty = models.IntegerField("Сложность (например, 800)", default=0)
    
    DIFFICULTY_CHOICES = [
        ('bg-info text-dark', 'Baby (Голубой)'),
        ('bg-success', 'Easy (Зеленый)'),
        ('bg-primary', 'Normal (Синий)'),
        ('bg-warning text-dark', 'Hard (Желтый)'),
        ('bg-danger', 'Legendary (Красный)'),
        ('bg-dark', 'X-Level (Черный)'),
    ]
    difficulty_level = models.CharField(
        "Цветовой уровень",
        max_length=50, 
        choices=DIFFICULTY_CHOICES, 
        default='bg-primary'
    )

    def __str__(self):
        return self.title

class Contest(models.Model):
    title = models.CharField("Название контеста", max_length=200)
    description = models.TextField("Описание/Правила", blank=True)
    start_time = models.DateTimeField("Время начала")
    end_time = models.DateTimeField("Время завершения")
    problems = models.ManyToManyField(Problem, related_name='contests', blank=True)

    def is_active(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Соревнование"
        verbose_name_plural = "Соревнования"

class Submission(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    user_answer = models.CharField("Ответ участника", max_length=100)
    solution_text = models.TextField("Решение", blank=True, null=True)
    is_correct = models.BooleanField("Верно?", default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username} - {self.problem.title} ({'OK' if self.is_correct else 'WA'})"

class Rank(models.Model):
    title = models.CharField("Название ранга", max_length=50)
    min_rating = models.IntegerField("Минимальный рейтинг для получения", default=0)
    color_code = models.CharField("Цвет (HEX, например #FF0000)", max_length=7, default="#808080")

    class Meta:
        verbose_name = "Настройка ранга"
        verbose_name_plural = "Настройки рангов"
        ordering = ['min_rating']

    def __str__(self):
        return f"{self.title} (от {self.min_rating})"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_disqualified = models.BooleanField(default=False, verbose_name="Дисквалифицирован")
    reason = models.CharField(max_length=255, blank=True, verbose_name="Причина бана")
    rating = models.IntegerField(default=0, verbose_name="Рейтинг")
    friends = models.ManyToManyField(User, related_name='user_friends', blank=True)
    
    def __str__(self):
        return f"Профиль {self.user.username}"

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