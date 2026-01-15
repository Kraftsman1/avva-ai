# MIT License - Copyright (c) 2026 Asigri Shamsu-Deen Al-Heyr
from core.persistence import storage
import sqlite3
import os

def test_persistence():
    print("🧪 Verifying System Memory...")
    
    # 1. Test Interaction Logging
    print("   - Logging test interaction...")
    storage.log_interaction("user", "Hello AVVA", None)
    storage.log_interaction("avva", "Hello User", "greet()")
    
    # 2. Test Permission Saving
    print("   - Saving test permission...")
    storage.save_permission("test_skill", "test_permission")
    
    # 3. Verify Database Contents
    print("   - Checking SQLite database...")
    conn = sqlite3.connect(storage.db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM history ORDER BY id DESC LIMIT 2")
    history = cursor.fetchall()
    print(f"     [History] Found {len(history)} recent entries.")
    for h in history:
        print(f"       {h[2]}: {h[3]} (Tool: {h[4]})")
        
    cursor.execute("SELECT * FROM permissions WHERE skill_name='test_skill'")
    perm = cursor.fetchone()
    if perm:
        print(f"     [Permissions] Successfully found 'test_skill' -> '{perm[2]}'")
    else:
        print("     [Permissions] FAILED to find test permission.")
        
    conn.close()
    print("\n✅ System Memory verification complete!")

if __name__ == "__main__":
    test_persistence()
