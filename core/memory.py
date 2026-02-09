"""
Memory System - Conversation memory and semantic recall for AVA.

Provides:
- Conversation session management
- Semantic search across history
- Context building for Brain queries
"""

import uuid
from core.persistence import storage
from core.config import config


class Memory:
    """Memory system for conversation persistence and recall."""

    def __init__(self):
        self.current_session_id = None
        self.session_title = None

    def start_session(self, title=None, brain_id=None):
        """Start a new conversation session."""
        self.current_session_id = storage.create_session(
            session_id=str(uuid.uuid4()),
            title=title,
            brain_id=brain_id
        )
        self.session_title = title or "New Conversation"
        return self.current_session_id

    def get_current_session(self):
        """Get the current session ID, creating one if needed."""
        if not self.current_session_id:
            self.start_session()
        return self.current_session_id

    def add_message(self, role, content, brain_id=None, intent=None, tool_call=None):
        """Add a message to the current session."""
        session_id = self.get_current_session()
        storage.add_message(
            session_id=session_id,
            role=role,
            content=content,
            brain_id=brain_id,
            intent=intent,
            tool_call=tool_call
        )

    def add_user_message(self, content):
        """Add a user message to memory."""
        self.add_message(role="user", content=content)
        # Auto-generate title from first user message if still "New Conversation"
        if self.session_title == "New Conversation" and content:
            self._update_session_title(content)

    def add_assistant_message(self, content, brain_id=None, intent=None, tool_call=None):
        """Add an assistant message to memory."""
        self.add_message(
            role="assistant",
            content=content,
            brain_id=brain_id,
            intent=intent,
            tool_call=tool_call
        )

    def get_recent_context(self, max_messages=10, include_sessions=3):
        """
        Build context string from recent conversation history.

        Args:
            max_messages: Maximum messages to include from current session
            include_sessions: Number of recent sessions to include

        Returns:
            Formatted context string for Brain queries
        """
        context_parts = []

        current_session = self.get_current_session()
        messages = storage.get_session_messages(current_session, limit=max_messages)

        if messages:
            context_parts.append("Recent conversation:")
            for msg in messages:
                role_emoji = "👤" if msg['role'] == "user" else "🤖"
                context_parts.append(f"{role_emoji} {msg['content'][:500]}")

        recent_sessions = storage.list_sessions(limit=include_sessions + 1, offset=1)
        for session in recent_sessions:
            if session['id'] != current_session:
                context_parts.append(f"\nEarlier session ({session['updated_at'].strftime('%Y-%m-%d %H:%M')}): {session['title']}")

        return "\n".join(context_parts)

    def recall(self, query, max_results=5):
        """
        Search for past conversations matching a query.

        Args:
            query: Search query string
            max_results: Maximum results to return

        Returns:
            List of matching conversation summaries
        """
        results = storage.search_conversations(query, limit=max_results)

        recalls = []
        for result in results:
            messages = storage.get_session_messages(result['session_id'], limit=5)
            summary = {
                'session_id': result['session_id'],
                'title': result['title'],
                'date': result['updated_at'].strftime('%Y-%m-%d %H:%M'),
                'messages': [m['content'][:200] for m in messages]
            }
            recalls.append(summary)

        return recalls

    def summarize_session(self, session_id=None, brain=None):
        """
        Generate a summary for a session using the Brain.

        Args:
            session_id: Session to summarize (default: current)
            brain: Brain instance to use for summarization
        """
        session_id = session_id or self.get_current_session()
        messages = storage.get_session_messages(session_id, limit=50)

        if not messages:
            return None

        conversation_text = "\n".join([f"{m['role']}: {m['content']}" for m in messages])

        if brain:
            try:
                response = brain.execute(
                    prompt=f"Summarize this conversation in 2-3 sentences:\n\n{conversation_text[:3000]}",
                    context={},
                    constraints={}
                )
                if response.success:
                    return response.natural_response or response.content
            except Exception as e:
                print(f"Error summarizing session: {e}")

        return conversation_text[:200] + "..." if len(conversation_text) > 200 else conversation_text

    def get_session_history(self, session_id=None, limit=100):
        """Get full message history for a session."""
        session_id = session_id or self.get_current_session()
        return storage.get_session_messages(session_id, limit=limit)

    def list_recent_sessions(self, limit=20):
        """List recent conversation sessions."""
        return storage.list_sessions(limit=limit)

    def delete_session(self, session_id=None):
        """Delete a conversation session."""
        session_id = session_id or self.current_session_id
        if session_id:
            storage.delete_session(session_id)
            if session_id == self.current_session_id:
                self.current_session_id = None

    def clear_old_sessions(self, days=30):
        """Delete sessions older than specified days."""
        return storage.delete_old_sessions(days=days)

    def get_stats(self):
        """Get memory statistics."""
        sessions = storage.list_sessions(limit=1000)
        return {
            'total_sessions': len(sessions),
            'current_session': self.current_session_id
        }

    def _update_session_title(self, first_message):
        """Generate a title from the first user message."""
        # Take first 50 chars or up to first sentence
        title = first_message[:50].strip()
        if '?' in title:
            title = title.split('?')[0] + '?'
        elif '.' in title:
            title = title.split('.')[0] + '.'
        elif len(first_message) > 50:
            title = title + '...'

        self.session_title = title
        # Update in database
        storage.update_session_title(self.current_session_id, title)


memory = Memory()
