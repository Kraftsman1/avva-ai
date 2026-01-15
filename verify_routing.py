from core.skill_manager import skill_manager

test_commands = [
    "terminal",
    "open firefox",
    "launch steam",
    "what time is it",
    "cpu usage"
]

print("--- AVVA Dynamic Router Verification ---")
for cmd in test_commands:
    exec_str = skill_manager.get_intent_match(cmd)
    if exec_str:
        print(f"User: '{cmd}' -> Matched: {exec_str}")
        result = skill_manager.execute(exec_str)
        print(f"AVVA: {result}")
    else:
        print(f"User: '{cmd}' -> No Local Match found.")
    print("-" * 30)
