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
from .models import BlogPost  
from .models import Comment

# --- ARCHIVE ---
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
            messages.error(request, "This problem has not been published yet.")
            return redirect('problem_list')

    contest = None
    if contest_id:
        contest = get_object_or_404(Contest, pk=contest_id)
    
    active_contest = contest or problem.contests.filter(start_time__lte=now, end_time__gte=now).first()
    is_banned = getattr(request.user.profile, 'is_disqualified', False) if request.user.is_authenticated else False

    result = None
    if request.method == 'POST' and not is_banned:
        user_answer = request.POST.get('answer', '').strip()
        solution = request.POST.get('solution', '')
        
        # Надежное сравнение строк
        correct_val = str(problem.correct_answer).strip().lower()
        is_correct = (user_answer.lower() == correct_val)
        
        if request.user.is_authenticated:
            Submission.objects.create(
                author=request.user,
                problem=problem,
                user_answer=user_answer,
                solution_text=solution,
                is_correct=is_correct
            )
        
        result = "correct" if is_correct else "wrong"
        
    return render(request, 'archive/problem_detail.html', {
        'problem': problem, 
        'result': result, 
        'active_contest': active_contest, 
        'is_banned': is_banned
    })

# --- SUBMISSIONS ---
def submission_list(request):
    now = timezone.now()
    base_query = Submission.objects.filter(author__profile__is_disqualified=False)
    
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
    if submission.author.profile.is_disqualified and not request.user.is_staff and request.user != submission.author:
        messages.error(request, "This submission is unavailable.")
        return redirect('submission_list')

    active_contests = submission.problem.contests.filter(start_time__lte=timezone.now(), end_time__gte=timezone.now())
    can_view = (request.user == submission.author or request.user.is_staff or not active_contests.exists())
    return render(request, 'archive/submission_detail.html', {'submission': submission, 'can_view': can_view})

# --- CONTESTS ---
def contest_list(request):
    contests = Contest.objects.all().order_by('-start_time')
    return render(request, 'archive/contest_list.html', {'contests': contests, 'now': timezone.now()})

def contest_dashboard(request, pk):
    contest = get_object_or_404(Contest, pk=pk)
    now = timezone.now()

    if contest.start_time > now and not request.user.is_staff:
        messages.warning(request, f"Contest starts at {contest.start_time}")
        return redirect('contest_list')

    problems = contest.problems.all()
    solved_ids = Submission.objects.filter(author=request.user, is_correct=True).values_list('problem_id', flat=True).distinct() if request.user.is_authenticated else []
    return render(request, 'archive/contest_dashboard.html', {'contest': contest, 'problems': problems, 'solved_ids': solved_ids})

def contest_standings(request, pk):
    contest = get_object_or_404(Contest, pk=pk)
    problems = contest.problems.all()
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

# --- ACCOUNTS & RANKING ---
class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

def ranking_view(request):
    users_list = User.objects.filter(profile__is_disqualified=False).select_related('profile').order_by('-profile__rating', 'username')
    paginator = Paginator(users_list, 100) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'archive/ranking.html', {'page_obj': page_obj})

def user_profile_view(request, username):
    target_user = get_object_or_404(User, username=username)
    if target_user.profile.is_disqualified and not request.user.is_staff and request.user != target_user:
        messages.error(request, "This user has been disqualified.")
        return redirect('ranking_view')

    profile = target_user.profile
    is_friend = False
    if request.user.is_authenticated:
        is_friend = request.user.profile.friends.filter(id=target_user.id).exists()

    solved_count = Submission.objects.filter(author=target_user, is_correct=True).values('problem').distinct().count()
    current_rank = Rank.objects.filter(min_rating__lte=profile.rating).order_by('-min_rating').first()
    submissions = Submission.objects.filter(author=target_user).order_by('-submitted_at')[:15]
    
    rating_history = target_user.rating_history.all().order_by('date')
    
    return render(request, 'archive/profile.html', {
        'target_user': target_user,
        'profile': profile,
        'solved_count': solved_count,
        'submissions': submissions,
        'rank': current_rank,
        'is_friend': is_friend,
        'rating_history': rating_history,
    })

