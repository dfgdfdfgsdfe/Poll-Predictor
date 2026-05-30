# =========================================================
# analytics/results.py
# =========================================================

import numpy as np
import pandas as pd


# =========================================================
# 후보별 득표율 추출
# =========================================================

def extract_candidate_values(
    worlds,
    candidate_name
):

    values = []

    for world in worlds:

        values.append(

            world[
                "final_result"
            ][candidate_name]

        )

    return np.array(
        values
    )


# =========================================================
# 승률 계산
# =========================================================

def calculate_win_rates(
    worlds,
    candidate_names
):

    wins = {

        candidate: 0

        for candidate
        in candidate_names
    }

    for world in worlds:

        winner = world[
            "winner"
        ]

        wins[winner] += 1

    total = len(
        worlds
    )

    results = {}

    for candidate in candidate_names:

        results[candidate] = (

            wins[candidate]

            /
            total

        ) * 100

    return results


# =========================================================
# 후보별 요약 통계
# =========================================================

def summarize_candidate(
    worlds,
    candidate_name
):

    values = extract_candidate_values(
        worlds,
        candidate_name
    )

    return {

        "candidate":
            candidate_name,

        "mean":
            float(
                np.mean(
                    values
                )
            ),

        "median":
            float(
                np.median(
                    values
                )
            ),

        "lower":
            float(
                np.percentile(
                    values,
                    2.5
                )
            ),

        "upper":
            float(
                np.percentile(
                    values,
                    97.5
                )
            ),

        "std":
            float(
                np.std(
                    values
                )
            )
    }


# =========================================================
# 결과 테이블 생성
# =========================================================

def build_results_table(
    worlds,
    candidate_names
):

    win_rates = (
        calculate_win_rates(
            worlds,
            candidate_names
        )
    )

    rows = []

    for candidate in candidate_names:

        summary = (
            summarize_candidate(
                worlds,
                candidate
            )
        )

        rows.append({

            "후보":
                candidate,

            "예상 득표율":
                round(
                    summary["mean"],
                    2
                ),

            "승률":
                round(
                    win_rates[
                        candidate
                    ],
                    2
                ),

            "95% 하한":
                round(
                    summary["lower"],
                    2
                ),

            "95% 상한":
                round(
                    summary["upper"],
                    2
                ),

            "표준편차":
                round(
                    summary["std"],
                    2
                )
        })

    df = pd.DataFrame(
        rows
    )

    df = df.sort_values(
        "예상 득표율",
        ascending=False
    )

    df = df.reset_index(
        drop=True
    )

    return df


# =========================================================
# 승률 순 정렬
# =========================================================

def build_win_rate_table(
    worlds,
    candidate_names
):

    win_rates = (
        calculate_win_rates(
            worlds,
            candidate_names
        )
    )

    rows = []

    for candidate in candidate_names:

        rows.append({

            "후보":
                candidate,

            "승률":
                round(
                    win_rates[
                        candidate
                    ],
                    2
                )
        })

    df = pd.DataFrame(
        rows
    )

    df = df.sort_values(
        "승률",
        ascending=False
    )

    df = df.reset_index(
        drop=True
    )

    return df


# =========================================================
# 대표 World 추출
# =========================================================

def find_median_world(
    worlds,
    candidate_names
):
    """
    가장 평균에 가까운 World
    """

    means = {}

    for candidate in candidate_names:

        values = []

        for world in worlds:

            values.append(

                world[
                    "final_result"
                ][candidate]

            )

        means[candidate] = (
            np.mean(
                values
            )
        )

    best_world = None

    best_distance = None

    for world in worlds:

        distance = 0

        for candidate in candidate_names:

            distance += (

                world[
                    "final_result"
                ][candidate]

                -

                means[
                    candidate
                ]

            ) ** 2

        if (

            best_distance is None

            or

            distance < best_distance

        ):

            best_distance = distance

            best_world = world

    return best_world


# =========================================================
# World 번호 추가
# =========================================================

def attach_world_ids(
    worlds
):

    result = []

    for idx, world in enumerate(
        worlds
    ):

        copied = dict(
            world
        )

        copied[
            "world_id"
        ] = idx + 1

        result.append(
            copied
        )

    return result
