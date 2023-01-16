from __future__ import annotations

import random
from datetime import date, datetime

import streamlit as st
from streamlit_extras.let_it_rain import rain

from get_stats import DAILY_GOAL, answers, show_stats, users

emoji_options = [
    "🎈",
    "🎉",
    "🎊",
    "🎆",
    "🎇",
    "🧨",
    "✨",
    "🎀",
    "🎁",
    "🎗️",
    "🎟️",
    "🎫",
    "🎖️",
    "🏆",
    "🏅",
    "🥇",
    "🥈",
    "🥉",
    "🏵️",
]

# Add animals to the emoji options
emoji_options += [
    "🐶",
    "🐱",
    "🐭",
    "🐹",
    "🐰",
    "🦊",
    "🐻",
    "🐼",
    "🐨",
    "🐯",
    "🦁",
    "🐮",
    "🐷",
    "🐽",
    "🐸",
    "🐵",
    "🙈",
    "🙉",
    "🙊",
    "🐒",
    "🐔",
    "🐧",
    "🐦",
    "🐤",
    "🐣",
    "🐥",
    "🦆",
    "🦅",
    "🦉",
    "🦇",
    "🐺",
    "🐗",
    "🐴",
    "🦄",
    "🐝",
    "🐛",
    "🦋",
    "🐌",
    "🐞",
    "🐜",
    "🕷️",
    "🦂",
]


st.set_page_config("Multiplication practice")

st.title("Multiplication practice")

st.write("This is a simple multiplication practice app.")

if "name" not in st.session_state:
    st.session_state["name"] = ""

name = st.text_input("What is your name?", value=st.session_state["name"]).lower()


if not name:
    st.stop()

st.session_state["name"] = name

if name == st.secrets["see_all_name"]:
    st.write("Go to stats to see all stats")
    st.stop()


try:
    user = users.fetch({"name": name}).items[0]
except IndexError:
    user = {"name": name, "total_score": 0, "last_answered": 0, "emoji": "🎈"}
    user = users.put(user)

if not user.get("emoji", ""):
    user["emoji"] = "🎈"

emoji_picker = st.selectbox("Pick an emoji", options=emoji_options, index=emoji_options.index(user["emoji"]))

if emoji_picker != user["emoji"]:
    user["emoji"] = emoji_picker
    users.put(user)

rain(
    emoji=emoji_picker,
    font_size=54,
    falling_speed=5,
    animation_length="infinite",
)


def get_nums(name: str, num: int) -> tuple[int, int]:
    random.seed(name + str(num))
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    return num1, num2


correct_today = answers.fetch(
    {"name": name, "correct_answer_on": str(date.today())}, limit=DAILY_GOAL
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
        show_stats(name, date.today())


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
            "correct_answer_at": None,
        }
    )


text_answer = st.text_input(f"{num1} x {num2} = ", key=idx)
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
    answer["incorrect_guesses"].append(attempted_answer)
    answers.put(answer, key=answer["key"])
else:
    st.write("Correct!")
    st.balloons()
    user["last_answered"] += 1
    answer["correct_answer_at"] = str(datetime.now())
    answer["correct_answer_on"] = str(date.today())
    answers.put(answer, key=answer["key"])
    users.put(user, key=user["key"])
    st.experimental_rerun()
