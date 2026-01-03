from django.contrib import admin
from .models import Problem, Submission
from .models import Rank # Добавь в импорты
from .models import Contest, Profile, RatingHistory
admin.site.register(Problem)
admin.site.register(Submission)


@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'end_time')
    filter_horizontal = ('problems',)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_disqualified', 'reason']
    list_filter = ['is_disqualified']
    search_fields = ['user__username']

@admin.register(Rank)
class RankAdmin(admin.ModelAdmin):
    list_display = ('title', 'min_rating', 'color_code')

@admin.register(RatingHistory)
class RatingHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'date', 'contest')
    list_filter = ('user', 'date')