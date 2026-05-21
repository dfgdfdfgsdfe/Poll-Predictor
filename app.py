# =========================================================
# 실전형 선거예측 시스템
# Ultimate Bayesian Edition
# =========================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from sklearn.linear_model import LinearRegression
from filterpy.kalman import KalmanFilter

import json
import os

# =========================================================
# 기본 설정
# =========================================================

st.set_page_config(
    page_title="Ultimate Election Predictor",
    layout="wide"
)

SAVE_DIR = "saved_simulations"

os.makedirs(
    SAVE_DIR,
    exist_ok=True
)

# =========================================================
# 세션 상태
# =========================================================

if "page" not in st.session_state:
    st.session_state.page = "menu"

if "simulation_name" not in st.session_state:
    st.session_state.simulation_name = ""

if "candidate_names" not in st.session_state:
    st.session_state.candidate_names = []

if "polls" not in st.session_state:
    st.session_state.polls = []

# =========================================================
# 메뉴
# =========================================================

if st.session_state.page == "menu":

    st.title("Ultimate Bayesian Election Predictor")

    st.markdown("""
    ## 기능

    - House Effect 제거
    - Time Decay
    - Dynamic R
    - Kalman Filter
    - Bayesian Poll Worlds
    - Nested Monte Carlo
    - 무당층 독립 추세
    - 승률 계산
    - 미래 예측 점선
    """)

    col1, col2 = st.columns(2)

    with col1:

        if st.button("새 시뮬레이션"):

            st.session_state.page = "new"

            st.rerun()

    with col2:

        if st.button("불러오기"):

            st.session_state.page = "load"

            st.rerun()

    st.stop()

# =========================================================
# 새 시뮬레이션
# =========================================================

