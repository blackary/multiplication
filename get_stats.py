from datetime import date

import streamlit as st
from dateutil import parser
from deta import Deta

DAILY_GOAL = 15
GOAL_MINUTES = 20

deta = Deta(st.secrets["deta_project_key"])

answers = deta.Base("multiplication_answers")
users = deta.Base("multiplication_users")


def get_score(num_correct: int, num_total: int, total_minutes: float) -> float:
    """
    Calculate score as number of correct answers today / total number of answers today
    - (number of minutes spent - GOAL_MINUTES) * 100
    """
    score = (num_correct / num_total) * 100 - max((total_minutes - GOAL_MINUTES), 0)

    return score


def get_score_for_date(name: str, on_date: date) -> float:
    correct_today = answers.fetch(
        {"name": name, "correct_answer_on": str(on_date)},
    ).items

    if not correct_today:
        return 0

    for item in correct_today:
        item["correct_answer_at"] = parser.parse(item["correct_answer_at"])
    start_time = min(correct_today, key=lambda x: x["correct_answer_at"])[
        "correct_answer_at"
    ]
    end_time = max(correct_today, key=lambda x: x["correct_answer_at"])[
        "correct_answer_at"
    ]
    total_time = end_time - start_time
    time_in_minutes = int(total_time.total_seconds() / 60)
    num_correct = len(correct_today)
    num_total = len(correct_today) + sum(
        len(c["incorrect_guesses"]) for c in correct_today
    )
    score = get_score(num_correct, num_total, time_in_minutes)

    return score


def show_stats(name: str, on_date: date | None = None):
    if on_date is None:
        on_date = date.today()

    correct_today = answers.fetch(
        {"name": name, "correct_answer_on": str(on_date)},
    ).items

    if not correct_today:
        st.write("No answers today")
        return

    for item in correct_today:
        item["correct_answer_at"] = parser.parse(item["correct_answer_at"])
    start_time = min(correct_today, key=lambda x: x["correct_answer_at"])[
        "correct_answer_at"
    ]
    end_time = max(correct_today, key=lambda x: x["correct_answer_at"])[
        "correct_answer_at"
    ]
    incorrect_guesses = sum([len(c["incorrect_guesses"]) for c in correct_today])
    problems_missed = [c for c in correct_today if len(c["incorrect_guesses"]) > 0]
    total_time = end_time - start_time
    time_in_minutes = int(total_time.total_seconds() / 60)
    num_correct = len(correct_today)
    num_total = len(correct_today) + sum(
        len(c["incorrect_guesses"]) for c in correct_today
    )
    st.write(f"Total number correct: **{num_correct}**")
    st.write(f"Total wrong answers: **{incorrect_guesses}**")
    st.write("Problems missed:")
    for p in problems_missed:
        guesses = ", ".join(str(g) for g in p["incorrect_guesses"])
        st.write(
            f"* {p['num1']} x {p['num2']} = {p['num1'] * p['num2']} (guessed {guesses})"
        )
    st.write(f"Total time: **{time_in_minutes} minutes**")
    score = get_score(num_correct, num_total, time_in_minutes)
    st.write(f"Score today: **{score:.2f}**")
