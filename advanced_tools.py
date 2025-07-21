"""
Advanced tools for Devin AI Assistant with improved architecture.
"""
import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from livekit.agents import function_tool, RunContext
from gemini_client import get_gemini_client, gemini_tool

logger = logging.getLogger(__name__)

@function_tool
@gemini_tool
async def image_analyzer(image_description: str, analysis_type: str, context: RunContext) -> str:
    """
    Analyze images or provide detailed analysis based on description using Gemini Vision.
    
    Args:
        image_description: Description of the image or image data
        analysis_type: Type of analysis ('objects', 'text', 'scene', 'emotions', 'technical')
    """
    client = get_gemini_client()
    
    prompts = {
        'objects': "Identify and describe all objects visible in this image. Provide details about their position, size, and characteristics.",
        'text': "Extract and transcribe any text visible in this image. Maintain formatting and note the style/font if relevant.",
        'scene': "Describe the overall scene, setting, mood, and atmosphere of this image. Include details about lighting, composition, and style.",
        'emotions': "Analyze the emotional content and mood conveyed in this image. Identify any people's expressions and overall emotional tone.",
        'technical': "Provide technical analysis including composition, lighting, color palette, photographic techniques, and quality assessment."
    }
    
    analysis_prompt = prompts.get(analysis_type, prompts['scene'])
    
    prompt = f"""Based on this image description: "{image_description}"

{analysis_prompt}

Provide a detailed, structured analysis."""
    
    response = await client.generate_content(prompt)
    return f"Image Analysis ({analysis_type}):\n{response}"

@function_tool
@gemini_tool
async def document_processor(document_content: str, task: str, context: RunContext) -> str:
    """
    Process documents with various tasks using Gemini AI.
    
    Args:
        document_content: The document content or description
        task: Processing task ('summarize', 'extract_key_points', 'analyze_sentiment', 'translate', 'rewrite')
    """
    client = get_gemini_client()
    
    task_prompts = {
        'summarize': "Create a concise summary of this document, highlighting the main points and conclusions.",
        'extract_key_points': "Extract the key points, important facts, and actionable items from this document in bullet format.",
        'analyze_sentiment': "Analyze the sentiment and tone of this document. Identify emotional indicators and overall mood.",
        'translate': "Translate this document while maintaining its structure and meaning.",
        'rewrite': "Rewrite this document to improve clarity, readability, and professional tone while preserving the original meaning.",
        'legal_review': "Review this document for potential legal issues, unclear terms, and areas that may need clarification.",
        'technical_review': "Review this document for technical accuracy, completeness, and clarity of technical concepts."
    }
    
    task_prompt = task_prompts.get(task, task_prompts['summarize'])
    
    prompt = f"""{task_prompt}

Document content:
{document_content}

Provide a structured response with clear sections."""
    
    response = await client.generate_content(prompt)
    return f"Document Processing ({task}):\n{response}"

@function_tool
async def advanced_search(query: str, search_type: str, context: RunContext) -> str:
    """
    Advanced search with multiple sources and intelligent filtering.
    
    Args:
        query: Search query
        search_type: Type of search ('web', 'academic', 'news', 'technical', 'code')
    """
    try:
        from langchain_community.tools import DuckDuckGoSearchRun
        
        # Enhanced search based on type
        if search_type == 'academic':
            enhanced_query = f"site:scholar.google.com OR site:arxiv.org OR site:researchgate.net {query}"
        elif search_type == 'news':
            enhanced_query = f"{query} site:reuters.com OR site:bbc.com OR site:ap.org"
        elif search_type == 'technical':
            enhanced_query = f"{query} site:stackoverflow.com OR site:github.com OR documentation"
        elif search_type == 'code':
            enhanced_query = f"{query} code examples site:github.com OR site:gitlab.com"
        else:
            enhanced_query = query
        
        search_tool = DuckDuckGoSearchRun()
        results = await search_tool.arun(tool_input=enhanced_query)
        
        if not results:
            return f"No {search_type} results found for: {query}"
        
        # Use Gemini to filter and enhance results
        client = get_gemini_client()
        filter_prompt = f"""Filter and enhance these search results for the query "{query}" with focus on {search_type} content:

{results}

Please:
1. Remove irrelevant results
2. Rank results by relevance and quality
3. Provide a brief summary of each relevant result
4. Highlight key insights or findings
"""
        
        enhanced_results = await client.generate_content(filter_prompt)
        return f"Enhanced {search_type.title()} Search Results:\n{enhanced_results}"
        
    except Exception as e:
        logger.error(f"Advanced search error: {e}")
        return f"Search error: {str(e)}"

