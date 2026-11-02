from datetime import date, timedelta

from fastapi import APIRouter, Depends

from database import (
    get_db,
    HabitDB,
    HabitCompletionDB
)
from auth import get_current_user


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("")
def get_dashboard(
    db=Depends(get_db),
    user=Depends(get_current_user)
):
    user_id = user["user_id"]

    # Получаем привычки текущего пользователя
    habits = (
        db.query(HabitDB)
        .filter(
            HabitDB.user_id == user_id
        )
        .all()
    )

    total_habits = len(habits)

    # Последние 7 дней
    today = date.today()
    week_start = today - timedelta(days=6)

    habit_ids = [
        habit.id
        for habit in habits
    ]

    completions = []

    if habit_ids:
        completions = (
            db.query(HabitCompletionDB)
            .filter(
                HabitCompletionDB.habit_id.in_(habit_ids),
                HabitCompletionDB.completed == True,
                HabitCompletionDB.date >= week_start,
                HabitCompletionDB.date <= today
            )
            .all()
        )

    # Даты выполнения
    completed_by_date = {}

    for completion in completions:

        if completion.date not in completed_by_date:
            completed_by_date[completion.date] = 0

        completed_by_date[completion.date] += 1

    # Сегодня
    completed_today = completed_by_date.get(
        today,
        0
    )

    today_percentage = 0

    if total_habits > 0:
        today_percentage = round(
            completed_today / total_habits * 100
        )

    # Последние 7 дней
    weekly_data = []

    total_week_completions = 0

    for i in range(7):

        current_date = (
            week_start
            + timedelta(days=i)
        )

        completed = completed_by_date.get(
            current_date,
            0
        )

        total_week_completions += completed

        percentage = 0

        if total_habits > 0:
            percentage = round(
                completed / total_habits * 100
            )

        weekly_data.append({
            "date": current_date,
            "completed": completed,
            "total": total_habits,
            "percentage": percentage
        })

    return {
        "today": {
            "completed": completed_today,
            "total": total_habits,
            "percentage": today_percentage
        },
        "week": weekly_data,
        "total_week_completions": total_week_completions
    }