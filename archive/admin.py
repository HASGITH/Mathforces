from django.contrib import admin
from .models import Problem, Submission, Contest, Profile, Rank, RatingHistory

# 1. ПРАВИЛЬНАЯ настройка для ЗАДАЧ (Problem)
@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    # Эти поля есть в модели Problem
    list_display = ('title', 'difficulty', 'difficulty_level') 
    list_editable = ('difficulty', 'difficulty_level') # Чтобы менять прямо из списка

# 2. ПРАВИЛЬНАЯ настройка для ПРОФИЛЕЙ (Profile)
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    # В Profile есть поля user и rating
    list_display = ('user', 'rating', 'is_disqualified')
    search_fields = ('user__username',)

# 3. Остальные модели (если они еще не зарегистрированы)
# Если ты уже регистрировал их через @admin.register выше, эти строки не нужны
if not admin.site.is_registered(Submission):
    admin.site.register(Submission)
if not admin.site.is_registered(Contest):
    admin.site.register(Contest)
if not admin.site.is_registered(Rank):
    admin.site.register(Rank)
if not admin.site.is_registered(RatingHistory):
    admin.site.register(RatingHistory)