@login_required
def profile_view(request):
    return user_profile_view(request, request.user.username)

@login_required
def toggle_friend(request, username):
    target_user = get_object_or_404(User, username=username)
    if target_user.profile.is_disqualified:
        messages.error(request, "Cannot add a disqualified user to friends.")
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
    friends = request.user.profile.friends.filter(profile__is_disqualified=False).select_related('profile')
    return render(request, 'archive/friends_list.html', {'friends': friends})

# --- RATING SYSTEM ---
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
        author_subs = submissions.filter(author=author)
        solved_problems = contest.problems.filter(
            submission__author=author,
            submission__is_correct=True,
            submission__submitted_at__gte=contest.start_time,
            submission__submitted_at__lte=contest.end_time
        ).distinct()
        
        solved_count = solved_problems.count()
        penalty = 0
        for problem in solved_problems:
            prob_subs = author_subs.filter(problem=problem).order_by('submitted_at')
            first_correct = prob_subs.filter(is_correct=True).first()
            if first_correct:
                time_passed = (first_correct.submitted_at - contest.start_time).total_seconds() // 60
                failed_before = prob_subs.filter(submitted_at__lt=first_correct.submitted_at).count()
                penalty += time_passed + (failed_before * 20)

        participants.append({
            'user': author,
            'old_rating': author.profile.rating,
            'solved': solved_count,
            'penalty': penalty,
            'change': 0
        })

    if not participants:
        messages.warning(request, "No active participants found.")
        return redirect('contest_standings', pk=pk)

    K = 30 
    for i in range(len(participants)):
        for j in range(len(participants)):
            if i == j: continue
            p1, p2 = participants[i], participants[j]
            expected = 1 / (1 + 10 ** ((p2['old_rating'] - p1['old_rating']) / 400))
            
            if p1['solved'] > p2['solved']: 
                actual = 1
            elif p1['solved'] < p2['solved']: 
                actual = 0
            else:
                if p1['penalty'] < p2['penalty']: actual = 0.75
                elif p1['penalty'] > p2['penalty']: actual = 0.25
                else: actual = 0.5
            
            p1['change'] += K * (actual - expected)

    for p in participants:
        user = p['user']
        past_contests_count = user.rating_history.count()
        
        bonus = 0
        if p['solved'] > 0:
            if past_contests_count == 0: bonus = 50
            elif past_contests_count == 1: bonus = 25
        
        profile = user.profile
        profile.rating += int(p['change'] + bonus)
        profile.save()

        RatingHistory.objects.create(
            user=user, 
            rating=profile.rating, 
            contest=contest
        )
        
    messages.success(request, f"Rating calculated for {len(participants)} participants!")
    return redirect('contest_standings', pk=pk)

@staff_member_required
def manual_update_submission(request, pk, action):
    submission = get_object_or_404(Submission, pk=pk)
    if action == 'make_correct':
        submission.is_correct = True
    elif action == 'make_incorrect':
        submission.is_correct = False
    submission.save()
    messages.success(request, f"Submission #{submission.id} status updated.")
    return redirect('submission_detail', pk=pk)

def community_list(request):
    posts = BlogPost.objects.all().select_related('author')
    return render(request, 'archive/community.html', {'posts': posts})

@login_required
def create_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        if title and content:
            BlogPost.objects.create(author=request.user, title=title, content=content)
            return redirect('community')
    return render(request, 'archive/create_post.html')

def post_detail(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    if request.method == 'POST' and request.user.is_authenticated:
        text = request.POST.get('text')
        if text:
            Comment.objects.create(post=post, author=request.user, text=text)
            return redirect('post_detail', pk=pk)
    return render(request, 'archive/post_detail.html', {'post': post})