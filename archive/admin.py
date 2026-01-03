from django.contrib import admin
from .models import Problem, Submission, Contest, Profile, Rank, RatingHistory

# 1. Настройка для ЗАДАЧ (Problem)
# Мы добавили 'id' для удобства и 'list_display_links', чтобы заголовок остался ссылкой
@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'difficulty', 'difficulty_level') 
    list_display_links = ('id', 'title') # Клик по ID или названию откроет задачу
    list_editable = ('difficulty', 'difficulty_level') # Редактирование прямо в списке
    list_filter = ('difficulty_level',) # Фильтр справа по цветам
    search_fields = ('title',)

# 2. Настройка для ПРОФИЛЕЙ (Profile)
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'is_disqualified')
    search_fields = ('user__username',)
    list_editable = ('is_disqualified',) # Чтобы быстро банить/разбанивать

# 3. Регистрация остальных моделей
# Чтобы избежать ошибок "AlreadyRegistered", регистрируем их простым списком
@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('author', 'problem', 'is_correct', 'submitted_at')
    list_filter = ('is_correct', 'problem')

@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'end_time')

@admin.register(Rank)
class RankAdmin(admin.ModelAdmin):
    list_display = ('title', 'min_rating', 'color_code')

@admin.register(RatingHistory)
class RatingHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'date', 'contest')