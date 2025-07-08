"""
HEAVEN BML MCP Server
Build-Measure-Learn GitHub project management for AI agents
"""
from .server import serve


def main():
    """Main entry point for BML MCP Server"""
    import argparse
    import asyncio
    
    parser = argparse.ArgumentParser(
        description="HEAVEN BML MCP Server - GitHub project management for AI agents"
    )
    parser.add_argument(
        "--default-repo", 
        type=str, 
        default="sancovp/heaven-base",
        help="Default GitHub repository (format: owner/repo)"
    )
    
    args = parser.parse_args()
    asyncio.run(serve(args.default_repo))


if __name__ == "__main__":
    main()