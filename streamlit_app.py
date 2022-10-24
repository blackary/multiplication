import random
from datetime import datetime
from time import sleep

import streamlit as st

from st_database import database

st.set_page_config("Multiplication practice", page_icon="✖️")

st.title("Multiplication practice ✖️")

st.write("This is a simple multiplication practice app.")

name = st.text_input("What is your name?").lower()

if not name:
    st.stop()


def get_nums(name: str, num: int) -> tuple[int, int]:
    random.seed(name + str(num))
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    return num1, num2


db = database(name)

DAILY_GOAL = 100

db["current_num"] = db.get("current_num", 0)
idx = db["current_num"]

correct_today = []
for i in range(idx):
    if "correct_answer_on" in db[i]:
        correct_on = db[i]["correct_answer_on"].date()
        if correct_on == datetime.now().date():
            correct_today.append(db[i])

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
        incorrect_guesses = sum([len(c["incorrect_guesses"]) for c in correct_today])
        problems_missed = [c for c in correct_today if len(c["incorrect_guesses"]) > 0]
        total_time = (
            correct_today[-1]["correct_answer_on"]
            - correct_today[0]["correct_answer_on"]
        )
        time_in_minutes = int(total_time.total_seconds() / 60)
        st.write(f"Total number correct: **{num_correct}**")
        st.write(f"Total wrong answers: **{incorrect_guesses}**")
        st.write(f"Problems missed:")
        for p in problems_missed:
            f"* {p['num1']} x {p['num2']} = {p['num1'] * p['num2']} (guessed {', '.join(str(g) for g in p['incorrect_guesses'])})"
        st.write(f"Total time: **{time_in_minutes} minutes**")

num1, num2 = get_nums(name, idx)

text_answer = st.text_input(f"{num1} x {num2} = ")
submit = st.button("Submit")

if not text_answer and not submit:
    st.stop()

try:
    answer = int(text_answer)
except ValueError:
    st.error("Must put an integer value")
    st.stop()

if idx not in db:
    db[idx] = {
        "num1": num1,
        "num2": num2,
        "answer": num1 * num2,
        "incorrect_guesses": [],
        "correct_answer_on": None,
    }

if answer != num1 * num2:
    st.error("Incorrect!")
    data = db[idx]
    data["incorrect_guesses"].append(answer)
    db[idx] = data
else:
    st.write("Correct!")
    st.balloons()
    sleep(1)
    db["current_num"] += 1
    data = db[idx]
    data["correct_answer_on"] = datetime.now()
    db[idx] = data
    st.experimental_rerun()
