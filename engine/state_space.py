# =========================================================
# engine/state_space.py
# =========================================================

import numpy as np

from engine.kalman import (
    poll_variance,
    final_state,
    forecast_state
)


# =========================================================
# 후보 1명 처리
# =========================================================

def estimate_candidate_state(
    dataframe,
    candidate
):
    """
    후보 1명의
    잠재 지지율 추정
    """

    values = (
        dataframe[candidate]
        .astype(float)
        .tolist()
    )

    variances = []

    for _, row in dataframe.iterrows():

        variance = poll_variance(
            row[candidate],
            row["sample_size"]
        )

        variances.append(
            variance
        )

    return final_state(
        values,
        variances
    )


# =========================================================
# 무지지자 처리
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

        variance = poll_variance(
            row["undecided"],
            row["sample_size"]
        )

        variances.append(
            variance
        )

    return final_state(
        values,
        variances
    )


# =========================================================
# 전체 상태 추정
# =========================================================

def estimate_state_space(
    dataframe,
    candidate_names
):
    """
    모든 후보 +
    무지지자
    """

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
# 선거일까지 예측
# =========================================================

def forecast_to_election(
    state_space,
    days_until_election
):
    """
    Kalman 상태를
    선거일까지 외삽
    """

    forecast = {}

    for name, state in state_space.items():

        support = state[
            "support"
        ]

        trend = state[
            "trend"
        ]

        predicted = (
            forecast_state(
                support,
                trend,
                days_until_election
            )
        )

        predicted = np.clip(
            predicted,
            0,
            100
        )

        forecast[name] = (
            float(predicted)
        )

    return forecast


# =========================================================
# 정규화
# =========================================================

def normalize_forecast(
    forecast
):
    """
    후보 비율 총합 100
    """

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
# 최근 상태 요약
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
