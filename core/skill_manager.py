import os
import json
import importlib.util
import re

class SkillManager:
    def __init__(self, skills_dir="skills"):
        self.skills_dir = skills_dir
        self.registry = {}       # tool_name -> function
        self.tool_metadata = {}  # tool_name -> description
        self.direct_matches = {} # phrase -> execution_string (e.g. "open_firefox()")
        self.load_all_skills()

    def load_all_skills(self):
        """Scans for folder-based plugins and registers them."""
        if not os.path.exists(self.skills_dir):
            os.makedirs(self.skills_dir)
            
        print(f"System: Discoverying plugins in '{self.skills_dir}'...")
        
        for folder in os.listdir(self.skills_dir):
            folder_path = os.path.join(self.skills_dir, folder)
            manifest_path = os.path.join(folder_path, "manifest.json")
            
            if os.path.isdir(folder_path) and os.path.exists(manifest_path):
                self._load_plugin(folder, folder_path, manifest_path)

    def _load_plugin(self, folder_name, folder_path, manifest_path):
        """Standardized plugin loader based on AVA platform spec."""
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            entry_point = manifest.get("entry_point", "main.py")
            entry_path = os.path.join(folder_path, entry_point)
            
            spec = importlib.util.spec_from_file_location(folder_name, entry_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 1. Register tools from the module MANIFEST
            if hasattr(module, 'MANIFEST'):
                module_manifest = getattr(module, 'MANIFEST')
                for tool_id, info in module_manifest.items():
                    if hasattr(module, tool_id):
                        self.registry[tool_id] = getattr(module, tool_id)
                        self.tool_metadata[tool_id] = info.get("description", "")
                        print(f"  - Registered Tool: {tool_id}")

            # 2. Register Tier 1 Direct Match Intents
            intents = manifest.get("intents", {})
            if isinstance(intents, dict):
                for phrase, exec_str in intents.items():
                    self.direct_matches[phrase.lower()] = exec_str
            elif isinstance(intents, list):
                # Fallback for old style list
                for phrase in intents:
                    if hasattr(module, 'MANIFEST'):
                        first_tool = list(module_manifest.keys())[0]
                        self.direct_matches[phrase.lower()] = f"{first_tool}()"
                    
            print(f"✨ Loaded Plugin: {manifest.get('name', folder_name)}")
            
        except Exception as e:
            print(f"❌ Error loading plugin '{folder_name}': {e}")

    def get_direct_match(self, command):
        """Check for exact keyword matches (Tier 1 Intent)."""
        cmd_clean = command.lower().strip()
        for phrase, exec_str in self.direct_matches.items():
            if phrase in cmd_clean:
                return exec_str
        return None

    def get_tool_descriptions(self):
        """Prepare tool info for LLM (Tier 3 Intent)."""
        return "\n".join([f"- {name}: {desc}" for name, desc in self.tool_metadata.items()])

    def execute(self, exec_str):
        """
        Executes a tool string. 
        Supports formats: 'tool_name()' or 'tool_name("arg")'
        """
        try:
            # Parse tool name and arguments
            match = re.match(r"(\w+)\((.*)\)", exec_str)
            if not match:
                # If it's just a tool name without parens, try to execute it
                tool_name = exec_str
                args_str = ""
            else:
                tool_name = match.group(1)
                args_str = match.group(2)

            if tool_name in self.registry:
                # Basic argument parsing (can be improved)
                if not args_str:
                    return self.registry[tool_name]()
                else:
                    # Strip quotes and split basic args
                    args = [a.strip().strip('"').strip("'") for a in args_str.split(",")]
                    return self.registry[tool_name](*args)
            
            return f"Tool '{tool_name}' not found."
        except Exception as e:
            return f"Execution error for '{exec_str}': {e}"

skill_manager = SkillManager()
