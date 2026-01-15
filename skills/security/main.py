# MIT License - Copyright (c) 2026 Asigri Shamsu-Deen Al-Heyr
from core.persistence import storage

MANIFEST = {
    "get_active_permissions": {
        "description": "List all currently granted permissions and active security policies."
    }
}

def get_active_permissions():
    """Retrieves allowed permissions from the database for visual rendering."""
    perms = storage.get_allowed_permissions()
    
    # Format for UI
    result = {
        "status": "success",
        "type": "permissions",
        "count": len(perms),
        "permissions": []
    }
    
    for perm in perms:
        result["permissions"].append({
            "permission": perm
        })
        
    return result
