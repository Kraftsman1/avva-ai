
# Product Requirements Document (PRD)

**Project:** AVA – Advanced Voice Virtual Assistant
**Owner:** Product / Platform
**Status:** Approved for Execution
**Scope:** Desktop UI modernization, Core ↔ UI integration, and packaging

---

## 1. Background & Context

AVA currently has a functional Python GUI validating assistant behavior but suffers from:

* Outdated, unappealing UI
* Slow iteration and limited UX flexibility

These issues impact:

* User trust and adoption
* Contributor confidence
* The “platform-ready” positioning of AVA

**Objective:** Deliver a modern, desktop-native interface while preserving the Python Core and enabling platform extensibility.

---

## 2. Problem Statement

### User Problem

Users judge product quality by UI polish. A dated GUI undermines AVA’s perceived reliability and credibility.

### Product Problem

Python GUI toolkits (Tkinter, PyQt, GTK) limit:

* Modern UX design
* Streaming & real-time interaction
* Rapid iteration
* Extensible Brain and plugin workflows

---

## 3. Goals & Objectives

**Primary Goals**

1. Modern, trustworthy desktop UI
2. Separation of Core assistant logic and UI
3. Real-time interaction and streaming support
4. Brain management and configuration UX
5. Single-install Linux distribution

**Success Criteria**

* AVA feels modern and responsive
* UI evolves independently of Core
* Existing assistant functionality preserved
* Platform-first architecture established

**Non-Goals**

* Full Core rewrite (Python remains for MVP)
* Polishing the old Python GUI
* Mobile-first or web-only interfaces
* Non-MVP features beyond Home/Settings/Brains

---

## 4. Proposed Solution

Adopt a **hybrid architecture**:

```
Assistant Core (Python)
↕ Local API (WebSocket, JSON)
UI Layer (Nuxt 3)
↕
Desktop Wrapper (Tauri)
→ Flatpak Distribution
```

**Rationale:**
This separates logic and presentation, enables real-time interactions, supports multiple Brains, and provides a clean upgrade path to Rust or other languages.

---

## 5. Architecture Overview

### 5.1 Assistant Core (Python)

* Handles: intent resolution, Brain orchestration, permissions, plugins
* Owns system interactions and state
* Stateless UI (all UI rendering delegated)

### 5.2 Core ↔ UI Communication Protocol

**Transport:** WebSocket (JSON)
**Event-driven:** Core pushes state & streaming responses; UI pushes user commands
**Versioning:** Protocol version declared at handshake (`v1`)
**Error Handling:** Structured, typed, correlated by `id`

**Message Envelope:**

```json
{
  "type": "string",
  "id": "uuid|null",
  "timestamp": "ISO-8601",
  "payload": {}
}
```

**Core → UI Event Examples:**

* `assistant.state` – listening, thinking, responding
* `assistant.stream` – partial streaming responses
* `assistant.response` – final response
* `brain.list`, `brain.status` – Brain discovery and selection
* `plugin.event` – Plugin-generated events
* `settings.synced` – Settings acknowledgement

**UI → Core Event Examples:**

* `assistant.command` – user input (text/voice)
* `assistant.interrupt` – cancel in-progress commands
* `brain.select` – switch active Brain
* `settings.update` – update Core-managed settings

---

### 5.3 UI Layer (Nuxt 3)

**MVP Screens**

1. **Home**
   * Assistant status
   * Input controls (voice/text)
   * Recent activity

2. **Settings**
   * Permissions & privacy toggles
   * Default Brain selection
   * Voice behavior

3. **Brains**
   * List of installed/configured Brains
   * Select primary/fallback Brain
   * Cloud/local differentiation

---

### 5.4 Desktop Wrapper (Tauri)
* Hosts the Nuxt UI
* Bridges WebSocket communication to system resources

### 5.5 Packaging (Flatpak)
* Single-install distribution
* Sandboxed for security

---

## 6. Functional Requirements
* UI must render **assistant state in real-time**
* Streaming responses displayed incrementally
* Interrupts cancel ongoing commands cleanly
* Brain management fully reflected in UI
* Settings are bi-directionally synced

---

## 9. Risks & Mitigations

| Risk | Mitigation |
| --- | --- |
| IPC complexity | Keep API minimal, use versioned events |
| Flatpak permission conflicts | Conservative defaults, explicit permissions |

---

## 10. Milestones & Phases

**Phase 1: Stabilization**
* Freeze Python GUI
* Isolate Core assistant

**Phase 2: API Exposure**
* Implement WebSocket API
* Define message envelope and schema

**Phase 3: UI MVP**
* Nuxt screens: Home, Settings, Brains

**Phase 4: Desktop Packaging**
* Tauri integration
* Flatpak build
