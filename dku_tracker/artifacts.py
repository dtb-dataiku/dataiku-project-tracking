"""
artifacts.py — Project artifacts like dashboards, models, agents, APIs, and webapps.
"""

from __future__ import annotations
from typing import Any
from .client import get_project


def get_project_dashboards(project_key: str) -> list[dict[str, Any]]:
    """
    Return a summary of every dashboard in the project.

    Parameters
    ----------
    project_key : str

    Returns
    -------
    list of dicts with keys:
        project_key, dashboard_id, name, listed (published somewhere)
    """
    
    project = get_project(project_key)
    try:
        dashboards = project.list_dashboards()
    except Exception as exc:
        dashboards = []
    
    results = []

    for dashboard in dashboards:
        results.append({
            "project_key": project_key,
            "dashboard_id": dashboard.get("id", ""),
            "name": dashboard.get("name", ""),
            "tags": dashboard.get("tags", []),
            "listed": dashboard.get("listed", False)
        })

    return results


def get_project_webapps(project_key: str) -> list[dict[str, Any]]:
    """
    Return a summary of every webapp in the project.
 
    Parameters
    ----------
    project_key : str
 
    Returns
    -------
    list of dicts with keys:
        project_key, webapp_id, name, type (BOKEH | DASH | STANDARD | SHINY | custom-visual-webapps)
    """
    
    project = get_project(project_key)
    try:
        webapps = project.list_webapps()
    except Exception as exc:
        webapps = []
        
    results = []
 
    for webapp in webapps:
        results.append({
            "project_key": project_key,
            "webapp_id": webapp.get("id", ""),
            "name": webapp.get("name", ""),
            "type": webapp.get("type", ""),
            "tags": webapp.get("tags", [])
        })
 
    return results


def get_project_api_services(project_key: str) -> list[dict[str, Any]]:
    """
    Return a summary of every API service and its endpoints in the project.
 
    Each row in the returned list represents one endpoint, so a service with
    three endpoints will produce three rows (all sharing the same service_id).
 
    Parameters
    ----------
    project_key : str
 
    Returns
    -------
    list of dicts with keys:
        project_key, service_id, service_name, endpoint_id, endpoint_type, endpoint_model_id
    """
    
    project = get_project(project_key)
    try:
        api_services = project.list_api_services()
    except Exception as exc:
        api_services = []
        
    results = []
    
    for api_service_details in api_services:
        api_service = project.get_api_service(api_service_details['id'])
        endpoints = api_service.get_settings().settings.get('endpoints', [])
        for endpoint in endpoints:
            results.append({
                "project_key": project_key,
                "api_service_id": api_service_details.get('id', ''),
                "api_service_name": api_service_details.get('name', ''),
                "endpoint_id": endpoint.get('id', ''),
                "endpoint_type": endpoint.get('type', ''),
                "endpoint_model_id": endpoint.get('modelRef', ''),
                "tags": endpoint.get('tags', [])
            })

    return results


