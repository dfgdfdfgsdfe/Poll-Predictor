# =========================================================
# 실전형 선거예측 시스템 Ultimate Edition
# =========================================================
#
# 주요 기능
#
# - 후보 1~5명
# - 여론조사 무제한 입력
# - 저장 / 불러오기
# - 여론조사 수정 / 삭제
# - 날짜 자동 정렬
# - House Effect 제거
# - 시간 가중치(Time Decay)
# - 표본오차 자동 계산
# - 조사별 Dynamic R
# - Kalman Filter
# - 무당층 자동 계산
# - 무당층 독립 추세
# - 무당층 내부 선호 독립 추세
# - 불확실성 기반 추세
# - Monte Carlo 시뮬레이션
# - 승률 계산
# - 신뢰구간 계산
# - 미래 점선 예측
# - 추세 밴드 시각화
#
# =========================================================

import streamlit as st
import pandas as pd
import numpy as np

from sklearn.linear_model import LinearRegression
from filterpy.kalman import KalmanFilter

import plotly.graph_objects as go

import json
import os

# =========================================================
# [추가 1] 뒤로가기용 페이지 상태
# =========================================================

if "page" not in st.session_state:
    st.session_state.page = "menu"

# =========================================================
# [추가 2] 메인 메뉴
# =========================================================

if st.session_state.page == "menu":

    st.title("실전형 선거예측 시스템")

    st.markdown("## 메인 메뉴")

    col1, col2 = st.columns(2)

    with col1:

        if st.button("새 시뮬레이션"):

            st.session_state.page = "new"

            st.rerun()

    with col2:

        if st.button("저장된 시뮬레이션 불러오기"):

            st.session_state.page = "load"

            st.rerun()

    st.stop()

# =========================================================
# [추가 3] 새 시뮬레이션 페이지
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
# [추가 4] 불러오기 페이지
# =========================================================

if st.session_state.page == "load":

    st.title("시뮬레이션 불러오기")

    saved_files = [

        f.replace(".json","")

        for f in os.listdir(SAVE_DIR)

        if f.endswith(".json")
    ]

    if len(saved_files) == 0:

        st.warning("저장된 시뮬레이션 없음")

    else:

        selected = st.selectbox(
            "불러올 시뮬레이션",
            saved_files
        )

        col1, col2, col3 = st.columns(3)

        # =================================================
        # 불러오기
        # =================================================

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

        # =================================================
        # 삭제 기능
        # =================================================

        with col2:

            if st.button("시뮬레이션 삭제"):

                os.remove(
                    f"{SAVE_DIR}/{selected}.json"
                )

                st.success("삭제 완료")

                st.rerun()

        # =================================================
        # 뒤로가기
        # =================================================

        with col3:

            if st.button("← 뒤로가기"):

                st.session_state.page = "menu"

                st.rerun()

    st.stop()

# =========================================================
# [추가 5] 메인 시스템 페이지
# =========================================================

if st.session_state.page == "main":

    st.title(
        f"실전형 선거예측 시스템 "
        f"- {st.session_state.simulation_name}"
    )

    # =====================================================
    # 상단 네비게이션
    # =====================================================

    nav1, nav2 = st.columns(2)

    with nav1:

        if st.button("← 메인 메뉴"):

            st.session_state.page = "menu"

            st.rerun()

    with nav2:

        if st.button("현재 시뮬레이션 삭제"):

            file_path = (
                f"{SAVE_DIR}/"
                f"{st.session_state.simulation_name}.json"
            )

            if os.path.exists(file_path):

                os.remove(file_path)

            st.session_state.simulation_name = ""

            st.session_state.candidate_names = []

            st.session_state.polls = []

            st.session_state.page = "menu"

            st.success("삭제 완료")

            st.rerun()

# =========================================================
# 새 시뮬레이션
# =========================================================

if menu == "새 시뮬레이션":

    sim_name = st.text_input(
        "시뮬레이션 이름"
    )

    if st.button("생성"):

        if sim_name.strip() == "":

            st.error("이름 입력")

        else:

            st.session_state.simulation_name = sim_name

            st.session_state.candidate_names = []

            st.session_state.polls = []

            st.success("생성 완료")

# =========================================================
# 불러오기
# =========================================================

