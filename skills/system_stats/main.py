import psutil

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
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    return (f"CPU: {cpu_usage}%, RAM: {memory.percent}%, Disk: {disk.percent}%")

def get_cpu_info():
    return f"CPU usage is currently {psutil.cpu_percent(interval=1)}%."

def get_ram_info():
    return f"You are using {psutil.virtual_memory().percent}% of your memory."

def get_disk_info():
    return f"Your disk is {psutil.disk_usage('/').percent}% full."
