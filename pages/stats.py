from datetime import date

import streamlit as st
from dateutil import parser

from get_stats import answers, get_score_for_date, show_stats, users

if st.session_state["name"] == st.secrets["see_all_name"]:
    users = [u["name"] for u in users.fetch().items]
elif st.session_state["name"]:
    users = [st.session_state["name"]]
else:
    st.info("You must go to the home page to enter your name first")
    st.stop()

for name in users:
    st.write(f"## {name}")
    all_answers = answers.fetch({"name": name}).items
    raw_dates = set(a["correct_answer_on"] for a in all_answers if a is not None)

    all_dates = []
    for d in raw_dates:
        try:
            all_dates.append(parser.parse(d).date())
        except TypeError:
            pass

    selected_date = st.selectbox(
        "Select a date to see stats",
        options=sorted(all_dates, reverse=True),
        key=f"{name}-date",
    )
    show_stats(name, selected_date)

    scores_over_time = []

    for a_date in all_dates:
        score = get_score_for_date(name, a_date)
        scores_over_time.append({"date": a_date, "score": score})

    if scores_over_time:
        st.bar_chart(scores_over_time, x="date", y="score")
