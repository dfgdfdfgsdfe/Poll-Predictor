# =========================================================
# engine/time_decay.py
# =========================================================

import numpy as np


# =========================================================
# 날짜별 가중치
# =========================================================

def exponential_weight(
    days_old,
    decay_rate=0.03
):
    """
    weight

    exp(
        -λ × days
    )
    """

    return np.exp(
        -decay_rate * days_old
    )


# =========================================================
# 전체 조사 가중치
# =========================================================

def build_time_weights(
    dataframe,
    decay_rate=0.03
):
    """
    최신 조사 기준
    """

    latest_date = (
        dataframe["end_date"]
        .max()
    )

    weights = []

    for _, row in dataframe.iterrows():

        days_old = (

            latest_date

            -

            row["end_date"]

        ).days

        weight = exponential_weight(

            days_old,

            decay_rate
        )

        weights.append(
            weight
        )

    return weights


# =========================================================
# 분산 보정
# =========================================================

def adjust_variances_by_time(
    variances,
    weights
):
    """
    오래된 조사일수록

    variance 증가
    """

    adjusted = []

    for v, w in zip(
        variances,
        weights
    ):

        w = max(
            w,
            0.001
        )

        adjusted.append(
            v / w
        )

    return adjusted
