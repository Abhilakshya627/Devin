"""
DEVIN-like system interaction capabilities for Standalone Devin AI Assistant.
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
from standalone_framework import function_tool, RunContext, gemini_tool
from gemini_client import get_gemini_client

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
                # Default permissions - all disabled for security
                self.permissions = {
                    "system_control": False,
                    "file_operations": False,
                    "app_control": False,
                    "network_operations": False,
                    "screen_interaction": False,
                    "voice_interaction": False,
                    "automation": False
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
    
    def has_permission(self, permission: str) -> bool:
        """Check if a permission is granted."""
        return self.permissions.get(permission, False)
    
    def grant_permission(self, permission: str) -> bool:
        """Grant a specific permission."""
        if permission == "all":
            for perm in self.permissions:
                self.permissions[perm] = True
        else:
            if permission in self.permissions:
                self.permissions[permission] = True
            else:
                return False
        
        self.save_permissions()
        return True
    
    def revoke_permission(self, permission: str) -> bool:
        """Revoke a specific permission."""
        if permission == "all":
            for perm in self.permissions:
                self.permissions[perm] = False
        else:
            if permission in self.permissions:
                self.permissions[permission] = False
            else:
                return False
        
        self.save_permissions()
        return True

# Global permission manager
permission_manager = PermissionManager()

@function_tool
async def grant_permission(permission: str, context: RunContext) -> str:
    """
    Grant system permissions for DEVIN operations.
    
    Args:
        permission: Permission to grant ('all', 'system_control', 'file_operations', etc.)
    """
    try:
        if permission_manager.grant_permission(permission):
            logger.info(f"Permission granted: {permission}")
            return f"✅ Permission granted: {permission}"
        else:
            return f"❌ Unknown permission: {permission}"
    except Exception as e:
        logger.error(f"Error granting permission: {e}")
        return f"Error granting permission: {str(e)}"

@function_tool
async def revoke_permission(permission: str, context: RunContext) -> str:
    """
    Revoke system permissions for DEVIN operations.
    
    Args:
        permission: Permission to revoke ('all', 'system_control', 'file_operations', etc.)
    """
    try:
        if permission_manager.revoke_permission(permission):
            logger.info(f"Permission revoked: {permission}")
            return f"❌ Permission revoked: {permission}"
        else:
            return f"❌ Unknown permission: {permission}"
    except Exception as e:
        logger.error(f"Error revoking permission: {e}")
        return f"Error revoking permission: {str(e)}"

@function_tool
async def system_status_report(context: RunContext) -> str:
    """
    Generate a comprehensive DEVIN system status report.
    """
    try:
        report = []
        report.append("🤖 DEVIN SYSTEM STATUS REPORT")
        report.append("=" * 50)
        report.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # System Information
        report.append("💻 SYSTEM INFORMATION:")
        report.append(f"OS: {platform.system()} {platform.release()}")
        report.append(f"Machine: {platform.machine()}")
        report.append(f"Processor: {platform.processor()}")
        report.append(f"Python: {platform.python_version()}")
        
        # Resource Usage
        report.append("\n📊 RESOURCE USAGE:")
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        report.append(f"CPU Usage: {cpu_percent}%")
        report.append(f"Memory Usage: {memory.percent}% ({memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB)")
        report.append(f"Disk Usage: {disk.percent}% ({disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB)")
        
        # Network Information
        report.append("\n🌐 NETWORK STATUS:")
        try:
            import socket
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            report.append(f"Hostname: {hostname}")
            report.append(f"Local IP: {local_ip}")
        except:
            report.append("Network information unavailable")
        
        # Permission Status
        report.append("\n🔐 PERMISSION STATUS:")
        for perm, status in permission_manager.permissions.items():
            status_icon = "✅" if status else "❌"
            report.append(f"{status_icon} {perm.replace('_', ' ').title()}: {'Enabled' if status else 'Disabled'}")
        
        # Running Processes (top 5 by CPU)
        report.append("\n⚡ TOP PROCESSES (by CPU):")
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    proc_info = proc.info
                    if proc_info['cpu_percent'] > 0:
                        processes.append(proc_info)
                except:
                    continue
            
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            for proc in processes[:5]:
                report.append(f"• {proc['name']} (PID: {proc['pid']}) - CPU: {proc['cpu_percent']}%")
        except:
            report.append("Process information unavailable")
        
        report.append("")
        report.append("🎯 DEVIN System Status: OPERATIONAL")
        report.append("Ready to assist, Sir.")
        
        return "\n".join(report)
        
    except Exception as e:
        logger.error(f"System status error: {e}")
        return f"System status error: {str(e)}"

@function_tool
async def control_applications(action: str, app_name: str, context: RunContext) -> str:
    """
    Control applications on the system.
    
    Args:
        action: Action to perform ('start', 'stop', 'restart', 'list')
        app_name: Name of the application (if applicable)
    """
    if not permission_manager.has_permission("app_control"):
        return "❌ Application control permission required. Use grant_permission('app_control') first."
    
    try:
        if action == "list":
            # List running applications
            processes = []
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    processes.append(f"• {proc.info['name']} (PID: {proc.info['pid']})")
                except:
                    continue
            
            return f"Running applications:\n" + "\n".join(processes[:20])  # Limit to 20
        
        elif action == "start":
            if platform.system() == "Windows":
                subprocess.Popen(app_name, shell=True)
            else:
                subprocess.Popen(app_name, shell=True)
            return f"✅ Started application: {app_name}"
        
        elif action == "stop":
            # Find and terminate process by name
            killed = False
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if app_name.lower() in proc.info['name'].lower():
                        proc.terminate()
                        killed = True
                        break
                except:
                    continue
            
            if killed:
                return f"✅ Stopped application: {app_name}"
            else:
                return f"❌ Application not found: {app_name}"
        
        else:
            return f"❌ Unknown action: {action}. Use: start, stop, list"
            
    except Exception as e:
        logger.error(f"App control error: {e}")
        return f"Error controlling application: {str(e)}"

@function_tool
async def file_operations(operation: str, path: str, content: str = "", context: RunContext = None) -> str:
    """
    Perform file system operations.
    
    Args:
        operation: Operation to perform ('read', 'write', 'delete', 'list', 'create_dir')
        path: File or directory path
        content: Content for write operations
    """
    if not permission_manager.has_permission("file_operations"):
        return "❌ File operations permission required. Use grant_permission('file_operations') first."
    
    try:
        path_obj = Path(path)
        
        if operation == "read":
            if path_obj.exists() and path_obj.is_file():
                with open(path_obj, 'r', encoding='utf-8') as f:
                    content = f.read()
                return f"File content of {path}:\n{content[:1000]}{'...' if len(content) > 1000 else ''}"
            else:
                return f"❌ File not found: {path}"
        
        elif operation == "write":
            with open(path_obj, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"✅ File written: {path}"
        
        elif operation == "delete":
            if path_obj.exists():
                if path_obj.is_file():
                    path_obj.unlink()
                    return f"✅ File deleted: {path}"
                else:
                    return f"❌ Path is not a file: {path}"
            else:
                return f"❌ File not found: {path}"
        
        elif operation == "list":
            if path_obj.exists() and path_obj.is_dir():
                items = list(path_obj.iterdir())
                file_list = []
                for item in items[:20]:  # Limit to 20 items
                    type_icon = "📁" if item.is_dir() else "📄"
                    file_list.append(f"{type_icon} {item.name}")
                return f"Contents of {path}:\n" + "\n".join(file_list)
            else:
                return f"❌ Directory not found: {path}"
        
        elif operation == "create_dir":
            path_obj.mkdir(parents=True, exist_ok=True)
            return f"✅ Directory created: {path}"
        
        else:
            return f"❌ Unknown operation: {operation}. Use: read, write, delete, list, create_dir"
            
    except Exception as e:
        logger.error(f"File operation error: {e}")
        return f"Error with file operation: {str(e)}"

@function_tool
async def system_control(action: str, target: str = "", context: RunContext = None) -> str:
    """
    Control system functions.
    
    Args:
        action: Action to perform ('shutdown', 'restart', 'sleep', 'volume', 'time')
        target: Target value for certain actions (e.g., volume level)
    """
    if not permission_manager.has_permission("system_control"):
        return "❌ System control permission required. Use grant_permission('system_control') first."
    
    try:
        if action == "time":
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            return f"Current system time: {current_time}"
        
        elif action == "volume":
            if platform.system() == "Windows":
                try:
                    import pycaw.pycaw as pycaw
                    from ctypes import cast, POINTER
                    from comtypes import CLSCTX_ALL
                    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                    
                    devices = AudioUtilities.GetSpeakers()
                    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                    volume = cast(interface, POINTER(IAudioEndpointVolume))
                    
                    if target:
                        volume_level = float(target) / 100.0
                        volume.SetMasterScalarVolume(volume_level, None)
                        return f"✅ Volume set to {target}%"
                    else:
                        current_volume = volume.GetMasterScalarVolume()
                        return f"Current volume: {int(current_volume * 100)}%"
                except ImportError:
                    return "❌ Volume control requires pycaw library"
            else:
                return "❌ Volume control not supported on this platform"
        
        elif action in ["shutdown", "restart", "sleep"]:
            return f"❌ {action.title()} command disabled for safety. Please use system controls manually."
        
        else:
            return f"❌ Unknown action: {action}. Use: time, volume"
            
    except Exception as e:
        logger.error(f"System control error: {e}")
        return f"Error with system control: {str(e)}"

@function_tool
@gemini_tool
async def intelligent_automation(task_description: str, context: RunContext) -> str:
    """
    Use AI to analyze and suggest automation for complex tasks.
    
    Args:
        task_description: Description of the task to automate
    """
    if not permission_manager.has_permission("automation"):
        return "❌ Automation permission required. Use grant_permission('automation') first."
    
    try:
        client = get_gemini_client()
        
        prompt = f"""As Devin, analyze this automation task and provide a step-by-step plan:

