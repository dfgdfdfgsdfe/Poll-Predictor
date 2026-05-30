# =========================================================
# ui/worlds_view.py
# =========================================================

import pandas as pd
import streamlit as st


# =========================================================
# 단일 World 카드
# =========================================================

def render_world_card(
    world,
    candidate_names
):

    winner = world[
        "winner"
    ]

    world_id = world.get(
        "world_id",
        "-"
    )

    st.markdown(
        f"""
### 🌎 World {world_id}

**승자:** {winner}
"""
    )

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

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# World 목록
# =========================================================

def render_worlds(
    worlds,
    candidate_names
):

    st.header(
        "🌎 가능세계 목록"
    )

    for world in worlds:

        with st.expander(

            f"World {world['world_id']} | 승자: {world['winner']}"

        ):

            render_world_card(
                world,
                candidate_names
            )


# =========================================================
# 상위 World
# =========================================================

def render_top_worlds(
    worlds,
    candidate_names,
    count=10
):

    st.header(
        f"🏆 대표 가능세계 {count}개"
    )

    selected = worlds[
        :count
    ]

    for world in selected:

        with st.expander(

            f"World {world['world_id']}"

        ):

            render_world_card(
                world,
                candidate_names
            )


# =========================================================
# 승자별 World 개수
# =========================================================

def render_world_summary(
    worlds,
    candidate_names
):

    st.header(
        "📊 World 분포"
    )

    counts = {

        candidate: 0

        for candidate

        in candidate_names
    }

    for world in worlds:

        counts[
            world["winner"]
        ] += 1

    rows = []

    total = len(
        worlds
    )

    for candidate in candidate_names:

        rows.append({

            "후보":
                candidate,

            "World 수":
                counts[
                    candidate
                ],

            "비율":
                round(

                    counts[
                        candidate
                    ]

                    /

                    total

                    * 100,

                    2
                )
        })

    df = pd.DataFrame(
        rows
    )

    df = df.sort_values(
        "World 수",
        ascending=False
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# 특정 후보 승리 World만 보기
# =========================================================

def render_candidate_worlds(
    worlds,
    candidate_names,
    selected_candidate
):

    st.header(
        f"🎯 {selected_candidate} 승리 World"
    )

    filtered = []

    for world in worlds:

        if (

            world[
                "winner"
            ]

            ==

            selected_candidate

        ):

            filtered.append(
                world
            )

    if len(filtered) == 0:

        st.warning(
            "해당 World 없음"
        )

        return

    for world in filtered:

        with st.expander(

            f"World {world['world_id']}"

        ):

            render_world_card(
                world,
                candidate_names
            )
