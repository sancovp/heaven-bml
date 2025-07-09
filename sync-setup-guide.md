# Meta-Repo Sync Setup Guide

## Quick Setup for Testing

### 1. In your private sub-repo (e.g., heaven-base-private):

1. Add the sync-sender.yml workflow
2. Create these secrets:
   - `META_REPO_TOKEN`: Your GitHub PAT with repo access
   
3. Create this variable:
   - `META_REPO_NAME`: `sancovp/private_heaven_meta_workspace`

### 2. In your personal meta repo (private_heaven_meta_workspace):

1. Add both sync-receiver.yml and archive-closer.yml workflows
2. Ensure the default GITHUB_TOKEN has issues write access
3. Add secret:
   - `META_REPO_TOKEN`: Same PAT (for closing issues in sub-repos)

### 3. Test the sync:

1. Create an issue in your sub-repo
2. Watch it appear in meta-repo with `[repo#123]` prefix
3. Change labels in sub-repo, see them sync
4. Add `status-archived` label in meta-repo
5. Verify original issue gets closed

## How It Works

1. **Issue Creation**: Create in sub-repo → Webhook to meta → Wrapper created
2. **Issue Updates**: Any label/state change → Webhook → Wrapper updated  
3. **Archival**: Add status-archived in meta → Original closed

## Next Steps

Once this prototype works, we'll:
1. Add these workflows to the MCP create_repo function
2. Add repo_type support to MCP
3. Add personal meta repo creation function
4. Add subscription management for meta repos