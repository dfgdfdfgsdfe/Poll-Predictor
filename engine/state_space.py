# =========================================================
# engine/state_space.py
# =========================================================

import numpy as np

from engine.kalman import (
    poll_variance,
    final_state,
    forecast_state
)

from engine.time_decay import (
    build_time_weights,
    adjust_variances_by_time
)


# =========================================================
# 후보 1명 상태 추정
# =========================================================

def estimate_candidate_state(
    dataframe,
    candidate
):

    values = (
        dataframe[candidate]
        .astype(float)
        .tolist()
    )

    variances = []

    for _, row in dataframe.iterrows():

        variances.append(

            poll_variance(
                row[candidate],
                row["sample_size"]
            )

        )

    weights = build_time_weights(
        dataframe
    )

    variances = adjust_variances_by_time(
        variances,
        weights
    )

    return final_state(
        values,
        variances
    )


# =========================================================
# 무지지자 상태 추정
# =========================================================

def estimate_undecided_state(
    dataframe
):

    values = (
        dataframe["undecided"]
        .astype(float)
        .tolist()
    )

    variances = []

    for _, row in dataframe.iterrows():

        variances.append(

            poll_variance(
                row["undecided"],
                row["sample_size"]
            )

        )

    weights = build_time_weights(
        dataframe
    )

    variances = adjust_variances_by_time(
        variances,
        weights
    )

    return final_state(
        values,
        variances
    )


# =========================================================
# 전체 상태공간 추정
# =========================================================

def estimate_state_space(
    dataframe,
    candidate_names
):

    result = {}

    for candidate in candidate_names:

        result[candidate] = (

            estimate_candidate_state(
                dataframe,
                candidate
            )

        )

    result["UNDECIDED"] = (

        estimate_undecided_state(
            dataframe
        )

    )

    return result


# =========================================================
# 선거일까지 외삽
# =========================================================

def forecast_to_election(
    state_space,
    days_until_election
):

    forecast = {}

    for name, state in state_space.items():

        support = state[
            "support"
        ]

        trend = state[
            "trend"
        ]

        predicted = forecast_state(

            support,
            trend,
            days_until_election

        )

        predicted = np.clip(
            predicted,
            0,
            100
        )

        forecast[name] = float(
            predicted
        )

    return forecast


# =========================================================
# 후보 합 100 정규화
# =========================================================

def normalize_forecast(
    forecast
):

    result = {}

    candidate_total = 0

    for name, value in forecast.items():

        if name == "UNDECIDED":
            continue

        candidate_total += value

    if candidate_total <= 0:

        candidate_total = 1

    for name, value in forecast.items():

        if name == "UNDECIDED":

            result[name] = value

        else:

            result[name] = (

                value

                /

                candidate_total

            ) * 100

    return result


# =========================================================
# 상태 요약
# =========================================================

def build_state_summary(
    state_space
):

    rows = []

    for name, state in state_space.items():

        rows.append({

            "name":
                name,

            "support":
                round(
                    state["support"],
                    2
                ),

            "trend":
                round(
                    state["trend"],
                    4
                )

        })

    return rows


# =========================================================
# 선거일 예측 패키지
# =========================================================

def build_forecast_package(
    dataframe,
    candidate_names,
    days_until_election
):
    """
    app.py에서 바로 사용

    반환:

    {
        "state_space": ...,
        "forecast": ...,
        "summary": ...
    }
    """

    state_space = (
        estimate_state_space(
            dataframe,
            candidate_names
        )
    )

    forecast = (
        forecast_to_election(
            state_space,
            days_until_election
        )
    )

    forecast = normalize_forecast(
        forecast
    )

    summary = (
        build_state_summary(
            state_space
        )
    )

    return {

        "state_space":
            state_space,

        "forecast":
            forecast,

        "summary":
            summary

    }
