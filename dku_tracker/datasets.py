"""
datasets.py — Dataset inventory for a project.
"""

from __future__ import annotations

from typing import Any

from .client import get_project


def get_project_datasets(project_key: str) -> list[dict[str, Any]]:
    """
    Return a summary of every dataset in the project.

    Parameters
    ----------
    project_key : str

    Returns
    -------
    list of dicts with keys:
        project_key, name, type, connection, tags,
        schema_columns (list of {name, type}), managed
    """
    
    project = get_project(project_key)
    try:
        datasets = project.list_datasets(include_shared=True)
    except Exception as exc:
        datasets = []
    
    results = []

    for ds in datasets:
        metadata = {
            'project_key': project_key,
            'source_project_key': '',
            'name': '',
            'type': '',
            'connection': '',
            'short_description': '',
            'long_description': '',
            'tags': [],
            'columns': []
        }
        
        columns = ds.get('schema', {}).get('columns', [])
        columns = [{'name': c['name'], 'type': c['type'], 'comment': c.get('comment', '')} for c in columns]
        
        metadata['source_project_key'] = ds.get('projectKey', '')
        metadata['name'] = ds.get('name', '')
        metadata['connection'] = ds.get('params', {}).get('connection', '')
        metadata['type'] = ds.get('type', '')
        metadata['short_description'] = ds.get('shortDesc', 'No description provided.').strip()
        metadata['long_description'] = ds.get('description', 'No description provided.').strip()
        metadata['tags'] = ds.get('tags', [])
        metadata['columns'] = columns
        
        results.append(metadata)

    return results

def get_project_folders(project_key: str) -> list[dict[str, Any]]:
    """
    Return a summary of every managed folder in the project.

    Parameters
    ----------
    project_key : str

    Returns
    -------
    list of dicts with keys:
        project_key, name, id, type, connection, tags
    """
    
    project = get_project(project_key)
    try:
        folders = project.list_managed_folders()
    except Exception as exc:
        folders = []
    
    results = []

    for folder in folders:
        folder_settings = project.get_managed_folder(folder['id']).get_settings()
        
        results.append({
            "project_key": project_key,
            "folder_id": folder.get("id", ""),
            "name": folder.get("name", ""),
            "type": folder.get("type", ""),
            "connection": folder.get("params", {}).get("connection", ""),
            "short_description": folder_settings.short_description,
            "long_description": folder_settings.description,
            "tags": folder.get("tags", [])
        })

    return results