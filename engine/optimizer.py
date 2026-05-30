import numpy as np


def grid_search():

    r_grid = [
        0.5,
        1,
        2,
        4,
        8
    ]

    q_grid = [
        0.01,
        0.03,
        0.05,
        0.1
    ]

    lambda_grid = [
        0.003,
        0.01,
        0.03,
        0.05
    ]

    best_score = np.inf

    best = None

    for r in r_grid:

        for q in q_grid:

            for l in lambda_grid:

                score = 0

                if score < best_score:

                    best_score = score

                    best = (
                        r,
                        q,
                        l
                    )

    return best
