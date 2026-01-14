import os
import json
import importlib.util

class SkillManager:
    def __init__(self, skills_dir="skills"):
        self.skills_dir = skills_dir
        self.registry = {}       # intent -> function_mapping
        self.tool_metadata = {}  # tool_name -> description (for LLM)
        self.direct_matches = {} # trigger_phrase -> tool_name (Tier 1 Intent)
        self.load_all_skills()

    def load_all_skills(self):
        """Scans for folder-based plugins with manifest.json."""
        if not os.path.exists(self.skills_dir):
            os.makedirs(self.skills_dir)
            
        print(f"System: Discoverying plugins in '{self.skills_dir}'...")
        
        for folder in os.listdir(self.skills_dir):
            folder_path = os.path.join(self.skills_dir, folder)
            manifest_path = os.path.join(folder_path, "manifest.json")
            
            if os.path.isdir(folder_path) and os.path.exists(manifest_path):
                self._load_plugin(folder, folder_path, manifest_path)

    def _load_plugin(self, folder_name, folder_path, manifest_path):
        """Loads a plugin based on its manifest."""
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            entry_point = manifest.get("entry_point", "main.py")
            entry_path = os.path.join(folder_path, entry_point)
            
            # Dynamic import
            spec = importlib.util.spec_from_file_location(folder_name, entry_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Register internal skills from the module's MANIFEST
            if hasattr(module, 'MANIFEST'):
                module_manifest = getattr(module, 'MANIFEST')
                for tool_id, info in module_manifest.items():
                    self.registry[tool_id] = getattr(module, tool_id)
                    self.tool_metadata[tool_id] = info.get("description", "")
                    print(f"  - Registered Tool: {tool_id}")
            
            # Register Tier 1 Direct Match Intents
            intents = manifest.get("intents", [])
            for phrase in intents:
                # Map the first skill in the manifest to these direct phrases 
                # (Simple mapping for now, can be refined)
                if hasattr(module, 'MANIFEST'):
                    first_tool = list(module_manifest.keys())[0]
                    self.direct_matches[phrase.lower()] = first_tool
                    
            print(f"✨ Loaded Plugin: {manifest.get('name', folder_name)}")
            
        except Exception as e:
            print(f"❌ Error loading plugin '{folder_name}': {e}")

    def get_direct_match(self, command):
        """Tier 1 Intent: Check for exact/keyword matches to bypass LLM."""
        cmd_clean = command.lower().strip()
        for phrase, tool_name in self.direct_matches.items():
            if phrase in cmd_clean:
                return tool_name
        return None

    def get_tool_descriptions(self):
        """Tier 3 Intent: Describe tools for the LLM."""
        return "\n".join([f"- {name}: {desc}" for name, desc in self.tool_metadata.items()])

    def execute(self, tool_name):
        """Executes a registered tool."""
        if tool_name in self.registry:
            return self.registry[tool_name]()
        return f"Tool '{tool_name}' not found."

skill_manager = SkillManager()
