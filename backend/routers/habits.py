from fastapi import APIRouter, HTTPException, Depends
from datetime import date

from database import (
    HabitDB,
    HabitCompletionDB,
    get_db
)

from auth import get_current_user
from schemas import Habit


router = APIRouter(
    prefix="/habits",
    tags=["Habits"]
)


@router.get("")
def get_habits(
    db=Depends(get_db),
    user=Depends(get_current_user)
):
    habits = (
        db.query(HabitDB)
        .filter(
            HabitDB.user_id == user["user_id"]
        )
        .all()
    )

    return habits


@router.post("")
def create_habit(
    habit: Habit,
    db=Depends(get_db),
    user=Depends(get_current_user)
):
    new_habit = HabitDB(
        name=habit.name,
        description=habit.description,
        user_id=user["user_id"]
    )

    db.add(new_habit)
    db.commit()
    db.refresh(new_habit)

    return new_habit


@router.put("/{habit_id}")
def update_habit(
    habit_id: int,
    habit: Habit,
    db=Depends(get_db),
    user=Depends(get_current_user)
):
    existing_habit = (
        db.query(HabitDB)
        .filter(
            HabitDB.id == habit_id,
            HabitDB.user_id == user["user_id"]
        )
        .first()
    )

    if existing_habit is None:
        raise HTTPException(
            status_code=404,
            detail="Habit not found"
        )

    existing_habit.name = habit.name
    existing_habit.description = habit.description

    db.commit()
    db.refresh(existing_habit)

    return existing_habit


@router.delete("/{habit_id}")
def delete_habit(
    habit_id: int,
    db=Depends(get_db),
    user=Depends(get_current_user)
):
    habit = (
        db.query(HabitDB)
        .filter(
            HabitDB.id == habit_id,
            HabitDB.user_id == user["user_id"]
        )
        .first()
    )

    if habit is None:
        raise HTTPException(
            status_code=404,
            detail="Habit not found"
        )

    db.delete(habit)
    db.commit()

    return {
        "message": "Habit deleted successfully"
    }


@router.post("/{habit_id}/complete")
def complete_habit(
    habit_id: int,
    db=Depends(get_db),
    user=Depends(get_current_user)
):
    habit = (
        db.query(HabitDB)
        .filter(
            HabitDB.id == habit_id,
            HabitDB.user_id == user["user_id"]
        )
        .first()
    )

    if habit is None:
        raise HTTPException(
            status_code=404,
            detail="Habit not found"
        )

    today = date.today()

    existing_completion = (
        db.query(HabitCompletionDB)
        .filter(
            HabitCompletionDB.habit_id == habit_id,
            HabitCompletionDB.date == today
        )
        .first()
    )

    if existing_completion:
        raise HTTPException(
            status_code=400,
            detail="Habit already completed today"
        )

    completion = HabitCompletionDB(
        habit_id=habit_id,
        date=today,
        completed=True
    )

    db.add(completion)

    try:
        db.commit()
        db.refresh(completion)

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Habit already completed today"
        )

    return completion


@router.delete("/{habit_id}/complete")
def uncomplete_habit(
    habit_id: int,
    db=Depends(get_db),
    user=Depends(get_current_user)
):
    habit = (
        db.query(HabitDB)
        .filter(
            HabitDB.id == habit_id,
            HabitDB.user_id == user["user_id"]
        )
        .first()
    )

    if habit is None:
        raise HTTPException(
            status_code=404,
            detail="Habit not found"
        )

    today = date.today()

    completion = (
        db.query(HabitCompletionDB)
        .filter(
            HabitCompletionDB.habit_id == habit_id,
            HabitCompletionDB.date == today
        )
        .first()
    )

    if completion is None:
        raise HTTPException(
            status_code=404,
            detail="Habit is not completed today"
        )

    db.delete(completion)
    db.commit()

    return {
        "message": "Habit marked as incomplete"
    }


