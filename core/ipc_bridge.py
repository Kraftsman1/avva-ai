import subprocess
import shlex
import psutil
import os

class IPCBridge:
    """
    Centralized dispatcher for privileged OS actions.
    In Phase 3, this will communicate with a Rust daemon over a Unix Socket.
    """
    
    @staticmethod
    def call(action, **kwargs):
        """Dispatches an action to the system."""
        if action == "launch_app":
            return IPCBridge._launch_app(
                kwargs.get("exec_cmd"), 
                kwargs.get("name"),
                kwargs.get("terminal", False)
            )
        elif action == "get_system_stats":
            return IPCBridge._get_system_stats()
        elif action == "get_cpu_info":
            return IPCBridge._get_cpu_info()
        elif action == "get_ram_info":
            return IPCBridge._get_ram_info()
        elif action == "get_disk_info":
            return IPCBridge._get_disk_info()
        
        return {"status": "error", "message": f"Unknown IPC action: {action}"}

    @staticmethod
    def _clean_exec(exec_cmd):
        """Strips Freedesktop field codes."""
        field_codes = ["%U", "%u", "%F", "%f", "%i", "%c", "%k", "%n", "%m", "%v"]
        for code in field_codes:
            exec_cmd = exec_cmd.replace(code, "")
        return exec_cmd.strip()

    @staticmethod
    def _find_terminal():
        """Finds an installed terminal emulator."""
        candidates = ["com.system76.CosmicTerm", "gnome-terminal", "kgx", "konsole", "alacritty", "kitty", "xterm"]
        import shutil
        for term in candidates:
            if shutil.which(term):
                return term
        return "xterm"

    @staticmethod
    def _launch_app(exec_cmd, name, terminal=False):
        """Internal helper to launch application."""
        if not exec_cmd:
            return {"status": "error", "message": "No execution command provided."}
            
        try:
            clean_cmd = IPCBridge._clean_exec(exec_cmd)
            
            if terminal:
                term = IPCBridge._find_terminal()
                subprocess.Popen([term, "-e"] + shlex.split(clean_cmd), 
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                 start_new_session=True)
            else:
                subprocess.Popen(shlex.split(clean_cmd), 
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                 start_new_session=True)
                
            return {"status": "launched", "app": name}
        except Exception as e:
            return {"status": "error", "message": f"Launch failed: {str(e)}"}

    @staticmethod
    def _get_system_stats():
        """Aggregates system stats."""
        try:
            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            return {
                "status": "success",
                "cpu": cpu,
                "ram": ram,
                "disk": disk
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def _get_cpu_info():
        """Returns detailed CPU info."""
        return {"status": "success", "usage": psutil.cpu_percent(interval=1)}

    @staticmethod
    def _get_ram_info():
        """Returns detailed RAM info."""
        return {"status": "success", "usage": psutil.virtual_memory().percent}

    @staticmethod
    def _get_disk_info():
        """Returns detailed Disk info."""
        return {"status": "success", "usage": psutil.disk_usage('/').percent}

ipc_bridge = IPCBridge()
