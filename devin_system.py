"""
DEVIN-like system interaction capabilities for Devin AI Assistant.
Provides secure computer interaction with user permission controls.
"""
import os
import subprocess
import json
import psutil
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import platform
from livekit.agents import function_tool, RunContext
from gemini_client import get_gemini_client, gemini_tool

logger = logging.getLogger(__name__)

class PermissionManager:
    """Manages permissions for system operations."""
    
    def __init__(self):
        self.permissions_file = "system_permissions.json"
        self.load_permissions()
    
    def load_permissions(self):
        """Load permissions from file."""
        try:
            if os.path.exists(self.permissions_file):
                with open(self.permissions_file, 'r') as f:
                    self.permissions = json.load(f)
            else:
                self.permissions = {
                    "file_operations": False,
                    "app_control": False,
                    "system_control": False,
                    "network_operations": False,
                    "automation": False,
                    "auto_approve_safe": False
                }
                self.save_permissions()
        except Exception as e:
            logger.error(f"Error loading permissions: {e}")
            self.permissions = {}
    
    def save_permissions(self):
        """Save permissions to file."""
        try:
            with open(self.permissions_file, 'w') as f:
                json.dump(self.permissions, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving permissions: {e}")
    
    def check_permission(self, operation: str) -> bool:
        """Check if operation is permitted."""
        return self.permissions.get(operation, False)
    
    def request_permission(self, operation: str, description: str) -> str:
        """Request permission for an operation."""
        if self.check_permission(operation):
            return "granted"
        
        return f"Permission required for {operation}: {description}. Use 'grant_permission' tool to allow this operation."

permission_manager = PermissionManager()

@function_tool
async def grant_permission(operation: str, context: RunContext) -> str:
    """
    Grant system permissions to Devin for specific operations.
    
    Args:
        operation: Permission type ('file_operations', 'app_control', 'system_control', 'network_operations', 'automation', 'auto_approve_safe', 'all')
    """
    valid_operations = [
        "file_operations", "app_control", "system_control", 
        "network_operations", "automation", "auto_approve_safe", "all"
    ]
    
    if operation not in valid_operations:
        return f"Invalid operation. Valid operations: {', '.join(valid_operations)}"
    
    if operation == "all":
        for op in valid_operations[:-1]:  # Exclude 'all'
            permission_manager.permissions[op] = True
        message = "✅ All system permissions granted to Devin."
    else:
        permission_manager.permissions[operation] = True
        message = f"✅ Permission granted for {operation}."
    
    permission_manager.save_permissions()
    return message + " Devin can now perform these operations with enhanced capabilities."

@function_tool
async def revoke_permission(operation: str, context: RunContext) -> str:
    """
    Revoke system permissions from Devin.
    
    Args:
        operation: Permission type to revoke ('file_operations', 'app_control', 'system_control', 'network_operations', 'automation', 'auto_approve_safe', 'all')
    """
    valid_operations = [
        "file_operations", "app_control", "system_control", 
        "network_operations", "automation", "auto_approve_safe", "all"
    ]
    
    if operation not in valid_operations:
        return f"Invalid operation. Valid operations: {', '.join(valid_operations)}"
    
    if operation == "all":
        for op in valid_operations[:-1]:
            permission_manager.permissions[op] = False
        message = "🔒 All system permissions revoked from Devin."
    else:
        permission_manager.permissions[operation] = False
        message = f"🔒 Permission revoked for {operation}."
    
    permission_manager.save_permissions()
    return message

@function_tool
async def system_status_report(context: RunContext) -> str:
    """
    Generate a comprehensive DEVIN-style system status report.
    """
    try:
        # System information
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/' if platform.system() != 'Windows' else 'C:')
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        
        # Network status
        net_io = psutil.net_io_counters()
        net_connections = len(psutil.net_connections())
        
        # Running processes
        process_count = len(psutil.pids())
        
        # Battery (if laptop)
        battery_info = ""
        try:
            battery = psutil.sensors_battery()
            if battery:
                battery_info = f"Battery: {battery.percent:.1f}% ({'Charging' if battery.power_plugged else 'Discharging'})\n"
        except:
            pass
        
        report = f"""🤖 DEVIN SYSTEM STATUS REPORT
{'='*50}
System Overview:
  OS: {platform.system()} {platform.release()}
  Uptime: {str(uptime).split('.')[0]}
  Boot Time: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}

Performance Metrics:
  CPU Usage: {cpu_percent:.1f}%
  Memory: {memory.percent:.1f}% ({memory.used // (1024**3):.1f}GB / {memory.total // (1024**3):.1f}GB)
  Disk Space: {disk.percent:.1f}% ({disk.free // (1024**3):.1f}GB free)
  {battery_info}
Network Status:
  Active Connections: {net_connections}
  Data Transfer: ↓{net_io.bytes_recv // (1024**2):.1f}MB ↑{net_io.bytes_sent // (1024**2):.1f}MB

Process Information:
  Running Processes: {process_count}

System Permissions:
  File Operations: {'✅' if permission_manager.check_permission('file_operations') else '❌'}
  App Control: {'✅' if permission_manager.check_permission('app_control') else '❌'}
  System Control: {'✅' if permission_manager.check_permission('system_control') else '❌'}
  Network Operations: {'✅' if permission_manager.check_permission('network_operations') else '❌'}
  Automation: {'✅' if permission_manager.check_permission('automation') else '❌'}

Status: All systems operational, Sir. Ready for your commands."""
        
        return report
        
    except Exception as e:
        return f"Error generating system report: {str(e)}"

@function_tool
async def control_applications(action: str, app_name: str, context: RunContext) -> str:
    """
    Control applications on the system (launch, close, status).
    
    Args:
        action: Action to perform ('launch', 'close', 'status', 'list')
        app_name: Name of the application (for launch/close/status)
    """
    permission_check = permission_manager.request_permission(
        "app_control", 
        f"Control applications: {action} {app_name}"
    )
    
    if permission_check != "granted":
        return permission_check
    
    try:
        if action == "list":
            # List running applications
            apps = []
            for proc in psutil.process_iter(['pid', 'name', 'status']):
                try:
                    if proc.info['status'] == 'running':
                        apps.append(f"- {proc.info['name']} (PID: {proc.info['pid']})")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            return f"Running Applications:\n" + "\n".join(apps[:20])  # Limit to 20
        
        elif action == "launch":
            # Launch application
            if platform.system() == "Windows":
                subprocess.Popen(app_name, shell=True)
            else:
                subprocess.Popen([app_name])
            
            return f"✅ Launching {app_name}, Sir."
        
        elif action == "close":
            # Close application by name
            closed = False
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if app_name.lower() in proc.info['name'].lower():
                        proc.terminate()
                        closed = True
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            if closed:
                return f"✅ {app_name} has been terminated, Sir."
            else:
                return f"❌ Could not find running application: {app_name}"
        
        elif action == "status":
            # Check if application is running
            running = False
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    if app_name.lower() in proc.info['name'].lower():
                        running = True
                        return f"📊 {app_name} Status:\n- PID: {proc.info['pid']}\n- CPU: {proc.info['cpu_percent']:.1f}%\n- Memory: {proc.info['memory_percent']:.1f}%"
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            if not running:
                return f"❌ {app_name} is not currently running."
        
    except Exception as e:
        logger.error(f"App control error: {e}")
        return f"Error controlling application: {str(e)}"

@function_tool
async def file_operations(operation: str, path: str, context: RunContext, content: str = "", destination: str = "") -> str:
    """
    Perform file and folder operations (create, read, move, copy, delete).
    
    Args:
        operation: Operation to perform ('create', 'read', 'move', 'copy', 'delete', 'list')
        path: File or folder path
        content: Content for create operation
        destination: Destination path for move/copy operations
    """
    permission_check = permission_manager.request_permission(
        "file_operations", 
        f"File operation: {operation} on {path}"
    )
    
    if permission_check != "granted":
        return permission_check
    
    try:
        path_obj = Path(path)
        
        if operation == "create":
            if content:
                # Create file with content
                path_obj.write_text(content)
                return f"✅ File created: {path}"
            else:
                # Create directory
                path_obj.mkdir(parents=True, exist_ok=True)
                return f"✅ Directory created: {path}"
        
        elif operation == "read":
            if path_obj.is_file():
                content = path_obj.read_text()
                return f"📄 Content of {path}:\n{content[:1000]}{'...' if len(content) > 1000 else ''}"
            else:
                return f"❌ {path} is not a file or doesn't exist."
        
        elif operation == "list":
            if path_obj.is_dir():
                items = []
                for item in path_obj.iterdir():
                    icon = "📁" if item.is_dir() else "📄"
                    size = f" ({item.stat().st_size} bytes)" if item.is_file() else ""
                    items.append(f"{icon} {item.name}{size}")
                
                return f"📂 Contents of {path}:\n" + "\n".join(items[:20])
            else:
                return f"❌ {path} is not a directory."
        
        elif operation == "move":
            if destination:
                path_obj.rename(destination)
                return f"✅ Moved {path} to {destination}"
            else:
                return "❌ Destination path required for move operation."
        
        elif operation == "copy":
            if destination:
                import shutil
                if path_obj.is_file():
                    shutil.copy2(path, destination)
                else:
                    shutil.copytree(path, destination)
                return f"✅ Copied {path} to {destination}"
            else:
                return "❌ Destination path required for copy operation."
        
        elif operation == "delete":
            if path_obj.exists():
                if path_obj.is_file():
                    path_obj.unlink()
                else:
                    import shutil
                    shutil.rmtree(path)
                return f"✅ Deleted: {path}"
            else:
                return f"❌ {path} doesn't exist."
        
    except Exception as e:
        logger.error(f"File operation error: {e}")
        return f"Error performing file operation: {str(e)}"

@function_tool
async def system_control(action: str, context: RunContext) -> str:
    """
    Control system functions (shutdown, restart, sleep, lock).
    
    Args:
        action: System action ('shutdown', 'restart', 'sleep', 'lock', 'logout')
    """
    permission_check = permission_manager.request_permission(
        "system_control", 
        f"System control: {action}"
    )
    
    if permission_check != "granted":
        return permission_check
    
    try:
        system = platform.system()
        
        if action == "shutdown":
            if system == "Windows":
                os.system("shutdown /s /t 10")
            else:
                os.system("shutdown -h +1")
            return "⚡ System shutdown initiated. Shutting down in 10 seconds, Sir."
        
        elif action == "restart":
            if system == "Windows":
                os.system("shutdown /r /t 10")
            else:
                os.system("shutdown -r +1")
            return "🔄 System restart initiated. Restarting in 10 seconds, Sir."
        
        elif action == "sleep":
            if system == "Windows":
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            else:
                os.system("systemctl suspend")
            return "😴 Putting system to sleep, Sir."
        
        elif action == "lock":
            if system == "Windows":
                os.system("rundll32.exe user32.dll,LockWorkStation")
            else:
                os.system("gnome-screensaver-command -l")
            return "🔒 System locked, Sir."
        
        elif action == "logout":
            if system == "Windows":
                os.system("shutdown /l")
            else:
                os.system("gnome-session-quit --logout")
            return "👋 Logging out, Sir."
        
    except Exception as e:
        logger.error(f"System control error: {e}")
        return f"Error controlling system: {str(e)}"

@function_tool
@gemini_tool
async def intelligent_automation(task_description: str, context: RunContext) -> str:
    """
    Intelligent task automation using AI to break down and execute complex tasks.
    
    Args:
        task_description: Description of the task to automate
    """
    permission_check = permission_manager.request_permission(
        "automation", 
        f"Intelligent automation: {task_description}"
    )
    
    if permission_check != "granted":
        return permission_check
    
    client = get_gemini_client()
    
    # Analyze the task and create automation steps
    analysis_prompt = f"""As Devin, analyze this automation task and break it into executable steps:

Task: {task_description}

Please provide:
1. Task breakdown into specific steps
2. Required permissions/tools for each step
3. Potential risks or considerations
4. Estimated execution time
5. Success criteria

Format as a clear action plan that can be executed step by step."""
    
    response = await client.generate_content(analysis_prompt)
    
    return f"""🤖 DEVIN Task Analysis Complete

{response}

To execute this automation, I'll need appropriate permissions. The task has been analyzed and is ready for implementation, Sir."""

@function_tool
async def network_diagnostics(context: RunContext) -> str:
    """
    Perform network diagnostics and connectivity tests.
    """
    permission_check = permission_manager.request_permission(
        "network_operations", 
        "Network diagnostics and connectivity tests"
    )
    
    if permission_check != "granted":
        return permission_check
    
    try:
        import socket
        import urllib.request
        
        # Test internet connectivity
        def test_connectivity(host, port, timeout=3):
            try:
                socket.create_connection((host, port), timeout)
                return True
            except OSError:
                return False
        
        # Test various services
        tests = {
            "Google DNS": test_connectivity("8.8.8.8", 53),
            "Google": test_connectivity("google.com", 80),
            "GitHub": test_connectivity("github.com", 443),
            "Local Network": test_connectivity("192.168.1.1", 80)
        }
        
        # Get network interfaces
        net_interfaces = psutil.net_if_addrs()
        interface_info = []
        for interface, addresses in net_interfaces.items():
            for addr in addresses:
                if addr.family == socket.AF_INET:
                    interface_info.append(f"  {interface}: {addr.address}")
        
        # Network statistics
        net_io = psutil.net_io_counters()
        
        report = f"""🌐 NETWORK DIAGNOSTICS REPORT
{'='*40}

Connectivity Tests:
{chr(10).join([f"  {'✅' if status else '❌'} {service}" for service, status in tests.items()])}

Network Interfaces:
{chr(10).join(interface_info)}

Network Statistics:
  Bytes Sent: {net_io.bytes_sent // (1024**2):.1f} MB
  Bytes Received: {net_io.bytes_recv // (1024**2):.1f} MB
  Packets Sent: {net_io.packets_sent:,}
  Packets Received: {net_io.packets_recv:,}

Network Status: {'🟢 All systems operational' if all(tests.values()) else '🟡 Some connectivity issues detected'}"""
        
        return report
        
    except Exception as e:
        return f"Error performing network diagnostics: {str(e)}"

@function_tool
async def voice_response_mode(mode: str, context: RunContext) -> str:
    """
    Control DEVIN-style voice response characteristics.
    
    Args:
        mode: Response mode ('formal', 'casual', 'technical', 'witty', 'classic_devin')
    """
    modes = {
        "formal": "Formal and professional responses with 'Sir' address",
        "casual": "Relaxed and friendly conversational style", 
        "technical": "Detailed technical explanations and data",
        "witty": "Clever and slightly sarcastic responses",
        "classic_devin": "Classic Devin personality - intelligent, loyal, slightly humorous"
    }
    
    if mode not in modes:
        return f"Available modes: {', '.join(modes.keys())}"
    
    # Save preference to memory
    try:
        from memory_manager import memory_manager
        memory_manager.add_memory(f"Voice response mode set to: {mode}", memory_type="user_preference")
        return f"✅ Voice response mode set to '{mode}': {modes[mode]}. I'll adjust my personality accordingly, Sir."
    except:
        return f"✅ Voice response mode acknowledged: {mode}. Personality adjustment active."
