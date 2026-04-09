"""
client.py — Dataiku DSS client helpers.

When running inside Dataiku (recipe, notebook, webapp), no host or API key
is needed. dataikuapi.DSSClient() with no arguments connects to the local
instance using the current user's context.
"""

from __future__ import annotations

import dataikuapi
import dataiku


_CLIENT: dataikuapi.DSSClient | None = None
_HOST: str = None


def get_host() -> str:
    """
    Return a module-level singleton DSSClient for the local Dataiku instance.

    Returns
    -------
    str
    """
    
    global _HOST
    if _HOST is None:
        _HOST = "https://dss-70337748-dc36eeee-dku.us-east-1.app.dataiku.io"
    return _HOST


def get_client() -> dataikuapi.DSSClient:
    """
    Return a module-level singleton DSSClient for the local Dataiku instance.

    Uses the internal (no-auth) connection available when code runs inside DSS.
    Safe to call multiple times — only one client is created.

    Returns
    -------
    dataikuapi.DSSClient
    """
    
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = dataiku.api_client()
    return _CLIENT


def get_project(project_key: str) -> dataikuapi.DSSProject:
    """
    Return a DSSProject handle for the given project key.

    Parameters
    ----------
    project_key : str
        The DSS project key (e.g. "MY_PROJECT").

    Returns
    -------
    dataikuapi.DSSProject
    """
    
    return get_client().get_project(project_key)
