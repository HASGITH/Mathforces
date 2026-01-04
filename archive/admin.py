from django.contrib import admin
from .models import Problem, Submission, Contest, Profile, Rank, RatingHistory

# Сначала принудительно отменяем регистрацию, чтобы сбросить старый вид
try:
    admin.site.unregister(Problem)
except admin.sites.NotRegistered:
    pass

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    # ТЕПЕРЬ ТЫ УВИДИШЬ ЭТИ КОЛОНКИ:
    list_display = ('id', 'title', 'difficulty', 'difficulty_level') 
    
    # Клик по названию откроет задачу
    list_display_links = ('id', 'title') 
    
    # ВОТ ЭТО ПОЗВОЛИТ МЕНЯТЬ ЦВЕТА ПРЯМО В СПИСКЕ:
    list_editable = ('difficulty', 'difficulty_level') 
    
    # Фильтр справа для удобства
    list_filter = ('difficulty_level',)
    search_fields = ('title',)

# Регистрация профилей с быстрым баном
try:
    admin.site.unregister(Profile)
except admin.sites.NotRegistered:
    pass

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'is_disqualified')
    list_editable = ('is_disqualified',)

# Остальные модели просто регистрируем, если они еще не в системе
models_to_register = [Submission, Contest, Rank, RatingHistory]
for model in models_to_register:
    try:
        admin.site.register(model)
    except admin.site.AlreadyRegistered:
        pass