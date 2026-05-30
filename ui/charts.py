# =========================================================
# ui/charts.py
# =========================================================

import numpy as np
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go

import streamlit as st


# =========================================================
# 승률 차트
# =========================================================

def render_win_rate_chart(
    win_rates
):

    df = pd.DataFrame({

        "후보":
            list(
                win_rates.keys()
            ),

        "승률":
            list(
                win_rates.values()
            )
    })

    df = df.sort_values(
        "승률",
        ascending=False
    )

    fig = px.bar(

        df,

        x="후보",

        y="승률",

        text="승률"
    )

    fig.update_traces(
        texttemplate="%{y:.1f}%"
    )

    fig.update_layout(

        title="후보별 승률",

        height=500
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# 예상 득표율 차트
# =========================================================

def render_prediction_chart(
    result_df
):

    fig = go.Figure()

    fig.add_trace(

        go.Bar(

            x=result_df["후보"],

            y=result_df["예상 득표율"],

            error_y=dict(

                type="data",

                symmetric=False,

                array=(

                    result_df["95% 상한"]

                    -

                    result_df["예상 득표율"]

                ),

                arrayminus=(

                    result_df["예상 득표율"]

                    -

                    result_df["95% 하한"]

                )
            )
        )
    )

    fig.update_layout(

        title="예상 득표율",

        height=550
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# 후보별 분포
# =========================================================

def render_distribution_chart(
    worlds,
    candidate_names
):

    st.subheader(
        "득표율 분포"
    )

    candidate = st.selectbox(

        "후보 선택",

        candidate_names,

        key="distribution_candidate"
    )

    values = []

    for world in worlds:

        values.append(

            world[
                "final_result"
            ][candidate]

        )

    df = pd.DataFrame({

        "득표율":
            values
    })

    fig = px.histogram(

        df,

        x="득표율",

        nbins=25
    )

    fig.update_layout(

        title=f"{candidate} 득표율 분포",

        height=500
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# 가능세계 산점도
# =========================================================

def render_world_scatter(
    worlds,
    candidate_names
):

    st.subheader(
        "가능세계 분포"
    )

    if len(
        candidate_names
    ) < 2:

        st.info(
            "후보 2명 이상 필요"
        )

        return

    x_candidate = st.selectbox(

        "X축 후보",

        candidate_names,

        key="scatter_x"
    )

    y_candidate = st.selectbox(

        "Y축 후보",

        candidate_names,

        index=1,

        key="scatter_y"
    )

    rows = []

    for world in worlds:

        rows.append({

            "World":
                world[
                    "world_id"
                ],

            "Winner":
                world[
                    "winner"
                ],

            x_candidate:

                world[
                    "final_result"
                ][x_candidate],

            y_candidate:

                world[
                    "final_result"
                ][y_candidate]
        })

    df = pd.DataFrame(
        rows
    )

    fig = px.scatter(

        df,

        x=x_candidate,

        y=y_candidate,

        color="Winner",

        hover_data=[
            "World"
        ]
    )

    fig.update_layout(

        title="가능세계 산점도",

        height=650
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# 추세선
# =========================================================

def render_trend_chart(
    dataframe,
    candidate_names
):

    fig = go.Figure()

    for candidate in candidate_names:

        fig.add_trace(

            go.Scatter(

                x=dataframe[
                    "end_date"
                ],

                y=dataframe[
                    candidate
                ],

                mode="lines+markers",

                name=candidate
            )
        )

    fig.update_layout(

        title="여론조사 추세",

        height=650,

        xaxis_title="날짜",

        yaxis_title="지지율"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# 대표 World 표시
# =========================================================

def render_representative_world(
    world,
    candidate_names
):

    rows = []

    for candidate in candidate_names:

        rows.append({

            "후보":
                candidate,

            "득표율":
                round(

                    world[
                        "final_result"
                    ][candidate],

                    2
                )
        })

    df = pd.DataFrame(
        rows
    )

    df = df.sort_values(
        "득표율",
        ascending=False
    )

    st.subheader(
        f"대표 가능세계 (승자: {world['winner']})"
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# FiveThirtyEight 스타일 승률 카드
# =========================================================

def render_probability_cards(
    win_rates
):

    st.subheader(
        "당선 확률"
    )

    cols = st.columns(
        len(
            win_rates
        )
    )

    sorted_items = sorted(

        win_rates.items(),

        key=lambda x: x[1],

        reverse=True
    )

    for idx, (
        candidate,
        probability
    ) in enumerate(
        sorted_items
    ):

        with cols[idx]:

            st.metric(

                candidate,

                f"{probability:.1f}%"
            )
