# This file contains the ecosystem tool additions for the MCP server

# Add these methods to the BMLServer class:

def get_ecosystem_config(self, repo: str = None) -> dict:
    """Get current ecosystem.json configuration from a repository"""
    repo = repo or self.default_repo
    
    import subprocess
    try:
        cmd = f'gh api repos/{repo}/contents/ecosystem.json'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        
        file_data = json.loads(result.stdout)
        content = base64.b64decode(file_data['content']).decode('utf-8')
        
        return {
            'repo': repo,
            'config': json.loads(content),
            'sha': file_data['sha'],
            'success': True
        }
    except Exception as e:
        return {
            'repo': repo,
            'config': None,
            'sha': None,
            'success': False,
            'error': str(e)
        }

def add_repo_to_ecosystem(self, meta_repo: str, target_repo: str, section: str) -> dict:
    """Add a repository to an ecosystem section"""
    import subprocess
    
    try:
        # Get current config
        current = self.get_ecosystem_config(meta_repo)
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
        content = json.dumps(config, indent=2)
        encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        cmd = f'gh api repos/{meta_repo}/contents/ecosystem.json -f message="Add {target_repo} to {section} section" -f content="{encoded_content}" -f sha="{sha}"'
        subprocess.run(cmd, shell=True, check=True)
        
        return {
            'success': True,
            'meta_repo': meta_repo,
            'target_repo': target_repo,
            'section': section,
            'message': f'Successfully added {target_repo} to {section} section in {meta_repo}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def create_ecosystem_repo(self, repo_name: str, ecosystem_type: str = 'ecosystem_meta') -> dict:
    """Create a new repository with ecosystem configuration"""
    import subprocess
    
    try:
        # Create repository
        owner = repo_name.split('/')[0]
        name = repo_name.split('/')[1]
        
        private_flag = '--private' if ecosystem_type == 'personal_meta' else '--public'
        description = f'HEAVEN {ecosystem_type.replace("_", " ").title()} Repository'
        
        cmd = f'gh repo create {repo_name} {private_flag} --description "{description}"'
        subprocess.run(cmd, shell=True, check=True)
        
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
        
        cmd = f'gh api repos/{repo_name}/contents/ecosystem.json -f message="Initialize ecosystem configuration" -f content="{encoded_content}"'
        subprocess.run(cmd, shell=True, check=True)
        
        # Install ecosystem README workflow
        self.install_bml_workflows(repo_name)
        
        return {
            'success': True,
            'repo_name': repo_name,
            'ecosystem_type': ecosystem_type,
            'message': f'Ecosystem repository {repo_name} created successfully with {ecosystem_type} configuration'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# Add these tool definitions to list_tools():

Tool(
    name=BMLTools.GET_ECOSYSTEM_CONFIG.value,
    description="Get current ecosystem.json configuration from a repository. Shows the structured configuration including sections, repo lists, and settings for ecosystem/personal meta repositories.",
    inputSchema={
        "type": "object",
        "properties": {
            "repo": {
                "type": "string",
                "description": f"GitHub repository (default: {default_repo})",
            }
        },
        "required": [],
    },
),
Tool(
    name=BMLTools.ADD_REPO_TO_ECOSYSTEM.value,
    description="Add a repository to an ecosystem section. This updates the ecosystem.json configuration to include the target repository in the specified section, automatically creating the section if it doesn't exist.",
    inputSchema={
        "type": "object",
        "properties": {
            "meta_repo": {
                "type": "string",
                "description": "Meta repository containing ecosystem.json",
            },
            "target_repo": {
                "type": "string",
                "description": "Repository to add to the ecosystem",
            },
            "section": {
                "type": "string",
                "description": "Section name (e.g., 'Core Libraries', 'Tools', 'Active Projects')",
            }
        },
        "required": ["meta_repo", "target_repo", "section"],
    },
),
Tool(
    name=BMLTools.CREATE_ECOSYSTEM_REPO.value,
    description="Create a new ecosystem repository with automatic configuration. Creates either a public ecosystem meta repo (for showcasing projects) or private personal meta repo (for personal coordination) with pre-configured ecosystem.json and README generation workflows.",
    inputSchema={
        "type": "object",
        "properties": {
            "repo_name": {
                "type": "string",
                "description": "Repository name in format 'owner/repo'",
            },
            "ecosystem_type": {
                "type": "string",
                "enum": ["ecosystem_meta", "personal_meta"],
                "description": "Type of ecosystem repo: ecosystem_meta (public showcase) or personal_meta (private coordination)",
            }
        },
        "required": ["repo_name"],
    },
),

# Add these cases to call_tool():

case BMLTools.GET_ECOSYSTEM_CONFIG.value:
    result = bml_server.get_ecosystem_config(arguments.get("repo"))

case BMLTools.ADD_REPO_TO_ECOSYSTEM.value:
    meta_repo = arguments.get("meta_repo")
    target_repo = arguments.get("target_repo")
    section = arguments.get("section")
    if not all([meta_repo, target_repo, section]):
        raise ValueError("Missing required arguments: meta_repo, target_repo, section")
    result = bml_server.add_repo_to_ecosystem(meta_repo, target_repo, section)

case BMLTools.CREATE_ECOSYSTEM_REPO.value:
    repo_name = arguments.get("repo_name")
    if not repo_name:
        raise ValueError("Missing required argument: repo_name")
    result = bml_server.create_ecosystem_repo(
        repo_name,
        arguments.get("ecosystem_type", "ecosystem_meta")
    )