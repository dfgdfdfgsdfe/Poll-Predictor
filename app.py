import streamlit as st
import pandas as pd
import numpy as np

from sklearn.linear_model import LinearRegression
from filterpy.kalman import KalmanFilter

import plotly.graph_objects as go

# =========================================================
# 페이지 설정
# =========================================================

st.set_page_config(
    page_title="정치 여론조사 예측 시스템",
    layout="wide"
)

st.title("정치 여론조사 예측 시스템")

st.markdown("""
### 기능

- House Effect 제거
- 표본수 가중치 반영
- 표준오차(SE) 자동 계산
- 무당층 자동 계산
- 무당층 내부 표준오차 계산
- Kalman Filter
- 미래 예측 점선
- Monte Carlo 시뮬레이션
- 승률 계산
- 자동 득표율 정규화
""")

# =========================================================
# Session State
# =========================================================

if "polls" not in st.session_state:
    st.session_state.polls = []

# =========================================================
# 후보 입력
# =========================================================

st.header("1. 후보 입력")

candidate_count = st.slider(
    "후보 수",
    1,
    5,
    2
)

candidate_names = []

cols = st.columns(candidate_count)

for i in range(candidate_count):

    with cols[i]:

        name = st.text_input(
            f"후보 {i+1}",
            key=f"candidate_{i}"
        )

        if name.strip() != "":
            candidate_names.append(name.strip())

# 후보 중복 검사
if len(candidate_names) != len(set(candidate_names)):

    st.error("후보 이름이 중복되었습니다.")

    st.stop()

# =========================================================
# 선거일 입력
# =========================================================

st.header("2. 선거일 입력")

election_day = st.date_input(
    "선거일"
)

# =========================================================
# Kalman 설정
# =========================================================

st.header("3. Kalman Filter 설정")

R_option = st.select_slider(
    "R 값",
    options=[
        "매우 낮음",
        "낮음",
        "보통",
        "높음",
        "매우 높음"
    ],
    value="보통"
)

Q_option = st.select_slider(
    "Q 값",
    options=[
        "매우 낮음",
        "낮음",
        "보통",
        "높음",
        "매우 높음"
    ],
    value="보통"
)

R_map = {
    "매우 낮음": 0.5,
    "낮음": 1.0,
    "보통": 2.0,
    "높음": 4.0,
    "매우 높음": 8.0
}

Q_map = {
    "매우 낮음": 0.01,
    "낮음": 0.03,
    "보통": 0.05,
    "높음": 0.1,
    "매우 높음": 0.2
}

R_value = R_map[R_option]
Q_value = Q_map[Q_option]

st.info(f"""
현재 설정

R = {R_value}
Q = {Q_value}
""")

# =========================================================
# 여론조사 입력
# =========================================================

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

    support_values = {}

    cols = st.columns(
        max(1, len(candidate_names))
    )

    for idx, candidate in enumerate(candidate_names):

        with cols[idx]:

            support = st.number_input(
                f"{candidate} 지지율 (%)",
                min_value=0.0,
                max_value=100.0,
                step=0.1,
                key=f"support_{candidate}"
            )

            support_values[candidate] = support

    # 무당층 자동 계산
    undecided_total = (
        100
        - sum(support_values.values())
    )

    undecided_total = max(
        undecided_total,
        0
    )

    st.info(
        f"자동 계산된 무당층: "
        f"{round(undecided_total,2)}%"
    )

    # =====================================================
    # 무당층 내부 선호
    # =====================================================

    st.subheader("무당층 내부 후보 선호")

    undecided_preferences = {}

    cols2 = st.columns(
        max(1, len(candidate_names))
    )

    for idx, candidate in enumerate(candidate_names):

        with cols2[idx]:

            pref = st.number_input(
                f"무당층 중 {candidate} 선호 (%)",
                min_value=0.0,
                max_value=100.0,
                step=0.1,
                key=f"pref_{candidate}"
            )

            undecided_preferences[candidate] = pref

    submit = st.form_submit_button(
        "여론조사 추가"
    )

    if submit:

        if pollster.strip() == "":

            st.error("""
조사기관 이름을 입력해주세요.
""")

        elif end_date < start_date:

            st.error("""
조사 종료일이 시작일보다 빠릅니다.
""")

        elif sum(support_values.values()) > 100:

            st.error("""
후보 지지율 합계가 100 초과입니다.
""")

        elif sum(
            undecided_preferences.values()
        ) > 100:

            st.error("""
무당층 내부 선호 합계가 100 초과입니다.
""")

        else:

            poll = {
                "pollster": pollster,
                "start_date": str(start_date),
                "end_date": str(end_date),
                "sample_size": sample_size,
                "undecided_total": undecided_total,
                "supports": support_values,
                "undecided_preferences":
                    undecided_preferences
            }

            st.session_state.polls.append(
                poll
            )

            st.success("""
여론조사가 추가되었습니다.
""")

