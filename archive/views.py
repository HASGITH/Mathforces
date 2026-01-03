import math
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.decorators import login_required
from .models import Problem, Submission, Contest, Profile, Rank, RatingHistory # Добавь Rank в конец
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect
from django.core.paginator import Paginator

# --- АРХИВ ---
def problem_list(request):
    problems = Problem.objects.all()
    solved_ids = []
    if request.user.is_authenticated:
        solved_ids = Submission.objects.filter(
            author=request.user, 
            is_correct=True
        ).values_list('problem_id', flat=True).distinct()
    return render(request, 'archive/problem_list.html', {'problems': problems, 'solved_ids': solved_ids})

def problem_detail(request, pk, contest_id=None):
    problem = get_object_or_404(Problem, pk=pk)
    now = timezone.now()
    contest = None
    if contest_id:
        contest = get_object_or_404(Contest, pk=contest_id)
    
    active_contest = contest or problem.contests.filter(start_time__lte=now, end_time__gte=now).first()
    is_banned = getattr(request.user.profile, 'is_disqualified', False) if request.user.is_authenticated else False

    result = None
    if request.method == 'POST' and not is_banned:
        user_answer = request.POST.get('answer', '').strip()
        solution = request.POST.get('solution', '')
        is_correct = (user_answer == problem.correct_answer.strip())
        
        if request.user.is_authenticated:
            Submission.objects.create(
                author=request.user,
                problem=problem,
                user_answer=user_answer,
                solution_text=solution,
                is_correct=is_correct
            )
        result = "Правильно!" if is_correct else "Неверно!"
        
    return render(request, 'archive/problem_detail.html', {
        'problem': problem, 'result': result, 'active_contest': active_contest, 'is_banned': is_banned
    })

# --- ПОСЫЛКИ ---
def submission_list(request):
    submissions = Submission.objects.all().order_by('-submitted_at')[:50]
    return render(request, 'archive/submission_list.html', {'submissions': submissions})

def submission_detail(request, pk):
    submission = get_object_or_404(Submission, pk=pk)
    active_contests = submission.problem.contests.filter(start_time__lte=timezone.now(), end_time__gte=timezone.now())
    can_view = (request.user == submission.author or request.user.is_staff or not active_contests.exists())
    return render(request, 'archive/submission_detail.html', {'submission': submission, 'can_view': can_view})

# --- СОРЕВНОВАНИЯ ---
def contest_list(request):
    contests = Contest.objects.all().order_by('-start_time')
    return render(request, 'archive/contest_list.html', {'contests': contests, 'now': timezone.now()})

def contest_dashboard(request, pk):
    contest = get_object_or_404(Contest, pk=pk)
    problems = contest.problems.all()
    solved_ids = Submission.objects.filter(author=request.user, is_correct=True).values_list('problem_id', flat=True).distinct() if request.user.is_authenticated else []
    return render(request, 'archive/contest_dashboard.html', {'contest': contest, 'problems': problems, 'solved_ids': solved_ids})

def contest_standings(request, pk):
    contest = get_object_or_404(Contest, pk=pk)
    problems = contest.problems.all()
    submissions = Submission.objects.filter(problem__in=problems, submitted_at__gte=contest.start_time, submitted_at__lte=contest.end_time)
    users = {sub.author for sub in submissions}
    results = []
    for user in users:
        solved_count, penalty, user_problems = 0, 0, []
        for problem in problems:
            attempts = submissions.filter(author=user, problem=problem).order_by('submitted_at')
            correct_sub = attempts.filter(is_correct=True).first()
            if correct_sub:
                solved_count += 1
                time_passed = (correct_sub.submitted_at - contest.start_time).total_seconds() // 60
                failed_before = attempts.filter(submitted_at__lt=correct_sub.submitted_at).count()
                penalty += time_passed + (failed_before * 20)
                user_problems.append({'status': 'OK', 'failed': failed_before, 'time': int(time_passed)})
            else:
                user_problems.append({'status': 'WA', 'failed': attempts.count()})
        results.append({'user': user, 'solved': solved_count, 'penalty': int(penalty), 'problems': user_problems})
    results.sort(key=lambda x: (-x['solved'], x['penalty']))
    return render(request, 'archive/contest_standings.html', {'contest': contest, 'results': results, 'problems': problems})

# --- АККАУНТЫ ---
class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

@login_required
def profile_view(request):
    # Твой собственный профиль
    user_obj = request.user 
    profile = user_obj.profile
    
    # Считаем данные
    solved_count = Submission.objects.filter(author=user_obj, is_correct=True).values('problem').distinct().count()
    current_rank = Rank.objects.filter(min_rating__lte=profile.rating).order_by('-min_rating').first()
    submissions = Submission.objects.filter(author=user_obj).order_by('-submitted_at')[:15]
    
    return render(request, 'archive/profile.html', {
        'target_user': user_obj,  # ОБЯЗАТЕЛЬНО: добавляем эту строку
        'profile': profile,
        'solved_count': solved_count,
        'submissions': submissions,
        'rank': current_rank,
    })