else:

    saved_files = [

        f.replace(".json","")

        for f in os.listdir(SAVE_DIR)

        if f.endswith(".json")
    ]

    if len(saved_files) == 0:

        st.warning("저장된 시뮬레이션 없음")

    else:

        selected = st.selectbox(
            "불러올 시뮬레이션",
            saved_files
        )

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

            st.success("불러오기 완료")

# =========================================================
# 종료
# =========================================================

if st.session_state.simulation_name == "":

    st.stop()

# =========================================================
# 현재 시뮬레이션
# =========================================================

st.success(
    f"현재 시뮬레이션: "
    f"{st.session_state.simulation_name}"
)

# =========================================================
# 후보 입력
# =========================================================

st.header("2. 후보 입력")

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

            candidate_names.append(name.strip())

st.session_state.candidate_names = candidate_names

# =========================================================
# 선거일
# =========================================================

st.header("3. 선거일")

election_day = st.date_input(
    "선거일"
)

# =========================================================
# Kalman 옵션
# =========================================================

st.header("4. 시스템 설정")

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
    "최신 여론조사 우선 반영",
    options=[
        "매우 낮음",
        "낮음",
        "보통",
        "높음",
        "매우 높음"
    ],
    value="높음"
)

# =========================================================
# 내부 값 매핑
# =========================================================

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

# =========================================================
# 여론조사 입력
# =========================================================