# =========================================================
# 입력 데이터 출력
# =========================================================

st.header("5. 입력된 여론조사")

if len(st.session_state.polls) == 0:

    st.warning("""
아직 입력된 여론조사가 없습니다.
""")

else:

    rows = []

    for poll in st.session_state.polls:

        row = {
            "기관": poll["pollster"],
            "종료일": poll["end_date"],
            "표본수": poll["sample_size"],
            "무당층": poll["undecided_total"]
        }

        for candidate in candidate_names:

            row[candidate] = (
                poll["supports"]
                .get(candidate, 0)
            )

        rows.append(row)

    display_df = pd.DataFrame(rows)

    display_df["종료일"] = pd.to_datetime(
        display_df["종료일"]
    )

    display_df = display_df.sort_values(
        "종료일"
    )

    st.dataframe(
        display_df,
        use_container_width=True
    )

# =========================================================
# 예측 시작
# =========================================================

st.header("6. 예측 실행")

run_prediction = st.button(
    "예측 시작"
)

if run_prediction:

    if len(candidate_names) == 0:

        st.error("""
후보를 입력해주세요.
""")

    elif len(st.session_state.polls) < 2:

        st.error("""
최소 2개 이상의 여론조사가 필요합니다.
""")

    else:

        rows = []

        for poll in st.session_state.polls:

            row = {
                "pollster": poll["pollster"],
                "end_date": pd.to_datetime(
                    poll["end_date"]
                ),
                "sample_size": poll["sample_size"],
                "undecided_total":
                    poll["undecided_total"]
            }

            for candidate in candidate_names:

                row[candidate] = (
                    poll["supports"]
                    .get(candidate, 0)
                )

                row[f"{candidate}_pref"] = (
                    poll["undecided_preferences"]
                    .get(candidate, 0)
                )

            rows.append(row)

        df = pd.DataFrame(rows)

        df = df.sort_values(
            "end_date"
        )

        # =====================================================
        # House Effect 제거
        # =====================================================

        for candidate in candidate_names:

            overall_mean = np.average(
                df[candidate],
                weights=df["sample_size"]
            )

            pollster_mean = (
                df.groupby("pollster")
                .apply(
                    lambda x:
                    np.average(
                        x[candidate],
                        weights=x["sample_size"]
                    )
                )
            )

            house_effect = (
                pollster_mean
                - overall_mean
            )

            df[f"{candidate}_adjusted"] = (
                df[candidate]
                -
                df["pollster"].map(
                    house_effect
                )
            )

        # =====================================================
        # Kalman 함수
        # =====================================================

        def run_kalman(series):

            kf = KalmanFilter(
                dim_x=2,
                dim_z=1
            )

            kf.x = np.array([
                series.iloc[0],
                0
            ])

            kf.F = np.array([
                [1, 1],
                [0, 1]
            ])

            kf.H = np.array([
                [1, 0]
            ])

            kf.P *= 1000

            kf.R = R_value

            kf.Q = np.array([
                [Q_value, 0],
                [0, Q_value]
            ])

            filtered = []

            for value in series:

                kf.predict()
                kf.update(value)

                filtered.append(
                    float(kf.x[0])
                )

            return filtered

        # =====================================================
        # 그래프 생성
        # =====================================================

        fig = go.Figure()

        prediction_results = []

        # =====================================================
        # 후보별 계산
        # =====================================================

        for candidate in candidate_names:

            temp = (
                df.groupby("end_date")
                .mean(numeric_only=True)
                .reset_index()
            )

            temp = temp.sort_values(
                "end_date"
            )

            # ================================================
            # Kalman
            # ================================================

            temp["support_kalman"] = (
                run_kalman(
                    temp[f"{candidate}_adjusted"]
                )
            )

            temp["pref_kalman"] = (
                run_kalman(
                    temp[f"{candidate}_pref"]
                )
            )

            temp["undecided_kalman"] = (
                run_kalman(
                    temp["undecided_total"]
                )
            )

            # ================================================
            # 날짜 숫자화
            # ================================================

            temp["date_num"] = (
                temp["end_date"]
                -
                temp["end_date"].min()
            ).dt.days

            X = temp[["date_num"]]

            # ================================================
            # 회귀 모델
            # ================================================

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

            # ================================================
            # 선거일 예측
            # ================================================

            predicted_support = (
                support_model.predict(
                    [[election_num]]
                )[0]
            )

            predicted_pref = (
                pref_model.predict(
                    [[election_num]]
                )[0]
            )

            predicted_undecided = (
                undecided_model.predict(
                    [[election_num]]
                )[0]
            )

            # ================================================
            # 범위 제한
            # ================================================

            predicted_support = np.clip(
                predicted_support,
                0,
                100
            )

            predicted_pref = np.clip(
                predicted_pref,
                0,
                100
            )

            predicted_undecided = np.clip(
                predicted_undecided,
                0,
                100
            )

            # ================================================
            # 최종 예측
            # ================================================

            final_prediction = (
                predicted_support
                +
                (
                    predicted_undecided
                    *
                    (
                        predicted_pref / 100
                    )
                )
            )

            # ================================================
            # 표준오차 계산
            # ================================================

            avg_support = (
                predicted_support / 100
            )

            n = max(
                df["sample_size"].mean(),
                1
            )

            support_se = np.sqrt(
                (
                    avg_support
                    *
                    (
                        1 - avg_support
                    )
                ) / n
            )

            undecided_n = (
                n
                *
                (
                    predicted_undecided / 100
                )
            )

            undecided_n = max(
                undecided_n,
                1
            )

            avg_pref = (
                predicted_pref / 100
            )

            undecided_se = np.sqrt(
                (
                    avg_pref
                    *
                    (
                        1 - avg_pref
                    )
                ) / undecided_n
            )

            combined_se = np.sqrt(
                support_se**2
                +
                undecided_se**2
            )

            # ================================================
            # Monte Carlo
            # ================================================

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
                "candidate": candidate,
                "prediction": final_prediction,
                "simulations": simulations
            })

            # ================================================
            # 현재 추세 실선
            # ================================================

            fig.add_trace(
                go.Scatter(
                    x=temp["end_date"],
                    y=temp["support_kalman"],
                    mode="lines+markers",
                    name=f"{candidate} 추세"
                )
            )

            # ================================================
            # 미래 점선
            # ================================================

            future_dates = pd.date_range(
                start=temp["end_date"].max(),
                end=pd.to_datetime(
                    election_day
                ),
                periods=30
            )

            future_date_num = (
                future_dates
                -
                temp["end_date"].min()
            ).days.values.reshape(-1, 1)

            future_predictions = (
                support_model.predict(
                    future_date_num
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
                    name=f"{candidate} 미래 예측"
                )
            )

        # =====================================================
        # 자동 정규화
        # =====================================================

        total_prediction = sum(
            result["prediction"]
            for result in prediction_results
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

            # 정규화
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
        # 그래프 범위 자동 조절
        # =====================================================

        all_graph_values = []

        for trace in fig.data:

            all_graph_values.extend(
                trace.y
            )

        y_max = (
            max(all_graph_values)
            + 5
        )

        y_max = min(
            y_max,
            100
        )

        y_max = max(
            y_max,
            20
        )

        fig.update_layout(
            template="plotly_white",
            yaxis=dict(
                range=[0, y_max],
                ticksuffix="%"
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # =====================================================
        # 최종 결과
        # =====================================================

        st.header("7. 선거일 예측 결과")

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
                    round(prediction, 2),
                "승률":
                    round(win_rate, 2)
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

        # =====================================================
        # 원본 데이터
        # =====================================================

        st.header("8. 세부 데이터")

        st.dataframe(
            df,
            use_container_width=True
        )
