# =========================================================
# app.py
# Ultimate Bayesian Election Predictor (Stable Version)
# =========================================================

import streamlit as st
import pandas as pd

from data.models import ElectionProject, Poll
from data.storage import save_project, load_project, list_projects

from data.poll_processor import (
    project_to_dataframe,
    build_simulator_inputs
)

from engine.simulator import run_simulation

from ui.charts import (
    prediction_bar_chart,
    win_rate_chart,
    world_distribution_chart,
    candidate_boxplot,
    trend_chart,
    winner_distribution_chart,
    fte_probability_chart
)

from ui.worlds_view import (
    render_world_table,
    render_single_world,
    render_winner_summary,
    render_candidate_extremes
)

# =========================================================
# SETUP
# =========================================================

st.set_page_config(
    page_title="Ultimate Bayesian Election Predictor",
    layout="wide"
)

# =========================================================
# SESSION STATE
# =========================================================

if "project" not in st.session_state:
    st.session_state.project = None

if "result" not in st.session_state:
    st.session_state.result = None

if "page" not in st.session_state:
    st.session_state.page = "menu"

# =========================================================
# MENU
# =========================================================

if st.session_state.page == "menu":

    st.title("Election Predictor")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("새 프로젝트"):
            st.session_state.page = "create"
            st.rerun()

    with col2:
        if st.button("불러오기"):
            st.session_state.page = "load"
            st.rerun()

    st.stop()

# =========================================================
# CREATE
# =========================================================

if st.session_state.page == "create":

    st.title("프로젝트 생성")

    name = st.text_input("이름")
    election_date = st.date_input("선거일")
    candidates_raw = st.text_input("후보 (콤마)")

    if st.button("생성"):

        candidates = [
            c.strip()
            for c in candidates_raw.split(",")
            if c.strip()
        ]

        st.session_state.project = ElectionProject(
            project_name=name,
            election_date=str(election_date),
            candidate_names=candidates,
            polls=[]
        )

        st.session_state.page = "editor"
        st.rerun()

    st.stop()

# =========================================================
# LOAD
# =========================================================

if st.session_state.page == "load":

    st.title("불러오기")

    projects = list_projects()

    if not projects:
        st.warning("없음")
        st.stop()

    selected = st.selectbox("선택", projects)

    if st.button("열기"):

        st.session_state.project = load_project(selected)
        st.session_state.page = "editor"
        st.rerun()

    st.stop()

# =========================================================
# EDITOR
# =========================================================

project = st.session_state.project

if project is None:
    st.stop()

st.title(project.project_name)

st.write("선거일:", project.election_date)
st.write("후보:", project.candidate_names)

# =========================================================
# POLL INPUT
# =========================================================

st.header("여론조사 추가")

with st.form("poll_form"):

    pollster = st.text_input("기관")
    start_date = st.date_input("시작")
    end_date = st.date_input("종료")
    sample_size = st.number_input(
        "표본수",
        min_value=1,
        max_value=1_000_000,
        value=1000
    )

    supports = {}
    undecided_pref = {}

    st.subheader("지지율")

    for c in project.candidate_names:
        supports[c] = st.number_input(c, 0.0, 100.0, 0.0)

    st.subheader("무당층 선호")

    for c in project.candidate_names:
        undecided_pref[c] = st.number_input(c, 0.0, 100.0, 0.0)

    submitted = st.form_submit_button("추가")

    if submitted:

        undecided = max(0.0, 100 - sum(supports.values()))

        project.polls.append(
            Poll(
                pollster=pollster,
                start_date=str(start_date),
                end_date=str(end_date),
                sample_size=sample_size,
                supports=supports,
                undecided=undecided,
                undecided_preferences=undecided_pref
            )
        )

        st.success("추가 완료")

# =========================================================
# POLL LIST (VIEW + EDIT)
# =========================================================

st.header("여론조사 목록")

for i, poll in enumerate(project.polls):

    with st.expander(f"{i+1}. {poll.pollster}"):

        poll.pollster = st.text_input(
            "기관",
            value=poll.pollster,
            key=f"p_{i}_name"
        )

        poll.start_date = str(
            st.date_input(
                "시작",
                value=pd.to_datetime(poll.start_date),
                key=f"p_{i}_start"
            )
        )

        poll.end_date = str(
            st.date_input(
                "종료",
                value=pd.to_datetime(poll.end_date),
                key=f"p_{i}_end"
            )
        )

        poll.sample_size = st.number_input(
            "표본수",
            value=int(poll.sample_size),
            min_value=1,
            key=f"p_{i}_sample"
        )

        st.subheader("지지율")

        for c in project.candidate_names:

            poll.supports[c] = st.number_input(
                c,
                value=float(poll.supports.get(c, 0.0)),
                min_value=0.0,
                max_value=100.0,
                key=f"p_{i}_{c}"
            )

        poll.undecided = max(
            0.0,
            100 - sum(poll.supports.values())
        )

        st.info(f"무당층: {poll.undecided:.2f}")

        st.subheader("무당층 선호")

        for c in project.candidate_names:

            poll.undecided_preferences[c] = st.number_input(
                f"{c}",
                value=float(
                    poll.undecided_preferences.get(c, 0.0)
                ),
                min_value=0.0,
                max_value=100.0,
                key=f"p_{i}_pref_{c}"
            )

        if st.button("삭제", key=f"del_{i}"):

            project.polls.pop(i)
            st.rerun()

# =========================================================
# SAVE
# =========================================================

if st.button("저장"):

    save_project(project)
    st.success("저장 완료")

# =========================================================
# RUN SIMULATION
# =========================================================

if st.button("시뮬레이션 실행"):

    df = project_to_dataframe(project)
    inputs = build_simulator_inputs(project)

    result = run_simulation(
        df,
        inputs["candidate_names"],
        project.election_date,
        world_count=100
    )

    st.session_state.result = result

# =========================================================
# RESULT
# =========================================================

result = st.session_state.result

if result:

    st.header("결과")

    st.dataframe(result["prediction_table"])
    st.dataframe(result["win_rates"])

    st.plotly_chart(prediction_bar_chart(result["prediction_table"]))
    st.plotly_chart(win_rate_chart(result["win_rates"]))
    st.plotly_chart(world_distribution_chart(result["worlds"], project.candidate_names))
    st.plotly_chart(candidate_boxplot(result["worlds"], project.candidate_names))
    st.plotly_chart(trend_chart(df, project.candidate_names))
    st.plotly_chart(winner_distribution_chart(result["worlds"]))
    st.plotly_chart(fte_probability_chart(result["worlds"], project.candidate_names))

    st.header("가능세계")

    render_world_table(result["worlds"], project.candidate_names)
    render_single_world(result["worlds"], project.candidate_names)
    render_winner_summary(result["worlds"])
    render_candidate_extremes(result["worlds"], project.candidate_names)