if st.session_state.page == "new":

    st.title("새 시뮬레이션")

    sim_name = st.text_input(
        "시뮬레이션 이름"
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button("생성"):

            if sim_name.strip() == "":

                st.error("이름 입력")

            else:

                st.session_state.simulation_name = sim_name

                st.session_state.candidate_names = []

                st.session_state.polls = []

                st.session_state.page = "main"

                st.rerun()

    with col2:

        if st.button("← 뒤로가기"):

            st.session_state.page = "menu"

            st.rerun()

    st.stop()

# =========================================================
# 불러오기
# =========================================================

if st.session_state.page == "load":

    st.title("불러오기")

    saved_files = [

        f.replace(".json","")

        for f in os.listdir(SAVE_DIR)

        if f.endswith(".json")
    ]

    if len(saved_files) == 0:

        st.warning("저장된 시뮬레이션 없음")

    else:

        selected = st.selectbox(
            "선택",
            saved_files
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            if st.button("불러오기"):

                with open(
                    f"{SAVE_DIR}/{selected}.json",
                    "r",
                    encoding="utf-8"
                ) as f:

                    data = json.load(f)

                st.session_state.simulation_name = data["simulation_name"]

                st.session_state.candidate_names = data["candidate_names"]

                st.session_state.polls = data["polls"]

                st.session_state.page = "main"

                st.rerun()

        with col2:

            if st.button("삭제"):

                os.remove(
                    f"{SAVE_DIR}/{selected}.json"
                )

                st.success("삭제 완료")

                st.rerun()

        with col3:

            if st.button("← 뒤로가기"):

                st.session_state.page = "menu"

                st.rerun()

    st.stop()

# =========================================================
# 메인
# =========================================================

if st.session_state.page == "main":

    st.title(
        f"{st.session_state.simulation_name}"
    )

    # =====================================================
    # 메뉴
    # =====================================================

    nav1, nav2 = st.columns(2)

    with nav1:

        if st.button("← 메인 메뉴"):

            st.session_state.page = "menu"

            st.rerun()

    with nav2:

        if st.button("현재 시뮬레이션 삭제"):

            path = (
                f"{SAVE_DIR}/"
                f"{st.session_state.simulation_name}.json"
            )

            if os.path.exists(path):

                os.remove(path)

            st.session_state.page = "menu"

            st.rerun()

    # =====================================================
    # 후보
    # =====================================================

    st.header("1. 후보 설정")

    candidate_count = st.slider(
        "후보 수",
        1,
        5,
        max(
            2,
            len(st.session_state.candidate_names)
        )
    )

    candidate_names = []

    cols = st.columns(candidate_count)

    for i in range(candidate_count):

        default_name = ""

        if i < len(st.session_state.candidate_names):

            default_name = (
                st.session_state.candidate_names[i]
            )

        with cols[i]:

            name = st.text_input(
                f"후보 {i+1}",
                value=default_name,
                key=f"candidate_{i}"
            )

            if name.strip() != "":

                candidate_names.append(
                    name.strip()
                )

    st.session_state.candidate_names = candidate_names

    # =====================================================
    # 선거일
    # =====================================================

    st.header("2. 선거일")

    election_day = st.date_input(
        "선거일"
    )

    # =====================================================
    # 설정
    # =====================================================

    st.header("3. 엔진 설정")

    trust_level = st.select_slider(
        "여론조사 신뢰도",
        options=[
            "매우 낮음",
            "낮음",
            "보통",
            "높음",
            "매우 높음"
        ],
        value="보통"
    )

    trend_sensitivity = st.select_slider(
        "민심 변화 민감도",
        options=[
            "매우 낮음",
            "낮음",
            "보통",
            "높음",
            "매우 높음"
        ],
        value="보통"
    )

    time_decay_strength = st.select_slider(
        "최신 조사 반영도",
        options=[
            "매우 낮음",
            "낮음",
            "보통",
            "높음",
            "매우 높음"
        ],
        value="높음"
    )

    world_count = st.select_slider(
        "Bayesian World 수",
        options=[
            100,
            500,
            1000,
            3000,
            5000
        ],
        value=1000
    )

    # =====================================================
    # 매핑
    # =====================================================

    R_MAP = {

        "매우 낮음": 8.0,
        "낮음": 4.0,
        "보통": 2.0,
        "높음": 1.0,
        "매우 높음": 0.5
    }

    Q_MAP = {

        "매우 낮음": 0.01,
        "낮음": 0.03,
        "보통": 0.05,
        "높음": 0.1,
        "매우 높음": 0.2
    }

    DECAY_MAP = {

        "매우 낮음": 0.003,
        "낮음": 0.007,
        "보통": 0.015,
        "높음": 0.03,
        "매우 높음": 0.05
    }

    BASE_R = R_MAP[trust_level]

    Q_VALUE = Q_MAP[trend_sensitivity]

    LAMBDA = DECAY_MAP[time_decay_strength]

    # =====================================================
    # 여론조사 입력
    # =====================================================

    st.header("4. 여론조사 입력")

    with st.form("poll_form"):

        pollster = st.text_input(
            "조사기관"
        )

        col1, col2 = st.columns(2)

        with col1:

            start_date = st.date_input(
                "조사 시작일"
            )

        with col2:

            end_date = st.date_input(
                "조사 종료일"
            )

        sample_size = st.number_input(
            "표본 수",
            min_value=1,
            value=1000
        )

        st.subheader("후보 지지율")

        supports = {}

        cols = st.columns(
            max(1, len(candidate_names))
        )

        for idx, c in enumerate(candidate_names):

            with cols[idx]:

                val = st.number_input(
                    f"{c} (%)",
                    min_value=0.0,
                    max_value=100.0,
                    step=0.1,
                    key=f"support_{c}"
                )

                supports[c] = val

        undecided = (
            100
            -
            sum(supports.values())
        )

        undecided = max(
            undecided,
            0
        )

        st.info(
            f"자동 계산 무당층: "
            f"{round(undecided,2)}%"
        )

        st.subheader("무당층 내부 선호")

        undecided_pref = {}

        cols2 = st.columns(
            max(1, len(candidate_names))
        )

        for idx, c in enumerate(candidate_names):

            with cols2[idx]:

                pref = st.number_input(
                    f"{c} 선호 (%)",
                    min_value=0.0,
                    max_value=100.0,
                    step=0.1,
                    key=f"pref_{c}"
                )

                undecided_pref[c] = pref

        add_poll = st.form_submit_button(
            "여론조사 추가"
        )

        if add_poll:

            st.session_state.polls.append({

                "pollster": pollster,

                "start_date": str(start_date),

                "end_date": str(end_date),

                "sample_size": sample_size,

                "supports": supports,

                "undecided": undecided,

                "undecided_pref": undecided_pref
            })

            st.success("추가 완료")

    # =====================================================
    # 조사 목록
    # =====================================================

    st.header("5. 입력된 조사")

    delete_index = None

    for idx, poll in enumerate(
        st.session_state.polls
    ):

        with st.expander(
            f"{poll['pollster']} "
            f"| {poll['end_date']}"
        ):

            st.write(
                f"표본수: "
                f"{poll['sample_size']}"
            )

            st.json(
                poll["supports"]
            )

            st.json(
                poll["undecided_pref"]
            )

            if st.button(
                f"삭제 {idx}",
                key=f"delete_{idx}"
            ):

                delete_index = idx

    if delete_index is not None:

        st.session_state.polls.pop(
            delete_index
        )

        st.rerun()

    # =====================================================
    # 저장
    # =====================================================

    st.header("6. 저장")

    if st.button("시뮬레이션 저장"):

        data = {

            "simulation_name":
                st.session_state.simulation_name,

            "candidate_names":
                st.session_state.candidate_names,

            "polls":
                st.session_state.polls
        }

        with open(
            f"{SAVE_DIR}/"
            f"{st.session_state.simulation_name}.json",
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=4
            )

        st.success("저장 완료")

    # =====================================================
    # 예측 실행
    # =====================================================

    st.header("7. 예측")

    RUN = st.button(
        "Ultimate Bayesian Simulation 실행"
    )

    if RUN:

        if len(st.session_state.polls) < 2:

            st.error("최소 2개 조사 필요")

            st.stop()

        rows = []

        for poll in st.session_state.polls:

            row = {

                "pollster": poll["pollster"],

                "end_date": pd.to_datetime(
                    poll["end_date"]
                ),

                "sample_size": poll["sample_size"],

                "undecided": poll["undecided"]
            }

            for c in candidate_names:

                row[c] = poll["supports"][c]

                row[f"{c}_pref"] = (

                    poll["undecided_pref"][c]
                )

            rows.append(row)

        df = pd.DataFrame(rows)

        df = df.sort_values(
            "end_date"
        )

        latest_date = df["end_date"].max()

        df["days_old"] = (

            latest_date
            -
            df["end_date"]

        ).dt.days

        df["time_weight"] = np.exp(
            -LAMBDA * df["days_old"]
        )

        # =================================================
        # House Effect 제거
        # =================================================

        for c in candidate_names:

            overall_mean = np.average(
                df[c],
                weights=(
                    df["sample_size"]
                    *
                    df["time_weight"]
                )
            )

            pollster_mean = (

                df.groupby("pollster")

                .apply(

                    lambda x:

                    np.average(

                        x[c],

                        weights=(
                            x["sample_size"]
                            *
                            x["time_weight"]
                        )
                    )
                )
            )

            house_effect = (
                pollster_mean
                - overall_mean
            )

            df[f"{c}_adjusted"] = (

                df[c]

                -

                df["pollster"].map(
                    house_effect
                )
            )

        # =================================================
        # Kalman
        # =================================================

        def run_kalman(values, r_values):

            kf = KalmanFilter(
                dim_x=2,
                dim_z=1
            )

            kf.x = np.array([
                values.iloc[0],
                0
            ])

            kf.F = np.array([
                [1,1],
                [0,1]
            ])

            kf.H = np.array([
                [1,0]
            ])

            kf.P *= 1000

            kf.Q = np.array([
                [Q_VALUE,0],
                [0,Q_VALUE]
            ])

            filtered = []

            for idx, value in enumerate(values):

                kf.R = r_values.iloc[idx]

                kf.predict()

                kf.update(value)

                filtered.append(
                    float(kf.x[0])
                )

            return filtered

        # =================================================
        # Bayesian Worlds
        # =================================================

        world_predictions = {

            c: []

            for c in candidate_names
        }

        progress = st.progress(0)

        for world in range(world_count):

            for c in candidate_names:

                temp = (
                    df.groupby("end_date")
                    .mean(numeric_only=True)
                    .reset_index()
                )

                temp = temp.sort_values(
                    "end_date"
                )

                dynamic_r = []

                for idx, row in temp.iterrows():

                    p = row[f"{c}_adjusted"] / 100

                    n = max(
                        row["sample_size"],
                        1
                    )

                    se = np.sqrt(
                        (p * (1-p)) / n
                    )

                    se = max(
                        se,
                        0.0001
                    )

                    r_value = (
                        (se * 100)**2
                    ) * BASE_R

                    dynamic_r.append(
                        r_value
                    )

                temp["dynamic_r"] = dynamic_r

                sampled_supports = []

                sampled_prefs = []

                sampled_undecided = []

                for idx, row in temp.iterrows():

                    se = np.sqrt(
                        row["dynamic_r"]
                    )

                    sampled_supports.append(

                        np.random.normal(
                            row[f"{c}_adjusted"],
                            se
                        )
                    )

                    sampled_prefs.append(

                        np.random.normal(
                            row[f"{c}_pref"],
                            se
                        )
                    )

                    sampled_undecided.append(

                        np.random.normal(
                            row["undecided"],
                            se
                        )
                    )

                temp["sampled_support"] = np.clip(
                    sampled_supports,
                    0,
                    100
                )

                temp["sampled_pref"] = np.clip(
                    sampled_prefs,
                    0,
                    100
                )

                temp["sampled_undecided"] = np.clip(
                    sampled_undecided,
                    0,
                    100
                )

                temp["support_kalman"] = (

                    run_kalman(
                        temp["sampled_support"],
                        temp["dynamic_r"]
                    )
                )

                temp["pref_kalman"] = (

                    run_kalman(
                        temp["sampled_pref"],
                        temp["dynamic_r"]
                    )
                )

                temp["undecided_kalman"] = (

                    run_kalman(
                        temp["sampled_undecided"],
                        temp["dynamic_r"]
                    )
                )

                temp["date_num"] = (

                    temp["end_date"]

                    -

                    temp["end_date"].min()

                ).dt.days

                X = temp[["date_num"]]

                support_model = LinearRegression()

                pref_model = LinearRegression()

                undecided_model = LinearRegression()

                support_model.fit(
                    X,
                    temp["support_kalman"]
                )

                pref_model.fit(
                    X,
                    temp["pref_kalman"]
                )

                undecided_model.fit(
                    X,
                    temp["undecided_kalman"]
                )

                election_num = (

                    pd.to_datetime(election_day)

                    -

                    temp["end_date"].min()

                ).days

                core_support = (

                    support_model.predict(
                        [[election_num]]
                    )[0]
                )

                undecided_size = (

                    undecided_model.predict(
                        [[election_num]]
                    )[0]
                )

                undecided_pref = (

                    pref_model.predict(
                        [[election_num]]
                    )[0]
                )

                final_prediction = (

                    core_support

                    +

                    (
                        undecided_size

                        *

                        (
                            undecided_pref / 100
                        )
                    )
                )

                final_prediction = np.clip(
                    final_prediction,
                    0,
                    100
                )

                world_predictions[c].append(
                    final_prediction
                )

            progress.progress(
                (world + 1) / world_count
            )

        # =================================================
        # 평균 계산
        # =================================================

        final_results = []

        for c in candidate_names:

            sims = np.array(
                world_predictions[c]
            )

            final_results.append({

                "candidate": c,

                "prediction": np.mean(sims),

                "lower": np.percentile(
                    sims,
                    2.5
                ),

                "upper": np.percentile(
                    sims,
                    97.5
                ),

                "all_sims": sims
            })

        total = sum(
            x["prediction"]
            for x in final_results
        )

        for r in final_results:

            r["prediction"] = (

                r["prediction"]

                /

                total

            ) * 100

        # =================================================
        # 승률
        # =================================================

        win_counts = {
            c: 0
            for c in candidate_names
        }

        for i in range(world_count):

            sample = {}

            for r in final_results:

                sample[
                    r["candidate"]
                ] = r["all_sims"][i]

            total = sum(sample.values())

            for k in sample:

                sample[k] = (
                    sample[k]
                    / total
                ) * 100

            winner = max(
                sample,
                key=sample.get
            )

            win_counts[winner] += 1

        # =================================================
        # 결과표
        # =================================================

        st.header("8. 결과")

        rows = []

        for r in final_results:

            win_rate = (

                win_counts[r["candidate"]]

                /

                world_count

            ) * 100

            rows.append({

                "후보":
                    r["candidate"],

                "예상 득표율":
                    round(r["prediction"],2),

                "승률":
                    round(win_rate,2),

                "95% 하한":
                    round(r["lower"],2),

                "95% 상한":
                    round(r["upper"],2)
            })

        result_df = pd.DataFrame(rows)

        result_df = result_df.sort_values(
            "예상 득표율",
            ascending=False
        )

        st.dataframe(
            result_df,
            use_container_width=True
        )
# =================================================
# 그래프
# =================================================

st.header("9. 추세 그래프")

fig = go.Figure()

all_max = []

for c in candidate_names:

    temp = (
        df.groupby("end_date")
        .mean(numeric_only=True)
        .reset_index()
    )

    temp = temp.sort_values("end_date")

    dynamic_r = []

    for idx, row in temp.iterrows():

        p = row[f"{c}_adjusted"] / 100

        n = max(row["sample_size"], 1)

        se = np.sqrt((p * (1-p)) / n)

        se = max(se, 0.0001)

        r_value = ((se * 100)**2) * BASE_R

        dynamic_r.append(r_value)

    temp["dynamic_r"] = dynamic_r

    kalman_values = run_kalman(
        temp[f"{c}_adjusted"],
        temp["dynamic_r"]
    )

    temp["kalman"] = kalman_values

    temp["date_num"] = (
        temp["end_date"]
        -
        temp["end_date"].min()
    ).dt.days

    X = temp[["date_num"]]

    model = LinearRegression()

    model.fit(
        X,
        temp["kalman"]
    )

    future_dates = pd.date_range(
        start=temp["end_date"].min(),
        end=pd.to_datetime(election_day),
        freq="D"
    )

    future_num = (
        future_dates
        -
        temp["end_date"].min()
    ).days.values.reshape(-1,1)

    preds = model.predict(future_num)

    all_max.extend(preds)

    # =============================
    # 실제 데이터 점
    # =============================

    fig.add_trace(

        go.Scatter(

            x=temp["end_date"],

            y=temp[f"{c}_adjusted"],

            mode="markers",

            name=f"{c} 실제조사"
        )
    )

    # =============================
    # Kalman 추세 실선
    # =============================

    fig.add_trace(

        go.Scatter(

            x=temp["end_date"],

            y=temp["kalman"],

            mode="lines",

            name=f"{c} 추세"
        )
    )

    # =============================
    # 미래 예측 점선
    # =============================

    future_mask = (
        future_dates
        >
        temp["end_date"].max()
    )

    fig.add_trace(

        go.Scatter(

            x=future_dates[future_mask],

            y=preds[future_mask],

            mode="lines",

            line=dict(
                dash="dash"
            ),

            name=f"{c} 미래예측"
        )
    )

    # =============================
    # 신뢰구간 밴드
    # =============================

    sims = np.array(
        world_predictions[c]
    )

    spread = np.std(sims)

    upper = preds + spread

    lower = preds - spread

    lower = np.clip(
        lower,
        0,
        100
    )

    fig.add_trace(

        go.Scatter(

            x=list(future_dates)
              +
              list(future_dates[::-1]),

            y=list(upper)
              +
              list(lower[::-1]),

            fill="toself",

            opacity=0.15,

            line=dict(width=0),

            showlegend=False
        )
    )

# =================================================
# Y축 자동 설정
# =================================================

max_y = max(all_max) + 5

max_y = min(max_y, 100)

fig.update_layout(

    height=700,

    yaxis=dict(
        range=[0, max_y]
    ),

    xaxis_title="날짜",

    yaxis_title="지지율 (%)",

    hovermode="x unified"
)

st.plotly_chart(
    fig,
    use_container_width=True
)
