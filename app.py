# =========================================================
# app.py
# Ultimate Bayesian Election Predictor
# =========================================================

import streamlit as st

from data.models import (
    ElectionProject,
    Poll
)

from data.storage import (
    save_project,
    load_project,
    delete_project,
    list_projects
)

from data.poll_processor import (
    project_to_dataframe,
    build_simulator_inputs
)

from engine.simulator import (
    run_simulation
)

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
# Streamlit 설정
# =========================================================

st.set_page_config(
    page_title="Ultimate Bayesian Election Predictor",
    layout="wide"
)


# =========================================================
# 세션 상태
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

    st.title("Ultimate Bayesian Election Predictor")

    col1, col2, col3 = st.columns(3)

    with col1:

        if st.button("새 프로젝트"):

            st.session_state.project = None
            st.session_state.page = "create"
            st.rerun()

    with col2:

        if st.button("불러오기"):

            st.session_state.page = "load"
            st.rerun()

    st.stop()


# =========================================================
# CREATE PROJECT
# =========================================================

if st.session_state.page == "create":

    st.title("새 프로젝트 생성")

    name = st.text_input("프로젝트 이름")
    election_date = st.date_input("선거일")

    candidates_raw = st.text_input(
        "후보 (콤마로 구분)"
    )

    if st.button("생성"):

        candidates = [
            c.strip()
            for c in candidates_raw.split(",")
            if c.strip()
        ]

        st.session_state.project = ElectionProject(

            project_name=name,

            election_date=str(election_date),

            candidate_names=candidates

        )

        st.session_state.page = "editor"
        st.rerun()

    st.stop()


# =========================================================
# LOAD PROJECT
# =========================================================

if st.session_state.page == "load":

    st.title("프로젝트 불러오기")

    projects = list_projects()

    if len(projects) == 0:

        st.warning("저장된 프로젝트 없음")
        st.stop()

    selected = st.selectbox(
        "선택",
        projects
    )

    if st.button("불러오기"):

        project = load_project(selected)

        st.session_state.project = project
        st.session_state.page = "editor"
        st.rerun()

    st.stop()


# =========================================================
# EDITOR
# =========================================================

if st.session_state.page == "editor":

    project = st.session_state.project

    st.title(project.project_name)

    st.write("선거일:", project.election_date)
    st.write("후보:", project.candidate_names)

    # -----------------------------------------------------
    # Poll 입력
    # -----------------------------------------------------

    st.header("여론조사 입력")

    with st.form("poll_form"):

        pollster = st.text_input("조사기관")
        start_date = st.date_input("시작일")
        end_date = st.date_input("종료일")
        sample_size = st.number_input("표본수", 1, 100000, 1000)

        st.subheader("후보 지지율")

        supports = {}

        for c in project.candidate_names:

            supports[c] = st.number_input(
                f"{c}",
                0.0,
                100.0,
                0.0
            )

        st.subheader("무당층 선호")

        undecided_pref = {}

        for c in project.candidate_names:

            undecided_pref[c] = st.number_input(
                f"{c} 선호",
                0.0,
                100.0,
                0.0
            )

        undecided = max(
            0.0,
            100 - sum(supports.values())
        )

        submitted = st.form_submit_button("추가")

        if submitted:

            poll = Poll(

                pollster=pollster,
                start_date=str(start_date),
                end_date=str(end_date),
                sample_size=sample_size,
                supports=supports,
                undecided=undecided,
                undecided_preferences=undecided_pref

            )

            project.add_poll(poll)

            st.success("추가 완료")

    # -----------------------------------------------------
    # 저장
    # -----------------------------------------------------

    if st.button("저장"):

        save_project(project)
        st.success("저장 완료")

    # -----------------------------------------------------
    # 실행
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # 결과 출력
    # -----------------------------------------------------

    result = st.session_state.result

    if result:

        st.header("결과")

        st.dataframe(
            result["prediction_table"],
            use_container_width=True
        )

        st.subheader("승률")

        st.dataframe(
            result["win_rates"]
        )

        st.plotly_chart(
            prediction_bar_chart(
                result["prediction_table"]
            ),
            use_container_width=True
        )

        st.plotly_chart(
            win_rate_chart(
                result["win_rates"]
            ),
            use_container_width=True
        )

        st.plotly_chart(
            world_distribution_chart(
                result["worlds"],
                project.candidate_names
            ),
            use_container_width=True
        )

        st.plotly_chart(
            candidate_boxplot(
                result["worlds"],
                project.candidate_names
            ),
            use_container_width=True
        )

        st.plotly_chart(
            trend_chart(
                df,
                project.candidate_names
            ),
            use_container_width=True
        )

        st.plotly_chart(
            winner_distribution_chart(
                result["worlds"]
            ),
            use_container_width=True
        )

        st.plotly_chart(
            fte_probability_chart(
                result["worlds"],
                project.candidate_names
            ),
            use_container_width=True
        )

        st.header("가능세계")

        render_world_table(
            result["worlds"],
            project.candidate_names
        )

        render_single_world(
            result["worlds"],
            project.candidate_names
        )

        render_winner_summary(
            result["worlds"]
        )

        render_candidate_extremes(
            result["worlds"],
            project.candidate_names
        )
