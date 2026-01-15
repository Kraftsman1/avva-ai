from core.ipc_bridge import ipc_bridge

# The MANIFEST tells AVVA which functions are 'Tools' and how to describe them to the LLM.
MANIFEST = {
    "get_system_stats": {
        "description": "Get a full report of CPU, RAM, and Disk usage."
    },
    "get_cpu_info": {
        "description": "Check only the current CPU/processor usage percentage."
    },
    "get_ram_info": {
        "description": "Check only the current RAM/memory usage percentage."
    },
    "get_disk_info": {
        "description": "Check only the main disk storage usage percentage."
    }
}

def get_system_stats():
    res = ipc_bridge.call("get_system_stats")
    if res.get("status") == "success":
        return f"CPU: {res['cpu']}%, RAM: {res['ram']}%, Disk: {res['disk']}%"
    return f"Error: {res.get('message')}"

def get_cpu_info():
    res = ipc_bridge.call("get_cpu_info")
    return f"CPU usage is currently {res['usage']}%."

def get_ram_info():
    res = ipc_bridge.call("get_ram_info")
    return f"You are using {res['usage']}% of your memory."

def get_disk_info():
    res = ipc_bridge.call("get_disk_info")
    return f"Your disk is {res['usage']}% full."
