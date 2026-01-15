from core.skill_manager import SkillManager
import os

# Create a custom SkillManager instance for testing
print("--- AVVA Permission Guard Verification ---")
test_manager = SkillManager()

# 1. Test standard execution (Authorized)
print("\n[Test 1] Executing 'get_time()' (Requires 'system.read', currently whitelisted)")
res1 = test_manager.execute("get_time()")
print(f"Result: {res1}")

# 2. Test permission denial
print("\n[Test 2] Removing 'system.read' from whitelist and retrying...")
test_manager.allowed_permissions = ["apps.launch"] # Remove system.read
res2 = test_manager.execute("get_time()")
print(f"Result: {res2}")

# 3. Test App Launcher (Authorized)
print("\n[Test 3] Executing 'launch_application(\"terminal\")' (Requires 'apps.launch', whitelisted)")
res3 = test_manager.execute("launch_application(\"terminal_test\")") # terminal_test to avoid actual launch
print(f"Result: {res3}")

# 4. Completely unauthorized
print("\n[Test 4] Removing all permissions and retrying App Launcher...")
test_manager.allowed_permissions = []
res4 = test_manager.execute("launch_application(\"terminal_test\")")
print(f"Result: {res4}")
