import random
from datetime import datetime
from time import sleep

import streamlit as st

from st_database import database

st.set_page_config("Multiplication practice")

st.title("Multiplication practice")

st.write("This is a simple multiplication practice app.")

name = st.text_input("What is your name?").lower()

if not name:
    st.stop()


def get_nums(name: str, num: int) -> tuple[int, int]:
    # Generate integer from name and num
    random.seed(name + str(num))
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    return num1, num2


db = database(name)

db["current_num"] = db.get("current_num", 0)
idx = db["current_num"]

correct_today = 0
for i in range(idx):
    if "correct_answer_on" in db[i]:
        correct_on = db[i]["correct_answer_on"].date()
        if correct_on == datetime.now().date():
            correct_today += 1

bar = st.progress(0)
bar.progress(correct_today)
st.write(f"Number correct today: {correct_today} out of 100")

num1, num2 = get_nums(name, idx)

text_answer = st.text_input(f"{num1} x {num2} = ")

if not st.button("Submit guess"):
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
        "answer": answer,
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