st.header("5. 여론조사 입력")

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
        - sum(supports.values())
    )

    undecided = max(
        undecided,
        0
    )

    st.info(
        f"자동 계산된 무당층: "
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

# =========================================================
# 여론조사 표시
# =========================================================

st.header("6. 입력된 여론조사")

if len(st.session_state.polls) == 0:

    st.warning("입력된 조사 없음")

else:

    delete_index = None

    for idx, poll in enumerate(
        st.session_state.polls
    ):

        with st.expander(
            f"{poll['pollster']} | "
            f"{poll['end_date']}"
        ):

            st.write(
                f"표본수: "
                f"{poll['sample_size']}"
            )

            st.write(
                f"무당층: "
                f"{round(poll['undecided'],2)}%"
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

# =========================================================
# 저장
# =========================================================

st.header("7. 저장")

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

# =========================================================
# 예측 시작
# =========================================================

st.header("8. 예측")

RUN_SIMULATION = st.button(
    "예측 실행"
)

# =========================================================
# 예측 실행
# =========================================================

if RUN_SIMULATION:

    if len(candidate_names) == 0:

        st.error("후보 입력 필요")

        st.stop()

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

    df = df.sort_values("end_date")

    # =====================================================
    # Time Decay
    # =====================================================

    latest_date = df["end_date"].max()

    df["days_old"] = (

        latest_date
        -
        df["end_date"]

    ).dt.days

    df["time_weight"] = np.exp(
        -LAMBDA * df["days_old"]
    )

    # =====================================================
    # House Effect 제거
    # =====================================================

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

    # =====================================================
    # Kalman
    # =====================================================

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

    # =====================================================
    # 그래프
    # =====================================================

    fig = go.Figure()

    prediction_results = []

    # =====================================================
    # 후보별 계산
    # =====================================================

    for c in candidate_names:

        temp = (
            df.groupby("end_date")
            .mean(numeric_only=True)
            .reset_index()
        )

        temp = temp.sort_values(
            "end_date"
        )

        # =================================================
        # Dynamic R
        # =================================================

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

        # =================================================
        # 입력 자체를 랜덤화
        # =================================================

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

        # =================================================
        # Kalman
        # =================================================

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

        # =================================================
        # 날짜 숫자화
        # =================================================

        temp["date_num"] = (

            temp["end_date"]

            -

            temp["end_date"].min()

        ).dt.days

        X = temp[["date_num"]]

        # =================================================
        # 회귀
        # =================================================

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

        # =================================================
        # 미래 예측
        # =================================================

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

        core_support = np.clip(
            core_support,
            0,
            100
        )

        undecided_size = np.clip(
            undecided_size,
            0,
            100
        )

        undecided_pref = np.clip(
            undecided_pref,
            0,
            100
        )

        # =================================================
        # 최종 결합
        # =================================================

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

        # =================================================
        # 표준오차 계산
        # =================================================

        p = max(
            final_prediction / 100,
            0.0001
        )

        n = max(
            temp["sample_size"].mean(),
            1
        )

        support_se = np.sqrt(
            (p * (1-p)) / n
        )

        undecided_n = (

            n

            *

            (
                undecided_size / 100
            )
        )

        undecided_n = max(
            undecided_n,
            1
        )

        undecided_p = max(
            undecided_pref / 100,
            0.0001
        )

        undecided_se = np.sqrt(
            (
                undecided_p
                *
                (
                    1 - undecided_p
                )
            )

            /

            undecided_n
        )

        combined_se = np.sqrt(
            support_se**2
            +
            undecided_se**2
        )

        # =================================================
        # Monte Carlo
        # =================================================

        simulations = np.random.normal(
            final_prediction,
            combined_se * 100,
            10000
        )

        simulations = np.clip(
            simulations,
            0,
            100
        )

        prediction_results.append({

            "candidate": c,

            "prediction": final_prediction,

            "simulations": simulations,

            "lower": np.percentile(
                simulations,
                2.5
            ),

            "upper": np.percentile(
                simulations,
                97.5
            )
        })

        # =================================================
        # 추세선
        # =================================================

        fig.add_trace(
            go.Scatter(
                x=temp["end_date"],
                y=temp["support_kalman"],
                mode="lines+markers",
                name=f"{c} 추세"
            )
        )

        # =================================================
        # 신뢰구간 밴드
        # =================================================

        upper_band = (
            temp["support_kalman"]
            +
            np.sqrt(temp["dynamic_r"])
        )

        lower_band = (
            temp["support_kalman"]
            -
            np.sqrt(temp["dynamic_r"])
        )

        lower_band = np.clip(
            lower_band,
            0,
            100
        )

        fig.add_trace(
            go.Scatter(
                x=temp["end_date"],
                y=upper_band,
                line=dict(width=0),
                showlegend=False
            )
        )

        fig.add_trace(
            go.Scatter(
                x=temp["end_date"],
                y=lower_band,
                fill='tonexty',
                line=dict(width=0),
                opacity=0.15,
                showlegend=False
            )
        )

        # =================================================
        # 미래 점선
        # =================================================

        future_dates = pd.date_range(
            start=temp["end_date"].max(),
            end=pd.to_datetime(
                election_day
            ),
            periods=30
        )

        future_num = (

            future_dates

            -

            temp["end_date"].min()

        ).days.values.reshape(-1,1)

        future_predictions = (
            support_model.predict(
                future_num
            )
        )

        future_predictions = np.clip(
            future_predictions,
            0,
            100
        )

        fig.add_trace(
            go.Scatter(
                x=future_dates,
                y=future_predictions,
                mode="lines",
                line=dict(
                    dash="dash"
                ),
                name=f"{c} 미래"
            )
        )

    # =====================================================
    # 정규화
    # =====================================================

    total_prediction = sum(
        x["prediction"]
        for x in prediction_results
    )

    if total_prediction > 0:

        for result in prediction_results:

            result["prediction"] = (

                result["prediction"]

                /

                total_prediction

            ) * 100

    # =====================================================
    # 승률 계산
    # =====================================================

    win_counts = {
        c: 0
        for c in candidate_names
    }

    for i in range(10000):

        sample = {}

        for result in prediction_results:

            sample[
                result["candidate"]
            ] = result[
                "simulations"
            ][i]

        total = sum(sample.values())

        if total > 0:

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

    # =====================================================
    # 그래프 축
    # =====================================================

    all_values = []

    for trace in fig.data:

        try:

            all_values.extend(trace.y)

        except:

            pass

    y_max = min(
        max(all_values) + 5,
        100
    )

    y_max = max(
        y_max,
        20
    )

    fig.update_layout(

        template="plotly_white",

        yaxis=dict(
            range=[0,y_max],
            ticksuffix="%"
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # =====================================================
    # 결과 출력
    # =====================================================

    st.header("9. 최종 예측")

    result_rows = []

    for result in prediction_results:

        candidate = result["candidate"]

        prediction = result["prediction"]

        win_rate = (
            win_counts[candidate]
            / 10000
        ) * 100

        result_rows.append({

            "후보": candidate,

            "예상 득표율":
                round(prediction,2),

            "승률":
                round(win_rate,2),

            "95% 하한":
                round(result["lower"],2),

            "95% 상한":
                round(result["upper"],2)
        })

    result_df = pd.DataFrame(
        result_rows
    )

    result_df = result_df.sort_values(
        "예상 득표율",
        ascending=False
    )

    st.dataframe(
        result_df,
        use_container_width=True
    )
