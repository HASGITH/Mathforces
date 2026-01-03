import math
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.decorators import login_required
from .models import Problem, Submission, Contest, Profile, Rank, RatingHistory
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator

# --- АРХИВ ---
def problem_list(request):
    now = timezone.now()
    if request.user.is_staff:
        problems = Problem.objects.all()
    else:
        problems = Problem.objects.filter(
            Q(contests__isnull=True) | Q(contests__start_time__lte=now)
        ).distinct()

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
    
    if not request.user.is_staff:
        future_contests = problem.contests.filter(start_time__gt=now)
        has_started_contest = problem.contests.filter(start_time__lte=now).exists()
        
        if future_contests.exists() and not has_started_contest:
            messages.error(request, "Эта задача еще не опубликована.")
            return redirect('problem_list')

    contest = None
    if contest_id:
        contest = get_object_or_404(Contest, pk=contest_id)
    
    active_contest = contest or problem.contests.filter(start_time__lte=now, end_time__gte=now).first()
    
    # Проверка бана текущего пользователя
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
    now = timezone.now()
    # Базовый запрос: скрываем забаненных
    base_query = Submission.objects.filter(author__profile__is_disqualified=False)
    
    # ФИЛЬТРАЦИЯ ДЛЯ ССЫЛКИ ИЗ АРХИВА
    problem_id = request.GET.get('problem_id')
    status = request.GET.get('status')
    
    if problem_id:
        base_query = base_query.filter(problem_id=problem_id)
    if status == 'correct':
        base_query = base_query.filter(is_correct=True)

    if request.user.is_staff:
        submissions = base_query.order_by('-submitted_at')[:50]
    else:
        submissions = base_query.filter(
            Q(problem__contests__isnull=True) | Q(problem__contests__start_time__lte=now)
        ).distinct().order_by('-submitted_at')[:50]
        
    return render(request, 'archive/submission_list.html', {'submissions': submissions})

def submission_detail(request, pk):
    submission = get_object_or_404(Submission, pk=pk)
    # Если автор забанен, доступ только ему самому или админу
    if submission.author.profile.is_disqualified and not request.user.is_staff and request.user != submission.author:
        messages.error(request, "Эта посылка недоступна.")
        return redirect('submission_list')

    active_contests = submission.problem.contests.filter(start_time__lte=timezone.now(), end_time__gte=timezone.now())
    can_view = (request.user == submission.author or request.user.is_staff or not active_contests.exists())
    return render(request, 'archive/submission_detail.html', {'submission': submission, 'can_view': can_view})

# --- СОРЕВНОВАНИЯ ---
def contest_list(request):
    contests = Contest.objects.all().order_by('-start_time')
    return render(request, 'archive/contest_list.html', {'contests': contests, 'now': timezone.now()})

def contest_dashboard(request, pk):
    contest = get_object_or_404(Contest, pk=pk)
    now = timezone.now()

    if contest.start_time > now and not request.user.is_staff:
        messages.warning(request, f"Соревнование начнется в {contest.start_time}")
        return redirect('contest_list')

    problems = contest.problems.all()
    solved_ids = Submission.objects.filter(author=request.user, is_correct=True).values_list('problem_id', flat=True).distinct() if request.user.is_authenticated else []
    return render(request, 'archive/contest_dashboard.html', {'contest': contest, 'problems': problems, 'solved_ids': solved_ids})

def contest_standings(request, pk):
    contest = get_object_or_404(Contest, pk=pk)
    problems = contest.problems.all()
    # В таблице результатов контеста оставляем только тех, кто НЕ забанен
    submissions = Submission.objects.filter(
        problem__in=problems, 
        submitted_at__gte=contest.start_time, 
        submitted_at__lte=contest.end_time,
        author__profile__is_disqualified=False
    )
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

# --- АККАУНТЫ И РАНКИНГ ---
class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

