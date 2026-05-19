#!/usr/bin/env python3
"""
Autonomous Agency Orchestrator
Uses OpenRouter Freemium Models as strategic brain, delegates to local WUPHF agents
"""

import os
import json
import time
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

# Load .env file if it exists
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

class OrchestratorModel(Enum):
    """Freemium models from OpenRouter for strategic decisions"""
    FREE_ROUTER = "openrouter/free"  # Auto-selects best free model
    DEEPSEEK_FLASH = "deepseek/deepseek-r1:free"  # Fast reasoning
    TRINITY_LARGE = "arcee-ai/trinity-large-thinking:free"  # Complex reasoning
    NEMOTRON_SUPER = "nvidia/nemotron-3-super:free"  # General purpose

@dataclass
class AgentTask:
    """Task delegation to local WUPHF agent"""
    agent_slug: str
    task_description: str
    priority: str = "normal"
    deadline: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

@dataclass
class OrchestratorDecision:
    """Strategic decision from cloud orchestrator"""
    action: str
    reasoning: str
    agent_tasks: List[AgentTask]
    confidence: float
    model_used: str

class OpenRouterOrchestrator:
    """Cloud orchestrator using OpenRouter freemium models"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY", "")
        self.base_url = "https://openrouter.ai/api/v1"
        self.fallback_models = [
            OrchestratorModel.FREE_ROUTER.value,
            OrchestratorModel.DEEPSEEK_FLASH.value,
            OrchestratorModel.TRINITY_LARGE.value,
            OrchestratorModel.NEMOTRON_SUPER.value
        ]
        self.current_model_index = 0
    
    def _make_request(self, messages: List[Dict], model: str) -> Dict:
        """Make request to OpenRouter API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error calling OpenRouter: {e}")
            return None
    
    def make_strategic_decision(self, context: str, decision_type: str) -> OrchestratorDecision:
        """Make strategic decision using freemium models with fallback"""
        
        system_prompt = f"""You are the strategic orchestrator for an autonomous pitch deck agency. 
Your role is to analyze situations and delegate tasks to specialist agents.

Available agents:
- pm: Project Manager (planning, coordination)
- designer: Visual Design (pitch decks, branding) 
- cmo: Marketing (content, outreach, messaging)
- cro: Sales (closing, negotiation, customer management)
- sdr: Lead Generation (prospecting, outreach)
- research: Market Research (analysis, competitive intelligence)
- content: Content Creation (copywriting, messaging)
- analyst: Performance Analysis (metrics, optimization)

Decision types: {decision_type}

Respond in JSON format:
{{
    "action": "specific action to take",
    "reasoning": "why this action is best",
    "agent_tasks": [
        {{
            "agent_slug": "agent name",
            "task_description": "specific task",
            "priority": "high/normal/low",
            "context": {{}}
        }}
    ],
    "confidence": 0.0-1.0
}}"""

        user_prompt = f"Context: {context}\n\nWhat strategic decision should I make for {decision_type}?"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Try models in fallback order
        for i in range(len(self.fallback_models)):
            model = self.fallback_models[i]
            print(f"Trying model: {model}")
            
            response = self._make_request(messages, model)
            if response and "choices" in response:
                try:
                    content = response["choices"][0]["message"]["content"]
                    # Try to parse JSON from response
                    import re
                    json_match = re.search(r'\{[\s\S]*\}', content)
                    if json_match:
                        decision_data = json.loads(json_match.group())
                        
                        agent_tasks = [
                            AgentTask(
                                agent_slug=task["agent_slug"],
                                task_description=task["task_description"],
                                priority=task.get("priority", "normal"),
                                context=task.get("context")
                            )
                            for task in decision_data.get("agent_tasks", [])
                        ]
                        
                        return OrchestratorDecision(
                            action=decision_data["action"],
                            reasoning=decision_data["reasoning"],
                            agent_tasks=agent_tasks,
                            confidence=decision_data.get("confidence", 0.8),
                            model_used=model
                        )
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Failed to parse response from {model}: {e}")
                    continue
            
            print(f"Model {model} failed, trying next...")
            time.sleep(1)  # Rate limiting between attempts
        
        # Fallback to simple decision if all models fail
        return OrchestratorDecision(
            action="proceed with manual delegation",
            reasoning="All cloud models failed, using fallback",
            agent_tasks=[],
            confidence=0.3,
            model_used="fallback"
        )

