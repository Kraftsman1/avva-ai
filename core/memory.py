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
        # Generate smart title after first exchange (user + assistant)
        if self.session_title == "New Conversation":
            self._generate_smart_title()

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

    def toggle_pin(self, session_id):
        """Toggle pin status for a session."""
        return storage.toggle_session_pin(session_id)

    def export_conversation(self, session_id=None, format='markdown'):
        """
        Export a conversation to markdown or JSON format.

        Args:
            session_id: Session to export (default: current)
            format: 'markdown' or 'json'

        Returns:
            Formatted string content
        """
        session_id = session_id or self.current_session_id
        if not session_id:
            return None

        session = storage.get_session(session_id)
        messages = storage.get_session_messages(session_id, limit=1000)

        if not session:
            return None

        if format == 'json':
            import json
            from datetime import datetime

            # Serialize datetime objects
            def serialize(obj):
                if hasattr(obj, 'isoformat'):
                    return obj.isoformat()
                return obj

            export_data = {
                'session': {
                    'id': session['id'],
                    'title': session['title'],
                    'created_at': serialize(session.get('created_at')),
                    'updated_at': serialize(session.get('updated_at')),
                    'brain_id': session.get('brain_id'),
                    'pinned': session.get('pinned', False)
                },
                'messages': [
                    {
                        'role': msg['role'],
                        'content': msg['content'],
                        'timestamp': serialize(msg.get('timestamp')),
                        'brain_id': msg.get('brain_id'),
                        'intent': msg.get('intent')
                    }
                    for msg in messages
                ],
                'exported_at': datetime.now().isoformat()
            }
            return json.dumps(export_data, indent=2)

        else:  # markdown
            lines = []
            lines.append(f"# {session['title']}")
            lines.append("")
            lines.append(f"**Created:** {session.get('created_at', 'Unknown').strftime('%Y-%m-%d %H:%M') if hasattr(session.get('created_at'), 'strftime') else session.get('created_at', 'Unknown')}")
            lines.append(f"**Brain:** {session.get('brain_id', 'Unknown')}")
            lines.append("")
            lines.append("---")
            lines.append("")

            for msg in messages:
                timestamp = msg.get('timestamp', '')
                if hasattr(timestamp, 'strftime'):
                    timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    timestamp_str = str(timestamp)

                role_label = "**User**" if msg['role'] == 'user' else "**AVA**"
                lines.append(f"### {role_label} - {timestamp_str}")
                lines.append("")
                lines.append(msg['content'])
                lines.append("")
                lines.append("---")
                lines.append("")

            return "\n".join(lines)

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
        """Generate a basic title from the first user message (fallback)."""
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

    def _generate_smart_title(self):
        """Generate an intelligent title using the Brain."""
        try:
            from core.brain import brain

            # Get the first exchange (user message + assistant response)
            messages = storage.get_session_messages(self.current_session_id, limit=2)
            if len(messages) < 2:
                return

            # Build context from first exchange
            user_msg = messages[0]['content']
            assistant_msg = messages[1]['content']

            # Ask Brain to generate a concise title
            prompt = f"""Generate a very short, descriptive title (3-5 words max) for this conversation.
The title should capture the main topic or question.
Do not use quotes. Just return the title text.

User: {user_msg[:200]}
Assistant: {assistant_msg[:200]}

Title:"""

            response = brain.process(prompt)

            if response:
                # Extract title from response
                if isinstance(response, dict):
                    title = response.get("text", "").strip()
                else:
                    title = str(response).strip()

                # Clean up the title
                title = title.replace('"', '').replace("'", '').strip()
                # Remove common prefixes
                for prefix in ["Title:", "title:", "**", "*"]:
                    title = title.replace(prefix, '').strip()

                # Limit length
                if len(title) > 60:
                    title = title[:57] + '...'

                # Only update if we got a valid title
                if title and len(title) > 3:
                    self.session_title = title
                    storage.update_session_title(self.current_session_id, title)
                    print(f"✨ Generated smart title: {title}")
        except Exception as e:
            print(f"Could not generate smart title, using fallback: {e}")


memory = Memory()
