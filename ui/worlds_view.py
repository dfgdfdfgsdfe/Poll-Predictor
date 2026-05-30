# =========================================================
# ui/worlds_view.py
# =========================================================

import pandas as pd
import streamlit as st


# =========================================================
# World → DataFrame
# =========================================================

def worlds_to_dataframe(
    worlds,
    candidate_names
):

    rows = []

    for world in worlds:

        row = {

            "World":
                world["world_id"],

            "Winner":
                world["winner"]
        }

        for candidate in candidate_names:

            row[candidate] = round(

                world[
                    "final_result"
                ][candidate],

                2

            )

        rows.append(
            row
        )

    df = pd.DataFrame(
        rows
    )

    return df


# =========================================================
# 전체 세계 테이블
# =========================================================

def render_world_table(
    worlds,
    candidate_names
):

    df = worlds_to_dataframe(

        worlds,

        candidate_names

    )

    st.dataframe(

        df,

        use_container_width=True

    )


# =========================================================
# 단일 세계 보기
# =========================================================

def render_single_world(
    worlds,
    candidate_names
):

    if len(worlds) == 0:

        st.warning(
            "세계가 없습니다."
        )

        return

    selected = st.selectbox(

        "가능세계 선택",

        range(
            1,
            len(worlds) + 1
        )

    )

    world = worlds[
        selected - 1
    ]

    st.subheader(

        f"World {selected}"

    )

    st.write(

        f"승자: {world['winner']}"

    )

    rows = []

    for candidate in candidate_names:

        rows.append({

            "후보":
                candidate,

            "득표율":

                round(

                    world[
                        'final_result'
                    ][candidate],

                    2

                )

        })

    st.dataframe(

        pd.DataFrame(
            rows
        ),

        use_container_width=True

    )


# =========================================================
# 승자별 세계 수
# =========================================================

def winner_summary(
    worlds
):

    counts = {}

    for world in worlds:

        winner = (
            world["winner"]
        )

        counts[winner] = (

            counts.get(
                winner,
                0
            )

            + 1

        )

    rows = []

    total = len(
        worlds
    )

    for winner, count in counts.items():

        rows.append({

            "후보":
                winner,

            "승리 세계":

                count,

            "비율":

                round(

                    count
                    /
                    total
                    *
                    100,

                    2

                )

        })

    return pd.DataFrame(
        rows
    )


# =========================================================
# 승자 요약 표시
# =========================================================

def render_winner_summary(
    worlds
):

    st.dataframe(

        winner_summary(
            worlds
        ),

        use_container_width=True

    )


# =========================================================
# 상위 N개 세계
# =========================================================

def top_worlds(
    worlds,
    candidate,
    top_n=10
):

    sorted_worlds = sorted(

        worlds,

        key=lambda x:

        x["final_result"][
            candidate
        ],

        reverse=True

    )

    rows = []

    for world in sorted_worlds[
        :top_n
    ]:

        rows.append({

            "World":
                world["world_id"],

            candidate:

                round(

                    world[
                        "final_result"
                    ][candidate],

                    2

                ),

            "Winner":
                world["winner"]

        })

    return pd.DataFrame(
        rows
    )


# =========================================================
# 하위 N개 세계
# =========================================================

def bottom_worlds(
    worlds,
    candidate,
    top_n=10
):

    sorted_worlds = sorted(

        worlds,

        key=lambda x:

        x["final_result"][
            candidate
        ]

    )

    rows = []

    for world in sorted_worlds[
        :top_n
    ]:

        rows.append({

            "World":
                world["world_id"],

            candidate:

                round(

                    world[
                        "final_result"
                    ][candidate],

                    2

                ),

            "Winner":
                world["winner"]

        })

    return pd.DataFrame(
        rows
    )


# =========================================================
# 후보별 극단 세계
# =========================================================

def render_candidate_extremes(
    worlds,
    candidate_names
):

    candidate = st.selectbox(

        "후보 선택",

        candidate_names,

        key="extreme_candidate"

    )

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(
            "최고 시나리오"
        )

        st.dataframe(

            top_worlds(

                worlds,

                candidate

            ),

            use_container_width=True

        )

    with col2:

        st.subheader(
            "최저 시나리오"
        )

        st.dataframe(

            bottom_worlds(

                worlds,

                candidate

            ),

            use_container_width=True

        )
