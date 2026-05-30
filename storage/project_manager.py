from pathlib import Path
import json
import uuid
from datetime import datetime

PROJECTS_DIR = Path("projects")


def ensure_projects_dir():
    PROJECTS_DIR.mkdir(exist_ok=True)


def list_projects():

    ensure_projects_dir()

    projects = []

    for p in PROJECTS_DIR.iterdir():

        if not p.is_dir():
            continue

        project_file = p / "project.json"

        if project_file.exists():

            with open(
                project_file,
                "r",
                encoding="utf-8"
            ) as f:

                projects.append(
                    json.load(f)
                )

    return projects


def create_project(
    name,
    election_date,
    candidates
):

    ensure_projects_dir()

    project_id = str(
        uuid.uuid4()
    )

    project_dir = (
        PROJECTS_DIR
        / project_id
    )

    project_dir.mkdir()

    data = {

        "project_id":
            project_id,

        "name":
            name,

        "created_at":
            datetime.now().isoformat(),

        "election_date":
            str(election_date),

        "candidates":
            candidates
    }

    with open(
        project_dir / "project.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )

    return project_id


def delete_project(
    project_id
):

    import shutil

    target = (
        PROJECTS_DIR
        / project_id
    )

    if target.exists():

        shutil.rmtree(
            target
        )
