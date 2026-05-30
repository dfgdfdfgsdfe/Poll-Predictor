from pathlib import Path
import json

PROJECTS_DIR = Path(
    "projects"
)


def save_json(
    project_id,
    filename,
    data
):

    path = (
        PROJECTS_DIR
        / project_id
        / filename
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )


def load_json(
    project_id,
    filename
):

    path = (
        PROJECTS_DIR
        / project_id
        / filename
    )

    if not path.exists():
        return None

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)
