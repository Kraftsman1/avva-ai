from core.skill_manager import skill_manager

print("--- AVVA UI Manual Test ---")
print("This will trigger a real GTK Permission Overlay if you are on a Linux desktop.")
print("Command: 'what time is it'")
print("-" * 30)

# Empty whitelist to force the UI overlay
skill_manager.allowed_permissions = []

# This will now trigger a GTK window
result = skill_manager.execute("get_time()")

print("-" * 30)
print(f"SkillManager Result: {result}")
print(f"Current Whitelist: {skill_manager.allowed_permissions}")
