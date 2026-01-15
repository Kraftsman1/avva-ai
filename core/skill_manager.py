import os
import json
import importlib.util
import re

class SkillManager:
    def __init__(self, skills_dir="skills"):
        self.skills_dir = skills_dir
        self.registry = {}       # tool_name -> function
        self.tool_metadata = {}  # tool_name -> description
    def __init__(self, skills_dir="skills"):
        self.skills_dir = skills_dir
        self.registry = {}       # tool_name -> function
        self.tool_metadata = {}  # tool_name -> description
        self.tool_permissions = {} # tool_name -> list of permissions
        self.static_intents = {} # phrase -> execution_string
        self.regex_intents = []  # list of (compiled_regex, execution_template)
        
        # Whitelist of allowed permissions for the session
        # In the future, this will be populated from a user config or GTK prompt
        self.allowed_permissions = ["sys_info_read", "system_control"]
        
        self.load_all_skills()

    def load_all_skills(self):
        """Scans for folder-based plugins and registers them."""
        if not os.path.exists(self.skills_dir):
            os.makedirs(self.skills_dir)
            
        print(f"System: Discovering plugins in '{self.skills_dir}'...")
        
        for folder in os.listdir(self.skills_dir):
            folder_path = os.path.join(self.skills_dir, folder)
            manifest_path = os.path.join(folder_path, "manifest.json")
            
            if os.path.isdir(folder_path) and os.path.exists(manifest_path):
                self._load_plugin(folder, folder_path, manifest_path)

    def _load_plugin(self, folder_name, folder_path, manifest_path):
        """Standardized plugin loader supporting direct and parametric intents."""
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            entry_point = manifest.get("entry_point", "main.py")
            entry_path = os.path.join(folder_path, entry_point)
            
            # Use importlib to load the module
            spec = importlib.util.spec_from_file_location(folder_name, entry_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Extract permissions from manifest
            plugin_permissions = manifest.get("permissions", [])
            
            # 1. Register tools from the module MANIFEST
            if hasattr(module, 'MANIFEST'):
                module_manifest = getattr(module, 'MANIFEST')
                for tool_id, info in module_manifest.items():
                    if hasattr(module, tool_id):
                        self.registry[tool_id] = getattr(module, tool_id)
                        self.tool_metadata[tool_id] = info.get("description", "")
                        self.tool_permissions[tool_id] = plugin_permissions
                        print(f"  - Registered Tool: {tool_id} (Perms: {plugin_permissions})")

            # 2. Register Intents (Direct + Parametric)
            intents = manifest.get("intents", {})
            if isinstance(intents, dict):
                for pattern, exec_template in intents.items():
                    self._register_intent(pattern, exec_template, folder_name)
            elif isinstance(intents, list):
                # Legacy list support: map all phrases to the first tool in MANIFEST
                if hasattr(module, 'MANIFEST'):
                    first_tool = list(getattr(module, 'MANIFEST').keys())[0]
                    for phrase in intents:
                        self.static_intents[phrase.lower()] = f"{first_tool}()"

            print(f"✨ Loaded Plugin: {manifest.get('name', folder_name)}")
            
        except Exception as e:
            print(f"❌ Error loading plugin '{folder_name}': {e}")

    def _register_intent(self, pattern, exec_template, folder_name):
        """Helper to register a single intent pattern."""
        pattern = pattern.lower()
        if pattern.startswith("regex:"):
            regex_pattern = pattern[6:].strip()
            try:
                compiled = re.compile(regex_pattern, re.IGNORECASE)
                self.regex_intents.append((compiled, exec_template))
                print(f"  - Registered Parametric Intent: {regex_pattern}")
            except re.error as e:
                print(f"  ❌ Invalid regex in {folder_name}: {e}")
        else:
            self.static_intents[pattern] = exec_template

    def get_intent_match(self, command):
        """
        Check for any local matches (Tier 1 & Tier 2).
        Returns the resolved execution string or None.
        """
        cmd_clean = command.lower().strip()
        
        # 1. Check Static Intents (Priority 1)
        if cmd_clean in self.static_intents:
            return self.static_intents[cmd_clean]
            
        for phrase, exec_str in self.static_intents.items():
            if phrase in cmd_clean:
                return exec_str

        # 2. Check Regex Intents (Priority 2)
        for regex, template in self.regex_intents:
            match = regex.search(cmd_clean)
            if match:
                # Replace $1, $2, etc with capture groups
                resolved_exec = template
                for i, group in enumerate(match.groups(), 1):
                    resolved_exec = resolved_exec.replace(f"${i}", group)
                return resolved_exec

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
                tool_name = exec_str
                args_str = ""
            else:
                tool_name = match.group(1)
                args_str = match.group(2)

            if tool_name not in self.registry:
                return f"Tool '{tool_name}' not found."

            # --- PERMISSION CHECK ---
            required_perms = self.tool_permissions.get(tool_name, [])
            for perm in required_perms:
                if perm not in self.allowed_permissions:
                    print(f"🔒 Skill '{tool_name}' requesting permission '{perm}'...")
                    if self._request_permission(tool_name, perm):
                        self.allowed_permissions.append(perm)
                        print(f"✅ Permission '{perm}' granted by user.")
                    else:
                        return f"❌ Permission Denied: Skill '{tool_name}' requires '{perm}' which was rejected."

            # --- EXECUTION ---
            if not args_str:
                result = self.registry[tool_name]()
            else:
                args = [a.strip().strip('"').strip("'") for a in args_str.split(",")]
                result = self.registry[tool_name](*args)
            
            # Handle structured dict results (Phase 2 Standard)
            if isinstance(result, dict):
                result["text"] = self._format_structured_result(result)
                return result
            return result
            
        except Exception as e:
            return f"Execution error for '{exec_str}': {e}"

    def _request_permission(self, skill_name, permission):
        """Spawns the GTK Permission Overlay and waits for user response."""
        try:
            import subprocess
            import sys
            
            # Use the current python executable to run the UI script
            ui_script = os.path.join(os.path.dirname(__file__), "permission_prompt.py")
            
            # Run the process and wait for result
            # Code 0 = Allow, 1 = Deny
            proc = subprocess.run(
                [sys.executable, ui_script, skill_name, permission],
                capture_output=False
            )
            
            return proc.returncode == 0
        except Exception as e:
            print(f"⚠️ UI Error: Could not spawn permission prompt: {e}")
            return False

    def _format_structured_result(self, res):
        """Converts a dict result from a skill into a conversational string."""
        status = res.get("status", "error")
        
        if status == "launched":
            return f"Success! Launching {res.get('app')} for you."
        elif status == "ambiguous":
            options = ", ".join(res.get("options", []))
            return f"I found a few matches: {options}. Which one did you mean?"
        elif res.get("type") == "system_stats":
            return f"CPU is at {res['cpu']}%, RAM at {res['ram']}%, and Disk at {res['disk']}%."
        elif status == "not_found":
            return f"I'm sorry, I couldn't find an application related to '{res.get('query')}'."
        elif status == "error":
            return f"I ran into a problem: {res.get('message', 'Unknown error')}"
        
        return str(res)

skill_manager = SkillManager()