class WUPHFAgentInterface:
    """Interface to local WUPHF agents"""
    
    def __init__(self, wuphf_broker_url: str = "http://127.0.0.1:7890"):
        self.broker_url = wuphf_broker_url
    
    def delegate_task(self, task: AgentTask) -> bool:
        """Delegate task to local WUPHF agent via broker API"""
        try:
            # Try to send task via broker API
            payload = {
                "channel": "general",
                "from": "orchestrator",
                "content": f"@{task.agent_slug} {task.task_description}"
            }
            
            response = requests.post(
                f"{self.broker_url}/api/broker/message",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ Task delegated to {task.agent_slug}: {task.task_description}")
                return True
            else:
                print(f"❌ Failed to delegate to {task.agent_slug}: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error delegating to {task.agent_slug}: {e}")
            return False
    
    def create_wiki_task(self, task: AgentTask) -> bool:
        """Create task in WUPHF wiki for agent to pick up"""
        try:
            wiki_path = os.path.expanduser("~/.wuphf/wiki/tasks")
            os.makedirs(wiki_path, exist_ok=True)
            
            task_file = os.path.join(wiki_path, f"{task.agent_slug}-task-{int(time.time())}.md")
            
            content = f"""# Task for {task.agent_slug}

Priority: {task.priority}
Deadline: {task.deadline or 'ASAP'}

## Task
{task.task_description}

## Context
{json.dumps(task.context, indent=2) if task.context else 'None'}

## From Orchestrator
This task was generated by the cloud orchestrator based on strategic analysis.
"""
            
            with open(task_file, 'w') as f:
                f.write(content)
            
            print(f"✅ Wiki task created for {task.agent_slug}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating wiki task: {e}")
            return False

class AutonomousAgencyOrchestrator:
    """Main orchestrator combining cloud intelligence with local execution"""
    
    def __init__(self, openrouter_api_key: Optional[str] = None):
        self.cloud_orchestrator = OpenRouterOrchestrator(openrouter_api_key)
        self.wuphf_interface = WUPHFAgentInterface()
        self.decision_history = []
    
    def execute_strategy(self, context: str, decision_type: str = "general") -> bool:
        """Execute strategic decision with local agent delegation"""
        print(f"\n🧠 Cloud Orchestrator analyzing: {decision_type}")
        print(f"📋 Context: {context[:100]}...")
        
        # Get strategic decision from cloud
        decision = self.cloud_orchestrator.make_strategic_decision(context, decision_type)
        
        print(f"\n🎯 Strategic Decision: {decision.action}")
        print(f"💭 Reasoning: {decision.reasoning}")
        print(f"🤖 Model Used: {decision.model_used}")
        print(f"📊 Confidence: {decision.confidence:.2f}")
        
        # Record decision
        self.decision_history.append({
            "timestamp": time.time(),
            "decision_type": decision_type,
            "decision": decision.action,
            "model_used": decision.model_used,
            "confidence": decision.confidence
        })
        
        # Delegate tasks to local agents
        if decision.agent_tasks:
            print(f"\n🚀 Delegating {len(decision.agent_tasks)} tasks to local agents...")
            
            success_count = 0
            for task in decision.agent_tasks:
                # Try broker API first, fall back to wiki
                if not self.wuphf_interface.delegate_task(task):
                    self.wuphf_interface.create_wiki_task(task)
                    success_count += 1
                else:
                    success_count += 1
                
                time.sleep(0.5)  # Rate limiting
            
            print(f"✅ Successfully delegated {success_count}/{len(decision.agent_tasks)} tasks")
            return success_count > 0
        else:
            print("⚠️ No agent tasks to delegate")
            return False
    
    def launch_campaign(self, campaign_type: str = "lead_generation") -> bool:
        """Launch a specific campaign type"""
        contexts = {
            "lead_generation": "We need to generate 100 qualified leads for B2B SaaS startups in DACH region. Target: Pre-Seed to Series A, 5-50 employees, seeking €500K-€5M funding.",
            "outreach": "We have 100 identified leads and need to launch outreach campaign via email and LinkedIn. Goal: 20% response rate, 5% meeting booking rate.",
            "delivery": "We have closed first customer and need to deliver pitch deck project. Requirements: 12-slide investor deck, B2B SaaS focus, 48h turnaround.",
            "optimization": "We have completed first week of operations. Need to analyze performance metrics and optimize strategy for next week."
        }
        
        context = contexts.get(campaign_type, "General agency operations")
        return self.execute_strategy(context, campaign_type)

def main():
    """CLI interface for the orchestrator"""
    import sys
    
    # Check for API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY environment variable not set")
        print("Get your free API key from: https://openrouter.ai/keys")
        print("Then run: export OPENROUTER_API_KEY='your-key-here'")
        sys.exit(1)
    
    orchestrator = AutonomousAgencyOrchestrator(api_key)
    
    if len(sys.argv) < 2:
        print("Usage: python orchestrator.py <command>")
        print("Commands:")
        print("  launch_campaign - Launch lead generation campaign")
        print("  outreach - Start outreach sequence")
        print("  delivery - Execute project delivery")
        print("  optimize - Analyze and optimize performance")
        print("  custom <context> - Custom strategic decision")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "launch_campaign":
        success = orchestrator.launch_campaign("lead_generation")
    elif command == "outreach":
        success = orchestrator.launch_campaign("outreach")
    elif command == "delivery":
        success = orchestrator.launch_campaign("delivery")
    elif command == "optimize":
        success = orchestrator.launch_campaign("optimization")
    elif command == "custom":
        if len(sys.argv) < 3:
            print("Usage: python orchestrator.py custom <context>")
            sys.exit(1)
        context = " ".join(sys.argv[2:])
        success = orchestrator.execute_strategy(context, "custom")
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
    
    if success:
        print("\n✅ Orchestrator execution completed successfully")
        sys.exit(0)
    else:
        print("\n❌ Orchestrator execution failed")
        sys.exit(1)

if __name__ == "__main__":
    main()