@staff_member_required
def calculate_contest_rating(request, pk):
    contest = get_object_or_404(Contest, pk=pk)
    
    # Собираем все посылки во время контеста
    submissions = Submission.objects.filter(
        problem__in=contest.problems.all(),
        submitted_at__gte=contest.start_time,
        submitted_at__lte=contest.end_time
    )
    
    # 1. Собираем участников, НО исключаем тех, кто забанен (is_disqualified=True)
    author_list = list({
        sub.author for sub in submissions 
        if not sub.author.profile.is_disqualified  # <-- ВОТ ЭТА ПРОВЕРКА
    })
    
    participants = []
    for author in author_list:
        solved = submissions.filter(author=author, is_correct=True).values('problem').distinct().count()
        participants.append({
            'user': author,
            'old_rating': author.profile.rating,
            'solved': solved,
            'change': 0
        })

    # Если после фильтрации никого не осталось (все забанены или никто не участвовал)
    if not participants:
        messages.warning(request, "Нет активных участников (не забаненных) для начисления рейтинга.")
        return redirect('contest_standings', pk=pk)

    # 2. Алгоритм Эло (сравнение каждого с каждым)
    K = 40
    for i in range(len(participants)):
        for j in range(len(participants)):
            if i == j: continue
            p1, p2 = participants[i], participants[j]
            expected = 1 / (1 + 10 ** ((p2['old_rating'] - p1['old_rating']) / 400))
            if p1['solved'] > p2['solved']: actual = 1
            elif p1['solved'] < p2['solved']: actual = 0
            else: actual = 0.5
            p1['change'] += K * (actual - expected)

    # 3. Применяем изменения + БОНУСЫ
    for p in participants:
        user = p['user']
        past_contests = Submission.objects.filter(author=user, submitted_at__lt=contest.start_time).values('problem__contests').distinct().count()
        
        bonus = 0
        if past_contests == 0: bonus = 100
        elif past_contests == 1: bonus = 50
        elif past_contests == 2: bonus = 30
        
        profile = user.profile
        profile.rating += int(p['change'] + bonus)
        profile.save()

        # ДОБАВЬ ЭТО:
        RatingHistory.objects.create(
            user=user, 
            rating=profile.rating, 
            contest=contest
        )
        
    messages.success(request, f"Рейтинг начислен для {len(participants)} честных участников! Забаненные игроки проигнорированы.")
    return redirect('contest_standings', pk=pk)

def user_profile_view(request, username):
    target_user = get_object_or_404(User, username=username)
    profile = target_user.profile
    
    # Проверка, является ли этот пользователь другом для текущего
    is_friend = False
    if request.user.is_authenticated:
        is_friend = request.user.profile.friends.filter(id=target_user.id).exists()

    solved_count = Submission.objects.filter(author=target_user, is_correct=True).values('problem').distinct().count()
    current_rank = Rank.objects.filter(min_rating__lte=profile.rating).order_by('-min_rating').first()
    submissions = Submission.objects.filter(author=target_user).order_by('-submitted_at')[:15]
    
    return render(request, 'archive/profile.html', {
        'target_user': target_user, # Используем target_user, чтобы не путать с request.user
        'profile': profile,
        'solved_count': solved_count,
        'submissions': submissions,
        'rank': current_rank,
        'is_friend': is_friend,
    })

@login_required
def toggle_friend(request, username):
    target_user = get_object_or_404(User, username=username)
    if target_user != request.user:
        profile = request.user.profile
        if profile.friends.filter(id=target_user.id).exists():
            profile.friends.remove(target_user)
        else:
            profile.friends.add(target_user)
    return redirect('user_profile', username=username)

def user_search(request):
    query = request.GET.get('q', '')
    users = User.objects.filter(username__icontains=query).select_related('profile') if query else []
    return render(request, 'archive/user_search.html', {'users': users, 'query': query})

@login_required
def friends_list_view(request):
    # Получаем список друзей из профиля текущего пользователя
    friends = request.user.profile.friends.all().select_related('profile')
    return render(request, 'archive/friends_list.html', {'friends': friends})

def ranking_view(request):
    # Получаем всех пользователей, у которых есть профиль, сортируем по рейтингу
    users_list = User.objects.select_related('profile').order_by('-profile__rating', 'username')
    
    # Разбиваем список на страницы (по 100 человек на каждой)
    paginator = Paginator(users_list, 100) 
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'archive/ranking.html', {'page_obj': page_obj})