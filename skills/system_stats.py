import psutil

def get_system_stats():
    """Returns a string summary of current system resource usage."""
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    stats = (
        f"Currently, your CPU usage is at {cpu_usage} percent. "
        f"You are using {memory.percent} percent of your RAM, "
        f"and your main disk is {disk.percent} percent full."
    )
    return stats

def get_cpu_info():
    return f"CPU usage is currently {psutil.cpu_percent(interval=1)}%."

def get_ram_info():
    memory = psutil.virtual_memory()
    return f"You are using {memory.percent}% of your available memory."

def get_disk_info():
    disk = psutil.disk_usage('/')
    return f"Your disk is {disk.percent}% full."
