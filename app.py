# =========================================================
# ULTIMATE ADAPTIVE BAYESIAN ELECTION PREDICTOR
# FiveThirtyEight Style Edition
# FULL FINAL VERSION
# =========================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from pykalman import KalmanFilter
from datetime import timedelta
import json
import os

# =========================================================
# PAGE
# =========================================================

st.set_page_config(
    page_title="Adaptive Bayesian Election Predictor",
    layout="wide"
)

st.title("Adaptive Bayesian Election Predictor")

# =========================================================
# SAVE SYSTEM
# =========================================================

SAVE_DIR = "saved_simulations"

os.makedirs(SAVE_DIR, exist_ok=True)

# =========================================================
# SESSION
# =========================================================

if "polls" not in st.session_state:
    st.session_state.polls = []

if "candidates" not in st.session_state:
    st.session_state.candidates = []

# =========================================================
# MENU
# =========================================================

menu = st.sidebar.radio(
    "메뉴",
    [
        "새 시뮬레이션",
        "저장된 시뮬레이션 불러오기"
    ]
)

# =========================================================
# LOAD
# =========================================================

if menu == "저장된 시뮬레이션 불러오기":

    saved_files = [
        f.replace(".json", "")
        for f in os.listdir(SAVE_DIR)
        if f.endswith(".json")
    ]

    if len(saved_files) == 0:

        st.warning("저장된 시뮬레이션 없음")
        st.stop()

    selected_file = st.sidebar.selectbox(
        "불러올 시뮬레이션",
        saved_files
    )

    with open(
        f"{SAVE_DIR}/{selected_file}.json",
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    st.session_state.polls = data["polls"]
    st.session_state.candidates = data["candidates"]

    if st.sidebar.button("시뮬레이션 삭제"):

        os.remove(
            f"{SAVE_DIR}/{selected_file}.json"
        )

        st.success("삭제 완료")
        st.stop()

# =========================================================
# CANDIDATES
# =========================================================

st.sidebar.header("후보 관리")

candidate_input = st.sidebar.text_input(
    "후보 이름"
)

if st.sidebar.button("후보 추가"):

    if candidate_input.strip():

        st.session_state.candidates.append(
            candidate_input.strip()
        )

candidates = st.session_state.candidates

if len(candidates) == 0:

    st.info("후보를 추가하세요.")
    st.stop()

st.write("현재 후보:", candidates)

# =========================================================
# POLL INPUT
# =========================================================

st.header("여론조사 추가")

pollster = st.text_input("조사기관")

col1, col2 = st.columns(2)

with col1:
    start_date = st.date_input("조사 시작일")

with col2:
    end_date = st.date_input("조사 종료일")

sample_size = st.number_input(
    "표본 수",
    min_value=1,
    value=1000
)

st.subheader("후보 지지율")

support_data = {}

for c in candidates:

    support_data[c] = st.number_input(
        f"{c} 지지율",
        min_value=0.0,
        max_value=100.0,
        value=0.0,
        key=f"support_{c}"
    )

st.subheader("무당층 내부 선호")

pref_data = {}

for c in candidates:

    pref_data[c] = st.number_input(
        f"{c} 무당층 선호",
        min_value=0.0,
        max_value=100.0,
        value=0.0,
        key=f"pref_{c}"
    )

# =========================================================
# ADD POLL
# =========================================================

if st.button("여론조사 추가"):

    undecided = max(
        0,
        100 - sum(support_data.values())
    )

    poll = {
        "pollster": pollster,
        "start_date": str(start_date),
        "end_date": str(end_date),
        "sample_size": sample_size,
        "undecided": undecided
    }

    for c in candidates:

        poll[c] = support_data[c]
        poll[f"{c}_pref"] = pref_data[c]

    st.session_state.polls.append(poll)

# =========================================================
# POLL TABLE
# =========================================================

polls = st.session_state.polls

if len(polls) > 0:

    st.header("여론조사 목록")

    df_display = pd.DataFrame(polls)

    st.dataframe(df_display)

    delete_idx = st.number_input(
        "삭제할 조사 번호",
        min_value=0,
        max_value=len(polls)-1,
        value=0
    )

    if st.button("조사 삭제"):

        st.session_state.polls.pop(delete_idx)

        st.rerun()

# =========================================================
# SAVE
# =========================================================

st.header("시뮬레이션 저장")

save_name = st.text_input(
    "저장 이름"
)

if st.button("저장"):

    save_data = {
        "candidates": candidates,
        "polls": polls
    }

    with open(
        f"{SAVE_DIR}/{save_name}.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            save_data,
            f,
            ensure_ascii=False,
            indent=4
        )

    st.success("저장 완료")

# =========================================================
# FUNCTIONS
# =========================================================

def calculate_se(p, n):

    p = p / 100

    return np.sqrt(
        max(
            p * (1-p) / n,
            1e-6
        )
    ) * 100

# =========================================================
# AUTO R/Q
# =========================================================

def calculate_auto_r_q(df, variable):

    temp = df.sort_values(
        "end_date"
    )

    values = temp[variable].values

    if len(values) < 2:

        return 2.0, 1.0

    std = np.std(values)

    R = np.clip(
        1 + std/2,
        0.5,
        8
    )

    first = values[0]
    last = values[-1]

    dates = pd.to_datetime(
        temp["end_date"]
    )

    days = max(
        (
            dates.iloc[-1]
            -
            dates.iloc[0]
        ).days,
        1
    )

    slope = abs(last-first)/days

    Q = np.clip(
        0.5 + slope*5,
        0.1,
        5
    )

    return R, Q

# =========================================================
# KALMAN TREND
# =========================================================

def kalman_trend(values):

    kf = KalmanFilter(
        initial_state_mean=values[0],
        n_dim_obs=1
    )

    state_means, _ = kf.filter(values)

    return state_means.flatten()

# =========================================================
# RUN
# =========================================================

if st.button("예측 실행"):

    if len(polls) < 2:

        st.warning("여론조사 2개 이상 필요")
        st.stop()

    df = pd.DataFrame(polls)

    df["end_date"] = pd.to_datetime(
        df["end_date"]
    )

    df = df.sort_values("end_date")

    election_day = (
        df["end_date"].max()
        +
        timedelta(days=14)
    )

    NUM_SIMULATIONS = 100

    world_results = []

    final_results = {
        c: []
        for c in candidates
    }

    win_counts = {
        c: 0
        for c in candidates
    }

    # =====================================================
    # TREND GRAPH
    # =====================================================

    trend_fig = go.Figure()

    for c in candidates:

        trend = kalman_trend(
            df[c].values
        )

        x = np.arange(len(trend))

        model = LinearRegression()

        model.fit(
            x.reshape(-1,1),
            trend
        )

        future_days = (
            election_day
            -
            df["end_date"].max()
        ).days

        future_x = np.arange(
            len(trend),
            len(trend)+future_days
        )

        future_trend = model.predict(
            future_x.reshape(-1,1)
        )

        trend_fig.add_trace(
            go.Scatter(
                x=df["end_date"],
                y=trend,
                mode="lines",
                name=f"{c} 추세"
            )
        )

        future_dates = pd.date_range(
            start=df["end_date"].max(),
            periods=future_days,
            freq="D"
        )

        trend_fig.add_trace(
            go.Scatter(
                x=future_dates,
                y=future_trend,
                mode="lines",
                line=dict(dash="dash"),
                name=f"{c} 미래"
            )
        )

    # =====================================================
    # UNDECIDED TREND
    # =====================================================

    undecided_trend = kalman_trend(
        df["undecided"].values
    )

    trend_fig.add_trace(
        go.Scatter(
            x=df["end_date"],
            y=undecided_trend,
            mode="lines",
            name="무당층 추세"
        )
    )

    trend_fig.update_layout(

        title="지지율 추세",

        yaxis=dict(
            range=[
                0,
                max(
                    df[candidates].max()
                ) + 5
            ]
        )
    )

    st.plotly_chart(
        trend_fig,
        use_container_width=True
    )

    # =====================================================
    # MONTE CARLO
    # =====================================================

    for sim in range(NUM_SIMULATIONS):

        final_dict = {}

        # =================================================
        # UNDECIDED WORLD TREND
        # =================================================

        undecided_world = []

        R_u, Q_u = calculate_auto_r_q(
            df,
            "undecided"
        )

        for u in undecided_trend:

            se_u = calculate_se(
                max(u, 0.1),
                np.mean(df["sample_size"])
            ) * R_u

            sampled_u = np.random.normal(
                u,
                se_u
            )

            sampled_u = max(
                0,
                sampled_u
            )

            undecided_world.append(
                sampled_u
            )

        future_undecided = np.mean(
            undecided_world[-3:]
        )

        # =================================================
        # CANDIDATES
        # =================================================

        for c in candidates:

            R, Q = calculate_auto_r_q(
                df,
                c
            )

            candidate_trend = kalman_trend(
                df[c].values
            )

            sampled_world = []

            for i, row in df.iterrows():

                trend_value = candidate_trend[i]

                se = calculate_se(
                    trend_value,
                    row["sample_size"]
                ) * R

                sampled_support = np.random.normal(
                    trend_value,
                    se
                )

                sampled_support = max(
                    0,
                    sampled_support
                )

                undecided_n = max(
                    row["sample_size"]
                    *
                    (
                        row["undecided"]
                        /
                        100
                    ),
                    1
                )

                pref = row[f"{c}_pref"]

                pref_se = calculate_se(
                    pref,
                    undecided_n
                ) * R

                sampled_pref = np.random.normal(
                    pref,
                    pref_se
                )

                sampled_pref = np.clip(
                    sampled_pref,
                    0,
                    100
                )

                momentum = np.random.normal(
                    0,
                    Q
                )

                value = (
                    sampled_support
                    +
                    future_undecided
                    *
                    (
                        sampled_pref
                        / 100
                    )
                    +
                    momentum
                )

                sampled_world.append(value)

            weighted_sum = 0
            weight_total = 0

            for i, row in df.iterrows():

                days_ago = (
                    election_day
                    -
                    row["end_date"]
                ).days

                decay = np.exp(
                    -0.03 * days_ago
                )

                weighted_sum += (
                    sampled_world[i]
                    *
                    decay
                )

                weight_total += decay

            prediction = (
                weighted_sum
                /
                weight_total
            )

            prediction = max(
                0,
                prediction
            )

            final_dict[c] = prediction

        # =================================================
        # NORMALIZATION
        # =================================================

        total = sum(
            final_dict.values()
        )

        if total <= 0:

            total = 1

        for c in candidates:

            final_dict[c] = (
                final_dict[c]
                /
                total
            ) * 100

            final_dict[c] = max(
                0,
                final_dict[c]
            )

            final_results[c].append(
                final_dict[c]
            )

        winner = max(
            final_dict,
            key=final_dict.get
        )

        win_counts[winner] += 1

        world_results.append(
            {
                "world": sim + 1,
                "results": final_dict.copy()
            }
        )

    # =====================================================
    # FINAL RESULTS
    # =====================================================

    st.header("최종 예측")

    result_table = []

    for c in candidates:

        avg = np.mean(
            final_results[c]
        )

        lower = np.percentile(
            final_results[c],
            5
        )

        upper = np.percentile(
            final_results[c],
            95
        )

        win_rate = (
            win_counts[c]
            /
            NUM_SIMULATIONS
        ) * 100

        result_table.append(
            {
                "후보": c,
                "예상 득표율": round(avg,2),
                "5% 하한": round(lower,2),
                "95% 상한": round(upper,2),
                "승률": round(win_rate,2)
            }
        )

    result_df = pd.DataFrame(
        result_table
    )

    st.dataframe(result_df)

    # =====================================================
    # FIVE THIRTY EIGHT STYLE
    # =====================================================

    st.markdown("---")

    st.header("가능한 미래 시나리오")

    selected_world = st.selectbox(
        "World 선택",
        [
            w["world"]
            for w in world_results
        ]
    )

    selected_data = next(
        w for w in world_results
        if w["world"] == selected_world
    )

    world_df = pd.DataFrame(
        {
            "후보": list(
                selected_data["results"].keys()
            ),
            "득표율": list(
                selected_data["results"].values()
            )
        }
    )

    st.dataframe(world_df)

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=world_df["후보"],
            y=world_df["득표율"]
        )
    )

    fig.update_layout(

        title=f"World {selected_world}",

        yaxis=dict(
            range=[
                0,
                max(
                    world_df["득표율"]
                ) + 5
            ]
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    winner = max(
        selected_data["results"],
        key=selected_data["results"].get
    )

    st.success(
        f"예상 승리 후보: {winner}"
    )
