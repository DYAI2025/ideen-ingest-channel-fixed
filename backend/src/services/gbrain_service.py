"""
GBrain Integration Service
Handles communication with GBrain CLI for importing and querying ideas
"""
import subprocess
import asyncio
from pathlib import Path
from typing import Optional, Dict, List
import json
from datetime import datetime
from ..core.config import settings

class GBrainService:
    """Service for GBrain CLI operations"""
    
    def __init__(self):
        self.source = settings.gbrain_source
        self.gbrain_path = settings.gbrain_path
        self.gbrain_command = settings.gbrain_command
    
    async def import_file_to_gbrain(self, file_path: Path, phase: str = "seed") -> Dict:
        """
        Import a file to GBrain with automatic phase tagging
        
        Args:
            file_path: Path to the file to import
            phase: Phase to tag the idea with (seed, sprout, growth, flower, harvest)
        
        Returns:
            Import result with status and details
        """
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add phase tag if not present
            if phase and "---" in content:
                # Insert phase after the first line of frontmatter
                lines = content.split('\n', 1)
                first_line = lines[0]
                if first_line.startswith("---"):
                    # Insert phase after existing frontmatter
                    content = content.replace("---\n", f"---\nphase: {phase}\n", 1)
                else:
                    # Add frontmatter with phase
                    frontmatter = f"""---
phase: {phase}
date: {datetime.now().strftime("%Y-%m-%d")}
---
{content}"""
            elif phase:
                # Add frontmatter to files without it
                frontmatter = f"""---
phase: {phase}
date: {datetime.now().strftime("%Y-%m-%d")}
---
{content}"""
            
            # Save the modified content temporarily
            temp_file = file_path.with_suffix('.temp.md')
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Import to GBrain
            result = await self._run_gbrain_command([
                "put",
                file_path.stem,
                str(temp_file),
                "--source", self.source
            ])
            
            # Clean up temp file
            temp_file.unlink()
            
            # Extract slug from result
            slug = file_path.stem
            if "slug" in result:
                # Parse slug from GBrain output
                import re
                slug_match = re.search(r'slug["\s*:\s*([^\s"]+)', result)
                if slug_match:
                    slug = slug_match.group(1)
            
            return {
                "status": "success",
                "slug": slug,
                "phase": phase,
                "file": str(file_path),
                "timestamp": datetime.now().isoformat(),
                "gbrain_output": result
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "file": str(file_path),
                "timestamp": datetime.now().isoformat()
            }
    
    async def query_ideas(self, query: str, phase: Optional[str] = None) -> List[Dict]:
        """
        Query GBrain for ideas matching the query
        
        Args:
            query: Search query
            phase: Optional phase filter
        
        Returns:
            List of matching ideas with metadata
        """
        try:
            args = ["query", query, "--source", self.source]
            
            # Add phase filter if specified
            if phase:
                args.extend(["--tag", phase])
            
            result = await self._run_gbrain_command(args)
            
            # Parse results
            ideas = self._parse_gbrain_query_result(result)
            
            return ideas
            
        except Exception as e:
            return [{
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }]
    
    async def get_idea_graph(self, slug: str, depth: int = 2) -> Dict:
        """
        Get the graph structure for an idea
        
        Args:
            slug: Idea slug
            depth: Traversal depth
        
        Returns:
            Graph structure with nodes and edges
        """
        try:
            result = await self._run_gbrain_command([
                "graph",
                slug,
                "--depth", str(depth),
                "--source", self.source
            ])
            
            # Parse graph result
            graph = self._parse_gbrain_graph_result(result)
            
            return graph
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def list_ideas(self, phase: Optional[str] = None) -> List[Dict]:
        """
        List all ideas in the system
        
        Args:
            phase: Optional phase filter
        
        Returns:
            List of ideas with metadata
        """
        try:
            args = ["list", "--source", self.source]
            
            if phase:
                args.extend(["--tag", phase])
            
            result = await self._run_gbrain_command(args)
            
            # Parse list result
            ideas = self._parse_gbrain_list_result(result)
            
            return ideas
            
        except Exception as e:
            return [{
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }]
    
    async def create_link(self, from_slug: str, to_slug: str, link_type: str = "evolves_into") -> Dict:
        """
        Create a link between two ideas
        
        Args:
            from_slug: Source idea slug
            to_slug: Target idea slug
            link_type: Type of relationship
        
        Returns:
            Link creation result
        """
        try:
            result = await self._run_gbrain_command([
                "link",
                from_slug,
                to_slug,
                "--type", link_type,
                "--source", self.source
            ])
            
            return {
                "status": "success",
                "from": from_slug,
                "to": to_slug,
                "type": link_type,
                "timestamp": datetime.now().isoformat(),
                "gbrain_output": result
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_idea_details(self, slug: str) -> Dict:
        """
        Get detailed information about an idea
        
        Args:
            slug: Idea slug
        
        Returns:
        """
        try:
            result = await self._run_gbrain_command([
                "get",
                slug,
                "--source", self.source
            ])
            
            return {
                "status": "success",
                "slug": slug,
                "content": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "slug": slug,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _run_gbrain_command(self, args: List[str]) -> str:
        """
        Run a GBrain command asynchronously
        
        Args:
            args: Command arguments
        
        Returns:
            Command output
        """
        process = await asyncio.create_subprocess_exec(
            self.gbrain_command,
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            error_message = stderr.decode('utf-8').strip()
            raise Exception(f"GBrain command failed: {error_message}")
        
        return stdout.decode('utf-8').strip()
    
    def _parse_gbrain_query_result(self, result: str) -> List[Dict]:
        """Parse GBrain query result into structured data"""
        ideas = []
        lines = result.split('\n')
        
        for line in lines:
            if line.strip() and not line.startswith('['):
                # Parse score and slug
                if '] ' in line and '--' in line:
                    try:
                        # Format: [score] slug -- snippet
                        parts = line.split('] ', 1)
                        score = float(parts[0].strip('[]'))
                        remaining = parts[1].split('--', 1)
                        slug = remaining[0].strip()
                        snippet = remaining[1].strip() if len(remaining) > 1 else ""
                        
                        ideas.append({
                            "slug": slug,
                            "score": score,
                            "snippet": snippet
                        })
                    except (ValueError, IndexError):
                        continue
        
        return ideas
    
    def _parse_gbrain_graph_result(self, result: str) -> Dict:
        """Parse GBrain graph result into structured data"""
        # This is a simplified parser - actual implementation would need to handle
        # the specific output format of gbrain graph command
        return {
            "status": "success",
            "raw_output": result,
            "timestamp": datetime.now().isoformat()
        }
    
    def _parse_gbrain_list_result(self, result: str) -> List[Dict]:
        """Parse GBrain list result into structured data"""
        ideas = []
        lines = result.split('\n')
        
        for line in lines:
            if line.strip() and '\t' in line:
                # Format: slug    type    date    title
                parts = line.split('\t')
                if len(parts) >= 4:
                    ideas.append({
                        "slug": parts[0].strip(),
                        "type": parts[1].strip(),
                        "date": parts[2].strip(),
                        "title": parts[3].strip()
                    })
        
        return ideas