def ranking_view(request):
    # Показываем только тех, кто НЕ дисквалифицирован
    users_list = User.objects.filter(profile__is_disqualified=False).select_related('profile').order_by('-profile__rating', 'username')
    
    paginator = Paginator(users_list, 100) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'archive/ranking.html', {'page_obj': page_obj})

def user_profile_view(request, username):
    target_user = get_object_or_404(User, username=username)
    
    # Если пользователь забанен, его профиль видит только он сам или админ
    if target_user.profile.is_disqualified and not request.user.is_staff and request.user != target_user:
        messages.error(request, "Этот пользователь дисквалифицирован.")
        return redirect('ranking_view')

    profile = target_user.profile
    is_friend = False
    if request.user.is_authenticated:
        is_friend = request.user.profile.friends.filter(id=target_user.id).exists()

    solved_count = Submission.objects.filter(author=target_user, is_correct=True).values('problem').distinct().count()
    current_rank = Rank.objects.filter(min_rating__lte=profile.rating).order_by('-min_rating').first()
    submissions = Submission.objects.filter(author=target_user).order_by('-submitted_at')[:15]
    
    return render(request, 'archive/profile.html', {
        'target_user': target_user,
        'profile': profile,
        'solved_count': solved_count,
        'submissions': submissions,
        'rank': current_rank,
        'is_friend': is_friend,
    })

@login_required
def profile_view(request):
    # Редирект на именной профиль текущего юзера
    return user_profile_view(request, request.user.username)

@login_required
def toggle_friend(request, username):
    target_user = get_object_or_404(User, username=username)
    # Нельзя дружить с забаненными
    if target_user.profile.is_disqualified:
        messages.error(request, "Нельзя добавить в друзья дисквалифицированного пользователя.")
        return redirect('ranking_view')
        
    if target_user != request.user:
        profile = request.user.profile
        if profile.friends.filter(id=target_user.id).exists():
            profile.friends.remove(target_user)
        else:
            profile.friends.add(target_user)
    return redirect('user_profile', username=username)

def user_search(request):
    query = request.GET.get('q', '')
    # Ищем только по тем, кто НЕ дисквалифицирован
    if query:
        users = User.objects.filter(
            username__icontains=query,
            profile__is_disqualified=False
        ).select_related('profile')
    else:
        users = []
        
    return render(request, 'archive/user_search.html', {'users': users, 'query': query})

@login_required
def friends_list_view(request):
    # Прячем дисквалифицированных из списка друзей
    friends = request.user.profile.friends.filter(profile__is_disqualified=False).select_related('profile')
    return render(request, 'archive/friends_list.html', {'friends': friends})

@staff_member_required
def calculate_contest_rating(request, pk):
    contest = get_object_or_404(Contest, pk=pk)
    submissions = Submission.objects.filter(
        problem__in=contest.problems.all(),
        submitted_at__gte=contest.start_time,
        submitted_at__lte=contest.end_time
    )
    
    author_list = list({
        sub.author for sub in submissions 
        if not sub.author.profile.is_disqualified
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

    if not participants:
        messages.warning(request, "Нет активных участников для начисления рейтинга.")
        return redirect('contest_standings', pk=pk)

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

        RatingHistory.objects.create(
            user=user, 
            rating=profile.rating, 
            contest=contest
        )
        
    messages.success(request, f"Рейтинг начислен для {len(participants)} участников!")
    return redirect('contest_standings', pk=pk)

@staff_member_required
def manual_update_submission(request, pk, action):
    submission = get_object_or_404(Submission, pk=pk)
    if action == 'make_correct':
        submission.is_correct = True
    elif action == 'make_incorrect':
        submission.is_correct = False
    submission.save()
    
    messages.success(request, f"Статус посылки #{submission.id} изменен.")
    return redirect('submission_detail', pk=pk)

# В функции problem_list в контекст ничего добавлять не нужно, 
# мы просто используем ID задачи в шаблоне для фильтрации.