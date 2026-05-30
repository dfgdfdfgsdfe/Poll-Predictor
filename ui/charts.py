# =========================================================
# ui/charts.py
# =========================================================

import pandas as pd
import numpy as np

import plotly.graph_objects as go


# =========================================================
# 예측 결과 바 차트
# =========================================================

def prediction_bar_chart(
    prediction_table
):

    candidates = [
        row["후보"]
        for row in prediction_table
    ]

    values = [
        row["예상 득표율"]
        for row in prediction_table
    ]

    lowers = [
        row["95% 하한"]
        for row in prediction_table
    ]

    uppers = [
        row["95% 상한"]
        for row in prediction_table
    ]

    error_plus = [
        u - v
        for u, v
        in zip(
            uppers,
            values
        )
    ]

    error_minus = [
        v - l
        for l, v
        in zip(
            lowers,
            values
        )
    ]

    fig = go.Figure()

    fig.add_trace(

        go.Bar(

            x=candidates,

            y=values,

            error_y=dict(

                type="data",

                symmetric=False,

                array=error_plus,

                arrayminus=error_minus

            )

        )

    )

    fig.update_layout(

        title="예상 득표율",

        xaxis_title="후보",

        yaxis_title="득표율 (%)",

        height=500

    )

    return fig


# =========================================================
# 승률 차트
# =========================================================

def win_rate_chart(
    win_rates
):

    candidates = list(
        win_rates.keys()
    )

    values = list(
        win_rates.values()
    )

    fig = go.Figure()

    fig.add_trace(

        go.Bar(

            x=candidates,

            y=values

        )

    )

    fig.update_layout(

        title="승률",

        xaxis_title="후보",

        yaxis_title="승률 (%)",

        height=500

    )

    return fig


# =========================================================
# 가능세계 분포
# =========================================================

def world_distribution_chart(
    worlds,
    candidate_names
):

    fig = go.Figure()

    for candidate in candidate_names:

        values = []

        for world in worlds:

            values.append(

                world[
                    "final_result"
                ][candidate]

            )

        fig.add_trace(

            go.Histogram(

                x=values,

                name=candidate,

                opacity=0.6,

                nbinsx=20

            )

        )

    fig.update_layout(

        title="가능세계 분포",

        barmode="overlay",

        height=600,

        xaxis_title="득표율",

        yaxis_title="빈도"

    )

    return fig


# =========================================================
# 후보별 Box Plot
# =========================================================

def candidate_boxplot(
    worlds,
    candidate_names
):

    fig = go.Figure()

    for candidate in candidate_names:

        values = []

        for world in worlds:

            values.append(

                world[
                    "final_result"
                ][candidate]

            )

        fig.add_trace(

            go.Box(

                y=values,

                name=candidate

            )

        )

    fig.update_layout(

        title="후보별 득표율 분포",

        height=600,

        yaxis_title="득표율 (%)"

    )

    return fig


# =========================================================
# 추세선
# =========================================================

def trend_chart(
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

        xaxis_title="조사 종료일",

        yaxis_title="지지율 (%)",

        hovermode="x unified"

    )

    return fig


# =========================================================
# 세계 승자 분포
# =========================================================

def winner_distribution_chart(
    worlds
):

    winners = []

    for world in worlds:

        winners.append(
            world["winner"]
        )

    counts = pd.Series(
        winners
    ).value_counts()

    fig = go.Figure()

    fig.add_trace(

        go.Bar(

            x=counts.index,

            y=counts.values

        )

    )

    fig.update_layout(

        title="100개 세계 승자 분포",

        xaxis_title="후보",

        yaxis_title="승리 횟수",

        height=500

    )

    return fig


# =========================================================
# FiveThirtyEight 스타일
# =========================================================

def fte_probability_chart(
    worlds,
    candidate_names
):

    fig = go.Figure()

    for candidate in candidate_names:

        values = []

        for world in worlds:

            values.append(

                world[
                    "final_result"
                ][candidate]

            )

        hist, bins = np.histogram(
            values,
            bins=30,
            density=True
        )

        centers = (
            bins[:-1]
            +
            bins[1:]
        ) / 2

        fig.add_trace(

            go.Scatter(

                x=centers,

                y=hist,

                mode="lines",

                name=candidate

            )

        )

    fig.update_layout(

        title="가능세계 확률분포",

        xaxis_title="득표율",

        yaxis_title="밀도",

        height=650

    )

    return fig