Task: {task_description}

Available capabilities:
- File operations (read, write, delete, list directories)
- Application control (start, stop, list processes)
- System control (time, volume)
- Screen interaction (screenshots, mouse clicks, keyboard input)
- Voice interaction (speak text, listen for commands)

Provide:
1. Task analysis
2. Step-by-step automation plan
3. Required permissions
4. Safety considerations
5. Alternative approaches

Be practical and prioritize user safety."""
        
        response = await client.generate_content(prompt)
        
        return f"🤖 DEVIN Automation Analysis:\n\n{response}"
        
    except Exception as e:
        logger.error(f"Automation analysis error: {e}")
        return f"Automation analysis error: {str(e)}"

@function_tool
async def network_diagnostics(target: str = "", context: RunContext = None) -> str:
    """
    Perform network diagnostics and connectivity tests.
    
    Args:
        target: Target to test (IP address or domain name)
    """
    if not permission_manager.has_permission("network_operations"):
        return "❌ Network operations permission required. Use grant_permission('network_operations') first."
    
    try:
        import socket
        import subprocess
        
        results = []
        results.append("🌐 NETWORK DIAGNOSTICS")
        results.append("=" * 30)
        
        # Basic connectivity
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            results.append("✅ Internet connectivity: Online")
        except:
            results.append("❌ Internet connectivity: Offline")
        
        # Local network info
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        results.append(f"🏠 Hostname: {hostname}")
        results.append(f"🏠 Local IP: {local_ip}")
        
        # DNS test
        try:
            socket.gethostbyname("google.com")
            results.append("✅ DNS resolution: Working")
        except:
            results.append("❌ DNS resolution: Failed")
        
        # Ping test if target provided
        if target:
            try:
                if platform.system() == "Windows":
                    result = subprocess.run(['ping', '-n', '4', target], 
                                          capture_output=True, text=True, timeout=10)
                else:
                    result = subprocess.run(['ping', '-c', '4', target], 
                                          capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    results.append(f"✅ Ping to {target}: Success")
                else:
                    results.append(f"❌ Ping to {target}: Failed")
            except:
                results.append(f"❌ Ping to {target}: Error")
        
        return "\n".join(results)
        
    except Exception as e:
        logger.error(f"Network diagnostics error: {e}")
        return f"Network diagnostics error: {str(e)}"

@function_tool
async def voice_response_mode(mode: str, context: RunContext) -> str:
    """
    Configure voice response behavior for DEVIN.
    
    Args:
        mode: Response mode ('on', 'off', 'smart', 'status')
    """
    try:
        # This would integrate with voice_interaction.py
        # For now, just return status
        return f"🗣️ Voice response mode set to: {mode}\nNote: Voice integration requires voice_interaction module"
        
    except Exception as e:
        logger.error(f"Voice response error: {e}")
        return f"Voice response error: {str(e)}"
