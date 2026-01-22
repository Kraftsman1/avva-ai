
# AVA MVP State Diagrams & Event Flows

---

## 1. Home Screen

**Purpose:** Main assistant interaction panel.

**States**
1. **Idle** – Awaiting user input
2. **Listening** – Capturing voice input
3. **Processing** – Core is interpreting command
4. **Streaming Response** – Partial results arriving
5. **Complete Response** – Final response rendered
6. **Error** – Displayed if Core fails

**WebSocket Event Flow**

| UI Action | Event → Core | Core Response → UI |
| --- | --- | --- |
| User types input | `assistant.command` | `assistant.state: processing` → `assistant.stream` → `assistant.response` |
| User presses “stop” | `assistant.interrupt` | `assistant.state: idle` |

---

## 2. Settings Screen
**Purpose:** Configure global assistant behavior.

---

## 3. Brains Screen
**Purpose:** View, select, and configure LLM Brains.

---

## 4. Global Event Flow Notes
* `assistant.state` (home only)
* `assistant.stream` (home only)
* `core.ready` indicates Core availability
* `plugin.event` – Custom plugin events

---

## 5. Sequence Flow Example: Voice Command (Home Screen)
1. User clicks mic → UI emits: `assistant.command` (mode: voice)
2. Core receives → emits: `assistant.state: listening`
3. Voice captured → `assistant.state: processing`
4. Core begins streaming → `assistant.stream` (chunks)
5. Core completes → `assistant.response`
6. UI renders final response → `assistant.state: idle`

---

## 6. Sequence Flow Example: Switch Brain (Brains Screen)
1. UI user selects a Brain → emits `brain.select`
2. Core updates active Brain → emits `brain.status: active`
