"""
projects.py — Project-level metadata and contributors.
"""

from __future__ import annotations
from typing import Any
from .client import get_client, get_project


def get_project_metadata(project_key: str) -> dict[str, Any]:
    """
    Return core metadata for a single project.

    Includes display name, description, owner, tags, creation info,
    and the raw project settings for downstream use.

    Parameters
    ----------
    project_key : str
        The DSS project key.

    Returns
    -------
    dict with keys:
        project_key, name, description, owner, tags,
        creation_tag, created_on, status
    """
    
    project = get_project(project_key)
    
    project_exists = True
    try:
        summary = project.get_summary()
        settings = project.get_settings().get_raw()
        timeline = project.get_timeline()
    except Exception as exc:
        summary, settings, timeline = {}, {}, {}
        project_exists = False
        

    # creation_tag is the git-style first-commit metadata DSS stores
    creation_tag = summary.get("creationTag", {})

    # Get project folder from project location
    project_location = summary.get('projectLocation', [])
    project_folders = [p['name'] for p in reversed(project_location) if p['id'] != 'ROOT']
    project_folder = ' > '.join(project_folders)
    
    # Get project timeline
    last_modified_dt = timeline.get('lastModifiedOn', 0)

    return {
        "project_key": project_key,
        "name": summary.get("name", project_key),
        "short_description": summary.get("shortDesc", ""),
        "description": summary.get("description", ""),
        "owner": summary.get("ownerLogin", ""),
        "tags": sorted(summary.get("tags", [])),
        "status": settings.get("projectStatus", ""),
        "folder": project_folder,
        "created_by": creation_tag.get("lastModifiedBy", {}).get("login", ""),
        "created_on": creation_tag.get("lastModifiedOn", 0),
        "last_modified_on": last_modified_dt,
        "exists": project_exists
    }


def get_all_projects_metadata(ignore_tutorials: bool = True, ignore_dku_apps: bool = True) -> list[dict[str, Any]]:
    """
    Return core metadata for every project on the instance.

    Iterates all projects visible to the current user (admin context
    returns all projects).

    Returns
    -------
    list of dicts — each dict matches the shape of get_project_metadata()
    """
    
    client = get_client()
    results = []
    for project_key in client.list_project_keys():
        try:
            project = get_project(project_key)
            
            is_not_tutorial = True
            if ignore_tutorials:
                is_not_tutorial = project.get_summary().get('tutorialProject', False) != True
                
            is_not_app_instance = True
            if ignore_dku_apps:
                is_not_app_instance = project.get_summary().get('projectAppType', '') != 'APP_INSTANCE'
            
            if is_not_tutorial & is_not_app_instance:
                results.append(get_project_metadata(project_key))
        except Exception as exc:
            # Log and continue so one broken project doesn't abort the sweep
            results.append({
                "project_key": project_key,
                "error": str(exc),
            })
            
    return results


def get_project_contributors(project_key: str) -> list[dict[str, Any]]:
    """
    Return a list of users who have made git-tracked edits to the project.

    DSS tracks "last modified by" on individual objects (datasets, recipes,
    etc.). This function sweeps the project's object timeline via the
    activity log to surface unique contributors.

    Parameters
    ----------
    project_key : str

    Returns
    -------
    list of dicts with keys: login, display_name, last_active_on
    """
    
    project = get_project(project_key)

    # Use the project timeline (audit log entries scoped to this project)
    timeline = project.get_timeline()
    
    contributors = [t['login'] for t in timeline['allContributors']]
    contributors = list(filter(lambda c: not c.startswith('api:'), contributors))
    results = [{"project_key": project_key, "login": c} for c in contributors]

    return results
