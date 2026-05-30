# =========================================================
# engine/sampler.py
# =========================================================

import numpy as np


# =========================================================
# Dirichlet 샘플링
# =========================================================

def sample_dirichlet(
    percentages,
    strength
):

    keys = list(
        percentages.keys()
    )

    values = np.array([

        percentages[k]

        for k in keys

    ])

    values = np.clip(
        values,
        0.0001,
        None
    )

    alpha = (

        values
        / values.sum()

    ) * strength

    sampled = np.random.dirichlet(
        alpha
    )

    result = {}

    for k, v in zip(
        keys,
        sampled
    ):

        result[k] = (
            float(v)
            * 100
        )

    return result


# =========================================================
# 후보 지지율 샘플링
# =========================================================

def sample_candidate_supports(
    supports,
    sample_size
):

    effective_sample_size = (
        sample_size * 0.5
    )

    strength = max(
        effective_sample_size,
        50
    )

    return sample_dirichlet(

        supports,

        strength

    )


# =========================================================
# 무지지자 규모 샘플링
# =========================================================

def sample_undecided_size(
    undecided_pct,
    sample_size
):

    p = undecided_pct / 100

    n = max(
        sample_size,
        1
    )

    se = np.sqrt(
        p * (1 - p) / n
    )

    sampled = np.random.normal(
        undecided_pct,
        se * 100
    )

    return float(
        np.clip(
            sampled,
            0,
            100
        )
    )


# =========================================================
# 무지지자 선호 샘플링
# =========================================================

def sample_undecided_preferences(
    preferences,
    sample_size
):

    effective_sample_size = (
        sample_size * 0.5
    )

    strength = max(
        effective_sample_size,
        50
    )

    return sample_dirichlet(

        preferences,

        strength

    )


# =========================================================
# 무지지자 재배분
# =========================================================

def allocate_undecided(
    candidate_supports,
    undecided_size,
    undecided_preferences
):

    final_result = {}

    for candidate in candidate_supports:

        base_support = (
            candidate_supports[
                candidate
            ]
        )

        undecided_share = (

            undecided_size

            *

            undecided_preferences[
                candidate
            ]

            / 100

        )

        final_result[candidate] = (

            base_support

            +

            undecided_share

        )

    total = sum(
        final_result.values()
    )

    if total <= 0:

        total = 1

    for candidate in final_result:

        final_result[candidate] = (

            final_result[
                candidate
            ]

            /

            total

        ) * 100

    return final_result


# =========================================================
# 승자 결정
# =========================================================

def determine_winner(
    final_result
):

    return max(
        final_result,
        key=final_result.get
    )


# =========================================================
# World 생성
# =========================================================

def generate_world(
    supports,
    undecided,
    undecided_preferences,
    sample_size
):

    sampled_supports = (

        sample_candidate_supports(

            supports,

            sample_size

        )

    )

    sampled_undecided = (

        sample_undecided_size(

            undecided,

            sample_size

        )

    )

    sampled_preferences = (

        sample_undecided_preferences(

            undecided_preferences,

            sample_size

        )

    )

    final_result = (

        allocate_undecided(

            sampled_supports,

            sampled_undecided,

            sampled_preferences

        )

    )

    winner = (
        determine_winner(
            final_result
        )
    )

    return {

        "sampled_supports":
            sampled_supports,

        "sampled_undecided":
            sampled_undecided,

        "sampled_preferences":
            sampled_preferences,

        "final_result":
            final_result,

        "winner":
            winner
    }
