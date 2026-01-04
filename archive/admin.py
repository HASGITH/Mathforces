from django.contrib import admin
from .models import Problem, Submission, Contest, Profile, Rank, RatingHistory

# Сначала снимаем регистрацию, если она была, чтобы не было ошибок
if admin.site.is_registered(Problem):
    admin.site.unregister(Problem)

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    # Колонки, которые будут видны в таблице
    list_display = ('id', 'title', 'difficulty', 'difficulty_level') 
    
    # Ссылка на редактирование будет на ID и Названии
    list_display_links = ('id', 'title') 
    
    # ЭТИ ПОЛЯ МОЖНО БУДЕТ ПРАВИТЬ ПРЯМО В ТАБЛИЦЕ
    list_editable = ('difficulty', 'difficulty_level') 
    
    # Фильтр справа
    list_filter = ('difficulty_level',) 
    
    # Поиск
    search_fields = ('title',)

# Регистрация остальных моделей (проверь, чтобы не дублировались ниже)
if not admin.site.is_registered(Profile):
    @admin.register(Profile)
    class ProfileAdmin(admin.ModelAdmin):
        list_display = ('user', 'rating', 'is_disqualified')
        list_editable = ('is_disqualified',)

if not admin.site.is_registered(Submission):
    admin.site.register(Submission)

if not admin.site.is_registered(Contest):
    admin.site.register(Contest)

if not admin.site.is_registered(Rank):
    admin.site.register(Rank)

if not admin.site.is_registered(RatingHistory):
    admin.site.register(RatingHistory)