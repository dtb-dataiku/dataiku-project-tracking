"""
dku_tracker — Dataiku instance project tracking library.
 
Public API surface. Import from here for agent tools or recipe use.
"""

from .client import (
    get_host,
    get_client,
    get_project
)
from .projects import (
    get_project_metadata,
    get_all_projects_metadata,
    get_project_contributors
)
from .artifacts import (
    get_project_agents,
    get_project_api_services,
    get_project_dashboards,
    get_project_models,
    get_project_webapps
)
from .datasets import (
    get_project_datasets,
    get_project_folders
)
