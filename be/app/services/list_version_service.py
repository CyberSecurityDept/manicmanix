from datetime import datetime
from app.repositories.list_version_repository import get_gitlab_app_version, get_mvt_version

def prepare_version_data():
    app_version = get_gitlab_app_version()
    cyber_version = get_mvt_version()
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    data = [
        {
            "app_version": app_version,
            "datetime": current_datetime
        },
        {
            "cyber_version": cyber_version,
            "datetime": current_datetime
        }
    ]
    return data