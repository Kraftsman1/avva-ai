import os
import datetime
from skills.system_stats import get_system_stats, get_cpu_info, get_ram_info, get_disk_info

# This registry maps tool names (that the LLM will use) to actual Python functions.
TOOL_REGISTRY = {
    "get_system_stats": get_system_stats,
    "get_cpu_info": get_cpu_info,
    "get_ram_info": get_ram_info,
    "get_disk_info": get_disk_info,
    "get_time": lambda: f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}.",
    "get_date": lambda: f"Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}."
}

def get_tools_description():
    """Returns a string describing available tools for the LLM system prompt."""
    descriptions = [
        "- get_system_stats: Use this to get a full report of CPU, RAM, and Disk usage.",
        "- get_cpu_info: Use this if the user specifically asks about the processor or CPU.",
        "- get_ram_info: Use this if the user specifically asks about memory or RAM.",
        "- get_disk_info: Use this if the user asks about storage, disk space, or hard drive.",
        "- get_time: Use this to get the current clock time.",
        "- get_date: Use this to get today's date."
    ]
    return "\n".join(descriptions)

def execute_tool(tool_name):
    """Executes a tool from the registry and returns its output."""
    if tool_name in TOOL_REGISTRY:
        try:
            return TOOL_REGISTRY[tool_name]()
        except Exception as e:
            return f"Error executing tool {tool_name}: {e}"
    return f"Tool {tool_name} not found."
