# AI Agent System - Quick Reference

This directory contains specialized AI agent configurations for the Valorant Lobby Scout project.

## Available Agents

### 1. 🎨 [UI/GUI Development Agent](ui-gui-agent.md)
**When to use**: Anything related to the user interface, visual design, or user experience

**Common tasks**:
- Modify GUI layout or styling
- Add new UI components
- Fix UI bugs or responsiveness issues
- Implement animations or loading states
- Update the dark theme colors

**Primary file**: `gui_app.py`

---

### 2. 🔧 [API Integration Agent](api-integration-agent.md)
**When to use**: Anything involving external API calls or platform integrations

**Common tasks**:
- Add new API endpoints
- Fix API connection issues
- Implement rate limiting
- Add new streaming platforms
- Debug API responses
- Optimize API call patterns

**Primary files**: `valorant_api_client.py`, `tracker_api.py`, `streaming_services.py`

---

### 3. 📊 [Data & Statistics Agent](data-statistics-agent.md)
**When to use**: Anything related to data storage, statistics, or analytics

**Common tasks**:
- Add new statistics calculations
- Improve cache efficiency
- Implement new data structures
- Enhance smurf detection
- Fix data persistence issues
- Optimize database queries

**Primary files**: `player_stats.py`, `match_history.py`, `cache_manager.py`

---

### 4. 🐛 [Testing & QA Agent](testing-qa-agent.md)
**When to use**: Testing, debugging, or quality assurance tasks

**Common tasks**:
- Write unit tests
- Debug errors
- Analyze logs
- Profile performance
- Fix bugs
- Improve test coverage

**Primary files**: All `test_*.py` files, `BUGFIX_LOG_ERROR.md`

---

### 5. 📝 [Documentation Agent](documentation-agent.md)
**When to use**: Creating or updating documentation

**Common tasks**:
- Update README files
- Document new features
- Write API documentation
- Create user guides
- Update changelogs
- Write code comments

**Primary files**: `README.md`, `FEATURES.md`, all `.md` files

---

## Quick Agent Selection

```
┌─────────────────────────────────────────┐
│ What do you want to work on?           │
└─────────────────────────────────────────┘
           │
           ├─ GUI/Interface? ────────────► UI/GUI Agent
           │
           ├─ API/External data? ────────► API Integration Agent
           │
           ├─ Stats/Data/Cache? ─────────► Data & Statistics Agent
           │
           ├─ Tests/Bugs/Quality? ───────► Testing & QA Agent
           │
           └─ Docs/Comments? ────────────► Documentation Agent
```

## Multi-Agent Workflows

Some tasks require multiple agents working together:

### New Feature Development
```
1. Documentation Agent   → Plan and spec the feature
2. API Agent (if needed) → Integrate external APIs
3. Data Agent (if needed) → Add data structures
4. UI Agent              → Create interface
5. Testing Agent         → Write tests
6. Documentation Agent   → Update docs
```

### Bug Fix
```
1. Testing Agent     → Reproduce and identify root cause
2. Relevant Agent    → Implement the fix
3. Testing Agent     → Verify with tests
4. Documentation Agent → Document in bug log
```

### Performance Optimization
```
1. Testing Agent     → Profile and identify bottlenecks
2. Relevant Agent    → Optimize code
3. Testing Agent     → Verify improvements
4. Documentation Agent → Update performance notes
```

## Agent Rules

### Do's ✅
- Stay within your area of expertise
- Coordinate with other agents on cross-cutting concerns
- Update documentation when making changes
- Write tests for new functionality
- Follow the project's coding standards
- Log significant decisions

### Don'ts ❌
- Don't make changes outside your domain without coordinating
- Don't skip testing for "small" changes
- Don't leave outdated documentation
- Don't introduce breaking changes without discussion
- Don't commit commented-out code or TODOs without tickets

## Getting Started

1. **Identify your task type** using the quick selection guide above
2. **Read the relevant agent's full documentation** (linked above)
3. **Check if other agents need to be involved** for cross-cutting concerns
4. **Start work** following the agent's guidelines and best practices
5. **Coordinate handoffs** if multiple agents are needed

## Need Help?

- **Unclear which agent?** Start with Documentation Agent to clarify the task
- **Multiple agents needed?** Plan with Documentation Agent first
- **Agent conflict?** Refer to `.cursorrules` for project-wide guidance
- **New agent needed?** Propose it with clear scope and responsibilities

## File Ownership Map

Quick reference for which agent owns which files:

| Files | Primary Agent |
|-------|---------------|
| `gui_app.py` | UI/GUI Agent |
| `valorant_api_client.py`, `tracker_api.py`, `streaming_services.py` | API Agent |
| `player_stats.py`, `match_history.py`, `cache_manager.py` | Data Agent |
| `test_*.py`, logs | Testing Agent |
| `*.md` files | Documentation Agent |
| `player.py`, `game.py` | Shared (coordinate) |

## Version History

- **v1.0** (Oct 2025): Initial agent system created
  - 5 specialized agents
  - Clear separation of concerns
  - Comprehensive agent guides

---

For the complete project guidelines, see `../.cursorrules` in the parent directory.

