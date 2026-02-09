"""
Memory Skill - Recall and search through past conversations.

Provides tools for:
- Recalling past conversations by query
- Listing recent conversations
- Clearing memory/history
"""

from core.memory import memory


def recall(query: str = ""):
    """
    Search through past conversations.

    Args:
        query: Search query to find relevant conversations

    Returns:
        Formatted string with matching conversation summaries
    """
    if not query:
        return "Please specify what you'd like me to recall. For example: 'recall my questions about Python'"

    results = memory.recall(query, max_results=5)

    if not results:
        return f"I don't have any conversations matching '{query}' in my memory."

    response = f"Found {len(results)} conversation(s) matching '{query}':\n\n"

    for i, result in enumerate(results, 1):
        response += f"{i}. {result['title']} ({result['date']})\n"

        if result.get('messages'):
            preview = result['messages'][0] if len(result['messages']) > 0 else ""
            if preview:
                response += f"   Last message: {preview[:100]}...\n"
        response += "\n"

    return response


def list_conversations(limit: int = 10):
    """
    List recent conversations.

    Args:
        limit: Maximum number of conversations to show

    Returns:
        Formatted string with conversation list
    """
    sessions = memory.list_recent_sessions(limit=limit)

    if not sessions:
        return "No conversations in history yet."

    response = f"Your recent conversations ({len(sessions)}):\n\n"

    for i, session in enumerate(sessions, 1):
        date = session['updated_at'].strftime('%Y-%m-%d %H:%M') if hasattr(session['updated_at'], 'strftime') else str(session['updated_at'])
        response += f"{i}. {session['title']} - {date}\n"

    return response


def clear_memory(days: int = 0):
    """
    Clear conversation memory.

    Args:
        days: Clear conversations older than this many days (0 = all)

    Returns:
        Confirmation message
    """
    if days > 0:
        memory.clear_old_sessions(days=days)
        return f"Cleared conversations older than {days} days."
    else:
        sessions = memory.list_recent_sessions(limit=1000)
        count = len(sessions)
        for session in sessions:
            memory.delete_session(session['id'])
        return f"Cleared all {count} conversations from memory."


def get_memory_stats():
    """
    Get memory statistics.

    Returns:
        Formatted stats string
    """
    stats = memory.get_stats()
    return f"Memory Stats:\n- Total sessions: {stats['total_sessions']}\n- Current session: {stats['current_session']}"
