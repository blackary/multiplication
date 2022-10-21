import random
from datetime import date, datetime
from time import sleep

import streamlit as st
from dateutil import parser

# from st_database import database
from deta import Deta

deta = Deta(st.secrets["deta_project_key"])

st.set_page_config("Multiplication practice")

st.title("Multiplication practice")

st.write("This is a simple multiplication practice app.")

name = st.text_input("What is your name?").lower()

if not name:
    st.stop()


def get_nums(name: str, num: int) -> tuple[int, int]:
    random.seed(name + str(num))
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    return num1, num2


answers = deta.Base("multiplication_answers")
users = deta.Base("multiplication_users")

try:
    user = users.fetch({"name": name}).items[0]
except IndexError:
    user = {"name": name, "total_score": 0, "last_answered": 0}
    user = users.put(user)

DAILY_GOAL = 10

correct_today = answers.fetch(
    {"name": name, "correct_answer_on?pfx": str(date.today())}, limit=DAILY_GOAL
).items

idx = user["last_answered"]

num_correct = len(correct_today)

percent = int(min(num_correct / DAILY_GOAL * 100, 100))
st.progress(percent)
st.write(f"Number correct today: {num_correct} out of {DAILY_GOAL}")

if num_correct in [DAILY_GOAL, DAILY_GOAL + 1]:
    st.write("## You have completed your daily practice! (You can go on if you want)")
    for i in range(5):
        st.balloons()

if num_correct >= DAILY_GOAL:
    with st.expander("See how you did today", expanded=True):
        for item in correct_today:
            item["correct_answer_on"] = parser.parse(item["correct_answer_on"])
        start_time = min(correct_today, key=lambda x: x["correct_answer_on"])[
            "correct_answer_on"
        ]
        end_time = max(correct_today, key=lambda x: x["correct_answer_on"])[
            "correct_answer_on"
        ]
        incorrect_guesses = sum([len(c["incorrect_guesses"]) for c in correct_today])
        problems_missed = [c for c in correct_today if len(c["incorrect_guesses"]) > 0]
        total_time = end_time - start_time
        time_in_minutes = int(total_time.total_seconds() / 60)
        st.write(f"Total number correct: **{num_correct}**")
        st.write(f"Total wrong answers: **{incorrect_guesses}**")
        st.write("Problems missed:")
        for p in problems_missed:
            guesses = ", ".join(str(g) for g in p["incorrect_guesses"])
            f"* {p['num1']} x {p['num2']} = {p['num1'] * p['num2']} (guessed {guesses})"
        st.write(f"Total time: **{time_in_minutes} minutes**")

num1, num2 = get_nums(name, idx)

try:
    answer = answers.fetch({"name": name, "idx": idx}).items[0]
except IndexError:
    answer = answers.put(
        {
            "idx": idx,
            "name": name,
            "num1": num1,
            "num2": num2,
            "answer": num1 * num2,
            "incorrect_guesses": [],
            "correct_answer_on": None,
        }
    )


text_answer = st.text_input(f"{num1} x {num2} = ")
submit = st.button("Submit")

if not text_answer and not submit:
    st.stop()

try:
    attempted_answer = int(text_answer)
except ValueError:
    st.error("Must put an integer value")
    st.stop()

if attempted_answer != num1 * num2:
    st.error("Incorrect!")
    # data = db[idx]
    answer["incorrect_guesses"].append(attempted_answer)
    # data["incorrect_guesses"].append(answer)
    # db[idx] = data
    answers.put(answer, key=answer["key"])
else:
    st.write("Correct!")
    st.balloons()
    user["last_answered"] += 1
    # data = db[idx]
    answer["correct_answer_on"] = str(datetime.now())
    # db[idx] = data
    answers.put(answer, key=answer["key"])
    users.put(user, key=user["key"])
    sleep(1)
    st.experimental_rerun()