@function_tool
@gemini_tool
async def meeting_assistant(meeting_data: str, task: str, context: RunContext) -> str:
    """
    AI assistant for meeting-related tasks.
    
    Args:
        meeting_data: Meeting transcript, notes, or agenda
        task: Task to perform ('summarize', 'action_items', 'schedule_followup', 'generate_agenda')
    """
    client = get_gemini_client()
    
    task_prompts = {
        'summarize': """Summarize this meeting, including:
1. Key discussion points
2. Decisions made
3. Important announcements
4. Attendee participation highlights""",
        
        'action_items': """Extract action items from this meeting:
1. Specific tasks assigned
2. Person responsible
3. Deadlines mentioned
4. Priority level
5. Dependencies""",
        
        'schedule_followup': """Based on this meeting, suggest follow-up actions:
1. Required follow-up meetings
2. Recommended timeline
3. Key stakeholders to include
4. Agenda items for next meeting""",
        
        'generate_agenda': """Generate a comprehensive meeting agenda based on this information:
1. Clear objectives
2. Time allocations
3. Discussion topics
4. Decision points
5. Action items review"""
    }
    
    prompt = f"""{task_prompts.get(task, task_prompts['summarize'])}

Meeting Data:
{meeting_data}

Provide a well-structured, actionable response."""
    
    response = await client.generate_content(prompt)
    return f"Meeting Assistant ({task}):\n{response}"

@function_tool
@gemini_tool
async def learning_assistant(topic: str, learning_goal: str, context: RunContext) -> str:
    """
    Personalized learning assistant with curriculum generation.
    
    Args:
        topic: Subject or skill to learn
        learning_goal: Specific learning objective
    """
    client = get_gemini_client()
    
    prompt = f"""Create a personalized learning plan for the topic "{topic}" with the goal: "{learning_goal}"

Please provide:
1. Learning path breakdown (beginner to advanced)
2. Estimated timeline
3. Key concepts to master
4. Recommended resources and materials
5. Practice exercises and projects
6. Assessment methods
7. Common pitfalls to avoid
8. Prerequisites (if any)
9. Career applications

Make it practical and actionable with specific steps."""
    
    response = await client.generate_content(prompt)
    return f"Learning Plan for {topic}:\n{response}"

@function_tool
async def system_monitor(context: RunContext) -> str:
    """
    Enhanced system monitoring with intelligent alerts.
    """
    try:
        import psutil
        import platform
        
        # Collect comprehensive system data
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/' if platform.system() != 'Windows' else 'C:')
        
        # Network statistics
        net_io = psutil.net_io_counters()
        
        # Process information
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                if proc.info['cpu_percent'] > 5 or proc.info['memory_percent'] > 5:
                    processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort by CPU usage
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        top_processes = processes[:5]
        
        # Generate alerts
        alerts = []
        if cpu_percent > 80:
            alerts.append(f"⚠️ High CPU usage: {cpu_percent:.1f}%")
        if memory.percent > 85:
            alerts.append(f"⚠️ High memory usage: {memory.percent:.1f}%")
        if disk.percent > 90:
            alerts.append(f"⚠️ Low disk space: {disk.percent:.1f}% used")
        
        report = f"""System Performance Report
========================
CPU Usage: {cpu_percent:.1f}%
Memory Usage: {memory.percent:.1f}% ({memory.used // (1024**3):.1f}GB / {memory.total // (1024**3):.1f}GB)
Disk Usage: {disk.percent:.1f}% ({disk.used // (1024**3):.1f}GB / {disk.total // (1024**3):.1f}GB)
Network: ↓{net_io.bytes_recv // (1024**2):.1f}MB ↑{net_io.bytes_sent // (1024**2):.1f}MB

Top Resource-Using Processes:"""
        
        for proc in top_processes:
            report += f"\n- {proc['name']} (PID: {proc['pid']}): CPU {proc['cpu_percent']:.1f}%, RAM {proc['memory_percent']:.1f}%"
        
        if alerts:
            report += "\n\nAlerts:\n" + "\n".join(alerts)
        else:
            report += "\n\n✅ All systems running normally"
        
        return report
        
    except Exception as e:
        return f"System monitoring error: {str(e)}"

@function_tool
@gemini_tool
async def project_manager(project_data: str, task: str, context: RunContext) -> str:
    """
    AI project management assistant.
    
    Args:
        project_data: Project description, requirements, or current status
        task: Management task ('plan', 'timeline', 'risk_analysis', 'resource_allocation', 'status_report')
    """
    client = get_gemini_client()
    
    task_prompts = {
        'plan': """Create a comprehensive project plan including:
1. Project scope and objectives
2. Deliverables breakdown
3. Work breakdown structure (WBS)
4. Dependencies identification
5. Resource requirements
6. Success criteria""",
        
        'timeline': """Develop a realistic project timeline with:
1. Major milestones
2. Critical path identification
3. Buffer time allocation
4. Dependencies mapping
5. Risk contingency time
6. Review and approval phases""",
        
        'risk_analysis': """Conduct thorough risk analysis:
1. Risk identification and categorization
2. Impact and probability assessment
3. Risk mitigation strategies
4. Contingency planning
5. Risk monitoring approach
6. Early warning indicators""",
        
        'resource_allocation': """Optimize resource allocation:
1. Team composition and roles
2. Skill requirements mapping
3. Budget distribution
4. Equipment and tool needs
5. External vendor requirements
6. Capacity planning""",
        
        'status_report': """Generate project status report:
1. Current progress vs. plan
2. Completed deliverables
3. Upcoming milestones
4. Issues and blockers
5. Resource utilization
6. Budget status
7. Recommendations"""
    }
    
    prompt = f"""{task_prompts.get(task, task_prompts['plan'])}

Project Information:
{project_data}

Provide detailed, actionable insights with specific recommendations."""
    
    response = await client.generate_content(prompt)
    return f"Project Management ({task}):\n{response}"
