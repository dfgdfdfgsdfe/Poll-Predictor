# =========================================================
# data/storage.py
# =========================================================

import json
import os

from data.models import (
    ElectionProject
)

# =========================================================
# 저장 폴더
# =========================================================

SAVE_DIR = "saved_projects"

os.makedirs(
    SAVE_DIR,
    exist_ok=True
)

# =========================================================
# 파일 경로 생성
# =========================================================

def project_path(
    project_name: str
):

    safe_name = (
        project_name
        .strip()
        .replace("/", "_")
        .replace("\\", "_")
    )

    return os.path.join(
        SAVE_DIR,
        f"{safe_name}.json"
    )

# =========================================================
# 프로젝트 저장
# =========================================================

def save_project(
    project: ElectionProject
):

    path = project_path(
        project.project_name
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(

            project.to_dict(),

            f,

            ensure_ascii=False,

            indent=4
        )

# =========================================================
# 프로젝트 불러오기
# =========================================================

def load_project(
    project_name: str
):

    path = project_path(
        project_name
    )

    if not os.path.exists(
        path
    ):

        return None

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(
            f
        )

    return ElectionProject.from_dict(
        data
    )

# =========================================================
# 프로젝트 삭제
# =========================================================

def delete_project(
    project_name: str
):

    path = project_path(
        project_name
    )

    if os.path.exists(
        path
    ):

        os.remove(
            path
        )

        return True

    return False

# =========================================================
# 프로젝트 존재 여부
# =========================================================

def project_exists(
    project_name: str
):

    path = project_path(
        project_name
    )

    return os.path.exists(
        path
    )

# =========================================================
# 프로젝트 목록
# =========================================================

def list_projects():

    projects = []

    for filename in os.listdir(
        SAVE_DIR
    ):

        if not filename.endswith(
            ".json"
        ):

            continue

        projects.append(

            filename.replace(
                ".json",
                ""
            )

        )

    projects.sort()

    return projects

# =========================================================
# 프로젝트 정보 조회
# =========================================================

def get_project_summary():

    rows = []

    projects = list_projects()

    for project_name in projects:

        try:

            project = load_project(
                project_name
            )

            rows.append({

                "project_name":
                    project.project_name,

                "election_date":
                    project.election_date,

                "candidate_count":
                    len(
                        project.candidate_names
                    ),

                "poll_count":
                    len(
                        project.polls
                    )
            })

        except Exception:

            pass

    return rows

# =========================================================
# 프로젝트 복제
# =========================================================

def duplicate_project(
    source_name: str,
    target_name: str
):

    project = load_project(
        source_name
    )

    if project is None:

        return False

    project.project_name = (
        target_name
    )

    save_project(
        project
    )

    return True

# =========================================================
# 전체 삭제
# =========================================================

def delete_all_projects():

    files = [

        f

        for f

        in os.listdir(
            SAVE_DIR
        )

        if f.endswith(
            ".json"
        )
    ]

    for filename in files:

        os.remove(

            os.path.join(
                SAVE_DIR,
                filename
            )

        )

    return len(
        files
    )
