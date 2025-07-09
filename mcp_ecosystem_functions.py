"""
MCP functions for ecosystem management.

These functions will be integrated into the main MCP server to allow
dynamic ecosystem.json updates and README generation.
"""

import json
import base64
import requests
from typing import Dict, List, Any, Optional

def get_ecosystem_config(repo: str, github_token: str) -> Dict[str, Any]:
    """Get current ecosystem.json configuration from a repository."""
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        url = f'https://api.github.com/repos/{repo}/contents/ecosystem.json'
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        file_data = response.json()
        content = base64.b64decode(file_data['content']).decode('utf-8')
        
        return {
            'config': json.loads(content),
            'sha': file_data['sha'],
            'success': True
        }
    except Exception as e:
        return {
            'config': None,
            'sha': None,
            'success': False,
            'error': str(e)
        }

def update_ecosystem_config(repo: str, config: Dict[str, Any], github_token: str, 
                          sha: Optional[str] = None) -> Dict[str, Any]:
    """Update ecosystem.json configuration in a repository."""
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        # If no SHA provided, get current file SHA
        if not sha:
            current = get_ecosystem_config(repo, github_token)
            if not current['success']:
                return current
            sha = current['sha']
        
        # Encode new content
        content = json.dumps(config, indent=2)
        encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        # Update file
        url = f'https://api.github.com/repos/{repo}/contents/ecosystem.json'
        data = {
            'message': f'Update ecosystem configuration\n\n🤖 Updated via MCP API',
            'content': encoded_content,
            'sha': sha
        }
        
        response = requests.put(url, headers=headers, json=data)
        response.raise_for_status()
        
        return {
            'success': True,
            'message': 'Ecosystem configuration updated successfully',
            'commit': response.json()['commit']
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def add_repo_to_ecosystem(meta_repo: str, target_repo: str, section: str, 
                         github_token: str) -> Dict[str, Any]:
    """Add a repository to an ecosystem section."""
    try:
        # Get current config
        current = get_ecosystem_config(meta_repo, github_token)
        if not current['success']:
            return current
        
        config = current['config']
        sha = current['sha']
        
        # Add repo to section
        if section not in config['sections']:
            config['sections'][section] = {
                'description': f'Auto-created section for {section}',
                'repos': [],
                'auto_discover': True,
                'show_stats': True
            }
        
        if target_repo not in config['sections'][section]['repos']:
            config['sections'][section]['repos'].append(target_repo)
        
        # Update config
        return update_ecosystem_config(meta_repo, config, github_token, sha)
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def remove_repo_from_ecosystem(meta_repo: str, target_repo: str, github_token: str) -> Dict[str, Any]:
    """Remove a repository from all ecosystem sections."""
    try:
        # Get current config
        current = get_ecosystem_config(meta_repo, github_token)
        if not current['success']:
            return current
        
        config = current['config']
        sha = current['sha']
        
        # Remove repo from all sections
        removed_from = []
        for section_name, section_config in config['sections'].items():
            if target_repo in section_config['repos']:
                section_config['repos'].remove(target_repo)
                removed_from.append(section_name)
        
        if removed_from:
            # Update config
            result = update_ecosystem_config(meta_repo, config, github_token, sha)
            if result['success']:
                result['removed_from'] = removed_from
            return result
        else:
            return {
                'success': True,
                'message': f'Repository {target_repo} was not found in any sections'
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def create_ecosystem_repo(repo_name: str, ecosystem_type: str, github_token: str) -> Dict[str, Any]:
    """Create a new repository with ecosystem configuration."""
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        # Create repository
        owner = repo_name.split('/')[0]
        name = repo_name.split('/')[1]
        
        repo_data = {
            'name': name,
            'description': f'HEAVEN {ecosystem_type.replace("_", " ").title()} Repository',
            'private': ecosystem_type == 'personal_meta',
            'has_issues': True,
            'has_projects': True,
            'has_wiki': False
        }
        
        response = requests.post(
            f'https://api.github.com/user/repos',
            headers=headers,
            json=repo_data
        )
        response.raise_for_status()
        
        # Create initial ecosystem.json
        if ecosystem_type == 'personal_meta':
            initial_config = {
                'name': 'Personal Development Hub',
                'description': 'Central coordination for all development projects',
                'type': 'personal_meta',
                'sections': {
                    'Active Projects': {
                        'description': 'Currently active development work',
                        'repos': [],
                        'auto_discover': True,
                        'show_stats': True,
                        'show_issues': True
                    }
                },
                'template': 'personal',
                'auto_update': True,
                'badges': {
                    'version': True,
                    'last_updated': True,
                    'issue_count': True
                }
            }
        else:  # ecosystem_meta
            initial_config = {
                'name': f'{name.replace("-", " ").title()} Ecosystem',
                'description': 'AI Development Ecosystem',
                'type': 'ecosystem_meta',
                'sections': {
                    'Core Libraries': {
                        'description': 'Essential components',
                        'repos': [],
                        'auto_discover': True,
                        'show_stats': True
                    }
                },
                'template': 'ecosystem',
                'auto_update': True,
                'badges': {
                    'license': True,
                    'version': True,
                    'stars': True,
                    'last_updated': True
                }
            }
        
        # Add ecosystem.json to repo
        content = json.dumps(initial_config, indent=2)
        encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        file_data = {
            'message': 'Initialize ecosystem configuration',
            'content': encoded_content
        }
        
        file_response = requests.put(
            f'https://api.github.com/repos/{repo_name}/contents/ecosystem.json',
            headers=headers,
            json=file_data
        )
        file_response.raise_for_status()
        
        return {
            'success': True,
            'repo_name': repo_name,
            'ecosystem_type': ecosystem_type,
            'message': f'Ecosystem repository {repo_name} created successfully'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }