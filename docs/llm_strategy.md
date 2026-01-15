# AVA (Advanced Voice Virtual Assistant)

## LLM Integration Strategy — Ollama

This document defines how AVA integrates Large Language Models (LLMs) using **Ollama** as a local-first backend. The goal is to enhance natural language understanding while preserving performance, predictability, and user trust.

---

## 1. Guiding Principles

LLM usage in AVA follows strict product and architectural rules:

* LLMs enhance understanding, not control execution
* Local-first by default, cloud-optional
* Predictability over conversational depth
* Explicit user control and transparency
* No AI dependency for core system actions

AVA must remain fully usable without any LLM enabled.

---

## 2. Why Ollama

Ollama is the preferred LLM backend for AVA due to:

* Fully local execution
* Simple HTTP-based API
* Model-agnostic design
* Offline capability
* Strong alignment with Linux user expectations

Ollama enables advanced language handling without introducing cloud dependencies or API keys.

---

## 3. Role of the LLM in AVA

The LLM is **not** the primary decision-maker. It operates as a fallback and enhancement layer.

### Appropriate Uses

* Intent disambiguation
* Parameter extraction from natural language
* Explaining errors, logs, or commands
* Summarization and clarification
* Developer assistance

### Explicitly Excluded Uses

* Direct command execution
* Privileged or destructive decision-making
* Always-on processing
* System state control without confirmation

---

## 4. Intent Resolution Pipeline

LLM involvement occurs only after deterministic paths fail.

```
User Input
  ↓
Rule-Based Intent Match
  ↓
Structured NLP (slots / parameters)
  ↓
LLM Fallback (Ollama)
  ↓
Permission Gate
  ↓
Skill Execution
```

This ensures speed and safety for common commands.

---

## 5. Structured LLM Contract

All LLM responses must conform to a strict, machine-validated schema.

### Example Response Schema

```json
{
  "intent": "open_app",
  "arguments": {
    "app": "firefox"
  },
  "confidence": 0.92
}
```

### Handling Rules

* Responses below confidence threshold trigger clarification
* No execution occurs without explicit intent validation
* Invalid schemas are discarded

---

## 6. Execution & Safety Rules

* LLM output can only suggest actions
* Final execution always passes through the permission gate
* Destructive or elevated actions require user confirmation
* No silent execution from AI-generated output

Safety is enforced at the platform level, not delegated to the model.

---

## 7. Ollama Deployment Model

### External Ollama (Recommended)

* Ollama is installed and managed separately by the user
* AVA detects Ollama via localhost API
* AVA functions normally if Ollama is unavailable

#### Advantages

* Smaller AVA package size
* Independent model management
* Clear separation of responsibilities
* Simpler Flatpak sandboxing

This is the default and recommended approach.

---

### Bundled Ollama (Deferred)

Bundling Ollama within AVA is not recommended for early releases due to:

* Increased package size
* GPU and driver complexity
* Slower updates
* Higher maintenance overhead

This option may be revisited later if user demand justifies it.

---

## 8. User Experience & Controls

User-facing language avoids technical terminology.

### User Controls

* Enable or disable advanced language assistance
* Select preferred local model
* Operate AVA in full offline mode

### User-Facing Terminology

* “Local AI assistance”
* “Advanced language understanding (offline)”

Technical terms such as “LLM” or “Ollama” are reserved for developer documentation.

---

## 9. Security & Privacy Considerations

* All LLM processing occurs locally
* No data is transmitted externally
* Only minimal, relevant context is shared with the model
* Shared data is logged and inspectable

LLM integration must never obscure what information is being processed.

---

## 10. Model Strategy

Initial model selection prioritizes:

* Small to medium parameter sizes
* Fast inference times
* Strong instruction-following

Models that introduce excessive latency or verbosity are avoided.

---

## 11. Positioning Summary

LLM support in AVA is positioned as:

* Optional
* Local
* Assistive
* Transparent

Ollama enhances AVA’s intelligence without compromising its reliability, performance, or trust model.
