# =========================================================
# engine/kalman.py
# =========================================================

import numpy as np

from filterpy.kalman import (
    KalmanFilter
)


# =========================================================
# 표본오차 → 관측오차
# =========================================================

def poll_variance(
    support_pct,
    sample_size
):
    """
    비율추정 분산

    p(1-p)/n
    """

    p = max(
        0.0001,
        min(
            support_pct / 100,
            0.9999
        )
    )

    n = max(
        sample_size,
        1
    )

    variance = (

        p
        *
        (1 - p)

        /

        n

    )

    return (
        variance
        *
        100
        *
        100
    )


# =========================================================
# Kalman 생성
# =========================================================

def create_kalman_filter(
    initial_value,
    q_level=0.05
):
    """
    상태

    x[0]
    = 지지율 수준

    x[1]
    = 추세
    """

    kf = KalmanFilter(
        dim_x=2,
        dim_z=1
    )

    # 상태

    kf.x = np.array([

        initial_value,

        0.0

    ])

    # 상태전이

    kf.F = np.array([

        [1, 1],

        [0, 1]

    ])

    # 관측행렬

    kf.H = np.array([

        [1, 0]

    ])

    # 공분산

    kf.P *= 1000

    # 시스템 노이즈

    kf.Q = np.array([

        [q_level, 0],

        [0, q_level]

    ])

    return kf


# =========================================================
# Kalman 실행
# =========================================================

def run_kalman(
    values,
    variances,
    q_level=0.05
):
    """
    values

    관측값

    variances

    관측오차
    """

    if len(values) == 0:

        return []

    kf = create_kalman_filter(

        values[0],

        q_level
    )

    filtered = []

    trends = []

    for value, variance in zip(

        values,

        variances

    ):

        kf.R = np.array([
            [variance]
        ])

        kf.predict()

        kf.update(
            value
        )

        filtered.append(
            float(
                kf.x[0]
            )
        )

        trends.append(
            float(
                kf.x[1]
            )
        )

    return {

        "filtered":
            filtered,

        "trend":
            trends
    }


# =========================================================
# 마지막 상태 추출
# =========================================================

def final_state(
    values,
    variances,
    q_level=0.05
):
    result = run_kalman(

        values,

        variances,

        q_level

    )

    if len(
        result["filtered"]
    ) == 0:

        return None

    return {

        "support":

            result[
                "filtered"
            ][-1],

        "trend":

            result[
                "trend"
            ][-1]
    }


# =========================================================
# 미래 예측
# =========================================================

def forecast_state(
    support,
    trend,
    days
):
    """
    선형 상태공간 외삽

    support_t
    =
    support
    +
    trend × days
    """

    return (

        support

        +

        trend

        *

        days

    )