@router.get("/{habit_id}/history")
def get_habit_history(
    habit_id: int,
    db=Depends(get_db),
    user=Depends(get_current_user)
):
    habit = (
        db.query(HabitDB)
        .filter(
            HabitDB.id == habit_id,
            HabitDB.user_id == user["user_id"]
        )
        .first()
    )

    if habit is None:
        raise HTTPException(
            status_code=404,
            detail="Habit not found"
        )

    history = (
        db.query(HabitCompletionDB)
        .filter(
            HabitCompletionDB.habit_id == habit_id
        )
        .all()
    )

    return history


@router.get("/{habit_id}/stats")
def get_habit_stats(
    habit_id: int,
    db=Depends(get_db),
    user=Depends(get_current_user)
):
    habit = (
        db.query(HabitDB)
        .filter(
            HabitDB.id == habit_id,
            HabitDB.user_id == user["user_id"]
        )
        .first()
    )

    if habit is None:
        raise HTTPException(
            status_code=404,
            detail="Habit not found"
        )

    completions = (
        db.query(HabitCompletionDB)
        .filter(
            HabitCompletionDB.habit_id == habit_id,
            HabitCompletionDB.completed == True
        )
        .order_by(HabitCompletionDB.date.asc())
        .all()
    )

    total_completions = len(completions)

    today = date.today()

    completed_dates = {
        completion.date
        for completion in completions
    }

    completed_today = today in completed_dates

    # Current streak
    current_streak = 0

    if completed_today:
        current_date = today

        while current_date in completed_dates:
            current_streak += 1
            current_date = current_date.fromordinal(
                current_date.toordinal() - 1
            )

    # Best streak
    best_streak = 0
    current_run = 0
    previous_date = None

    for completion in completions:
        completion_date = completion.date

        if (
            previous_date is not None
            and completion_date.fromordinal(
                completion_date.toordinal() - 1
            ) == previous_date
        ):
            current_run += 1
        else:
            current_run = 1

        best_streak = max(
            best_streak,
            current_run
        )

        previous_date = completion_date

    # Completion rate
    completion_rate = 0

    if completions:
        first_date = completions[0].date
        days_since_start = (
            today - first_date
        ).days + 1

        completion_rate = round(
            total_completions / days_since_start * 100,
            2
        )

    return {
        "habit_id": habit_id,
        "habit_name": habit.name,
        "current_streak": current_streak,
        "best_streak": best_streak,
        "completed_today": completed_today,
        "total_completions": total_completions,
        "completion_rate": completion_rate
    }


@router.get("/{habit_id}/calendar")
def get_habit_calendar(
    habit_id: int,
    year: int,
    month: int,
    db=Depends(get_db),
    user=Depends(get_current_user)
):
    habit = (
        db.query(HabitDB)
        .filter(
            HabitDB.id == habit_id,
            HabitDB.user_id == user["user_id"]
        )
        .first()
    )

    if habit is None:
        raise HTTPException(
            status_code=404,
            detail="Habit not found"
        )

    if month < 1 or month > 12:
        raise HTTPException(
            status_code=400,
            detail="Month must be between 1 and 12"
        )

    import calendar

    days_in_month = calendar.monthrange(
        year,
        month
    )[1]

    completions = (
        db.query(HabitCompletionDB)
        .filter(
            HabitCompletionDB.habit_id == habit_id,
            HabitCompletionDB.date >= date(year, month, 1),
            HabitCompletionDB.date <= date(
                year,
                month,
                days_in_month
            )
        )
        .all()
    )

    completed_dates = {
        completion.date
        for completion in completions
        if completion.completed
    }

    days = []

    for day in range(1, days_in_month + 1):
        current_date = date(
            year,
            month,
            day
        )

        days.append({
            "date": current_date,
            "completed": current_date in completed_dates
        })

    return {
        "habit_id": habit_id,
        "habit_name": habit.name,
        "year": year,
        "month": month,
        "days": days
    }