def get_project_models(project_key: str) -> list[dict[str, Any]]:
    """
    Return a summary of every saved model (Lab + deployed) in the project.
 
    Note: This covers *saved models* (the versioned model objects), not
    in-progress Lab designs. Each row is one model; active version info
    is included where available.
 
    Parameters
    ----------
    project_key : str
 
    Returns
    -------
    list of dicts with keys:
        project_key, model_id, name, type (PREDICTION | CLUSTERING | ...),
        active_version_id, algorithm, tags
    """
    
    computer_vision_prediction_types = ['DEEP_HUB_IMAGE_CLASSIFICATION', 'DEEP_HUB_IMAGE_OBJECT_DETECTION']
    
    project = get_project(project_key)
    try:
        saved_models = project.list_saved_models()
    except Exception as exc:
        saved_models = []
        
    results = []
    
    for saved_model in saved_models:
        sm = project.get_saved_model(saved_model['id'])
        
        has_versions = False
        if sm.list_versions():
            has_versions = True
            active_version_id = sm.get_active_version().get('id')
        
        saved_model_type = saved_model.get('type', '')
        prediction_type = saved_model.get('predictionType', '')
        
        target_variable, algorithm = '', ''
        
        if prediction_type in computer_vision_prediction_types:
            target_variable = sm.get_settings().settings.get('miniTask', {}).get('targetVariable', '')
            
            trained_on = 0
            if has_versions:
                trained_on = sm.get_active_version().get('trainDate', 0)
        else:
            if has_versions:
                active_version_details = sm.get_version_details(active_version_id).details

                if saved_model_type != 'CLUSTERING':
                    target_variable = active_version_details.get('coreParams', {}).get('target_variable', '')

                algorithm = active_version_details.get('modeling', {}).get('algorithm', '')
                trained_on = active_version_details.get('trainInfo', {}).get('endTime', 0)
            else:
                target_variable, algorith = '', ''
                trained_on = 0
        
        if saved_model_type != 'LLM_GENERIC_RAW':
            results.append({
                "project_key": project_key,
                "saved_model_id": saved_model.get('id', ''),
                "name": saved_model.get('name', ''),
                "type": saved_model_type,
                "prediction_type": prediction_type,
                "target_variable": target_variable,
                "algorithm": algorithm,
                "trained_on": trained_on,
                "tags": saved_model.get('tags', [])
            })
        
#     for saved_model in saved_models:
#         sm = project.get_saved_model(saved_model['id'])
        
#         try:
#             active_version_id = sm.get_active_version().get('id')
            
#             saved_model_type = saved_model.get('type', '')
#             prediction_type = saved_model.get('predictionType', '')

#             computer_vision_prediction_types = ['DEEP_HUB_IMAGE_CLASSIFICATION', 'DEEP_HUB_IMAGE_OBJECT_DETECTION']

#             target_variable, algorithm = '', ''

#             if prediction_type in computer_vision_prediction_types:
#                 target_variable = sm.get_settings().settings.get('miniTask', {}).get('targetVariable', '')
#                 trained_on = sm.get_active_version().get('trainDate', 0)
#             else:
#                 active_version_details = sm.get_version_details(active_version_id).details

#                 if saved_model_type != 'CLUSTERING':
#                     target_variable = active_version_details.get('coreParams', {}).get('target_variable', '')

#                 algorithm = active_version_details.get('modeling', {}).get('algorithm', '')
#                 trained_on = active_version_details.get('trainInfo', {}).get('endTime', 0)
                
#             results.append({
#                 "project_key": project_key,
#                 "saved_model_id": saved_model.get('id', ''),
#                 "name": saved_model.get('name', ''),
#                 "type": saved_model_type,
#                 "prediction_type": prediction_type,
#                 "target_variable": target_variable,
#                 "algorithm": algorithm,
#                 "trained_on": trained_on,
#                 "tags": saved_model.get('tags', [])
#             })
#         except:
#             results.append({
#                 "project_key": project_key,
#                 "saved_model_id": saved_model.get('id', ''),
#                 "name": saved_model.get('name', ''),
#                 "type": '',
#                 "prediction_type": '',
#                 "target_variable": '',
#                 "algorithm": '',
#                 "trained_on": 0,
#                 "tags": saved_model.get('tags', [])
#             })
    
    return results


def get_project_agents(project_key: str) -> list[dict[str, Any]]:
    """
    Return a summary of every LLM Agent defined in the project.
 
    Parameters
    ----------
    project_key : str
 
    Returns
    -------
    list of dicts with keys:
        project_key, agent_id, name, llm_id, tool_count, tags
    """
    
    project = get_project(project_key)
    try:
        agents = project.list_agents()
    except Exception as exc:
        agents = []
        
    results = []

    for agent in agents:
        results.append({
            "project_key": project_key,
            "agent_id": agent.get("id", ""),
            "name": agent.get("name", ""),
            "type": agent.get("type", ""),
            "tags": agent.get("tags", [])
        })
 
    return results


