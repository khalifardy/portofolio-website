from django.utils import timezone
from workspace.models.pomodoro import DailyPomodoroStats
from datetime import timedelta, datetime

def calculate_streak(user):
    today = timezone.now().date()
    streak = 0
    current_date = today
    
    while True:
        stats = DailyPomodoroStats.objects.filter(
            user=user,
            date=current_date,
            complete_pomodoros__gt=0
        ).first()
        
        if stats:
            streak += 1
            current_date -= timedelta(days=1)
        else:
            break
        
        if streak > 365:
            break
    
    return streak

def get_week_stats(user):
    today = timezone.now().date()
    week_ago = today - timedelta(days=6)
    
    stats = DailyPomodoroStats.objects.filter(
        user=user,
        date__gte=week_ago,
        date__lte=today
    ).order_by('date')
    
    stats_dict = {s.date: s for s in stats}
    week_data = []
    
    for i in range(7):
        date = week_ago + timedelta(days=i)
        if date in stats_dict:
            s = stats_dict[date]
            week_data.append(
                {
                    'date': date,
                    'day': date.strftime('%a'),
                    'completed': s.complete_pomodoros,
                    'focus_minutes': s.total_focus_minutes,
                    'goal_met': s.goal_met
                }
            )
        else:
            week_data.append(
                {
                    'date': date,
                    'day': date.strftime('%a'),
                    'completed': 0,
                    'focus_minutes': 0,
                    'goal_met':False
                }
            )
    return week_data
        