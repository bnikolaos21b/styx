# STYX - Conversation Intelligence Platform

## Executive Summary

STYX is a **conversation analytics and intelligence platform** that provides deep insights into AI assistant conversations. It captures, stores, analyzes, and visualizes every interaction between users and AI assistants (specifically ARGUS, a home network AI assistant).

**Core Purpose:** Enable developers and analysts to review, search, filter, and understand conversation patterns, tool usage, failures, and performance metrics.

---

## Architecture Overview

### Technology Stack
- **Frontend:** Pure HTML5, CSS3, Vanilla JavaScript (no frameworks)
- **Backend:** Python Flask REST API
- **Database:** SQLite (conversation_logs.db)
- **Deployment:** Raspberry Pi 5, systemd services
- **Access:** Web-based UI (port 8892)

### File Structure
```
/home/pi-nb21/styx/
├── index.html          # Single-page application (5352 lines)
├── PROJECT_OVERVIEW.md # This document
└── (no build process - served directly)
```

### Data Flow
```
User Message → ARGUS Assistant → Tool Execution → Response
     ↓              ↓                  ↓              ↓
Conversation Logger ←───────────────────────────────┘
     ↓
SQLite Database
     ↓
STYX Web UI (Flask API → Browser)
```

---

## Core Features

### 1. Sessions View (Default View)

**Purpose:** Browse and search all conversation sessions.

**Layout (Desktop - 4 Panels):**
```
┌──────────┬┈┈┈┈┬────────────┬┈┈┈┈┬──────────────┬┈┈┈┈┬─────────────────┐
│ FILTERS  │handle│  SESSIONS  │handle│ CONVERSATION │handle│ TURN DETAIL     │
│ 220px    │  1   │   280px    │  2   │    flex      │  3   │    flex         │
│min:180px │resize│  min:200px │resize│   min:200px  │resize│   min:300px     │
└──────────┴──────┴────────────┴──────┴──────────────┴──────┴─────────────────┘
```

**Panel 1: Filters (220px, resizable)**
- **Search:** Text search across messages
- **Date:** Today, Yesterday, This week, Custom
- **Quality:** Any, Good, Warn, Fail (radio buttons)
- **Tool:** Dropdown of all tools + "No tool selected"
- **Duration:** Any, Fast (<5s), Normal (5-15s), Slow (>15s)
- **Error Type:** API Error, Tool Execution, LLM Call 2, Timeout
- **Second Pass:** Any, Used, Not used
- **Buttons:** Apply Filter, Reset Filters

**Panel 2: Sessions List (280px, resizable)**
- Shows session cards with:
  - First message (truncated)
  - Timestamp
  - Turn count
  - Quality indicator (green/yellow/red dot)
- Click session → loads conversation in Panel 3
- Selected session highlighted with blue left border

**Panel 3: Conversation (flex, resizable)**
- Chat replay view showing:
  - User messages (right-aligned, blue bubbles)
  - ARGUS responses (left-aligned, dark bubbles)
  - Tool badges on ARGUS messages
  - Timestamps on each message
- Click any message bubble → opens Turn Detail in Panel 4
- Shows turn dividers (Turn 1, Turn 2, etc.)

**Panel 4: Turn Detail (flex, resizable)**
- Comprehensive turn analysis:
  - User Message
  - Tool Selected (with params)
  - Tool Result (success/failure)
  - Final Response
  - Raw LLM Output (expandable)
  - **Execution Trace** (most important):
    - context_injected: Shows context size, memories, time context
    - llm_call_1_start: Full prompt sent to LLM (expandable)
    - llm_call_1_done: LLM response (expandable)
    - tool_executing: Tool being called
    - tool_result: Tool execution result with type-specific data:
      - **Presence tools:** Home/away counts, device states
      - **DNS tools:** Device info, domain count, top domains
      - **Health tools:** CPU%, temp, services status
      - **Speed tools:** Download/upload/ping
    - response_ready: Final response metadata
  - Failure Diagnostics (if failed)
  - Second Pass indicator (if used)

**Resize Handles:**
- 3 handles (4px wide blue lines) between panels
- Hover → turns blue
- Drag → resize adjacent panels
- Min widths enforced

---

### 2. Analytics View

**Purpose:** High-level metrics and statistics.

**Stats Row (4 cards):**
- Total Sessions (30 days)
- Total Turns (30 days)
- Failure Rate (percentage)
- Average Response Time

**Tool Usage Panel:**
- Table showing each tool:
  - Tool name
  - Count (times used)
  - Avg duration
  - Success rate (with visual bar)
  - Last used date

**Charts:**
- Hourly volume (last 24 hours)
- Daily volume (last 7 days)

**Top Errors Panel:**
- Error type
- Count
- Last seen
- Example error message

---

### 3. Actions View

**Purpose:** Audit log of all actions taken by ARGUS.

**Filters:**
- All, Blocks, Approvals, Restarts, Failed

**Table Columns:**
- Timestamp
- Action type
- Target (device/domain)
- Result (success/failed)
- Duration
- Details (expandable)

---

## Mobile Experience (< 768px)

### Bottom Navigation
```
┌─────────────────────────────────────────┐
│  📋        💬        📊        📋       │
│Sessions   Detail   Analytics  Actions  │
└─────────────────────────────────────────┘
```

### Sessions View (Mobile)
- Full-screen session list
- Search bar at top
- Session cards (full width)
- Tap session → opens Conversation view

### Conversation View (Mobile)
- Full-screen chat replay
- Back button to sessions
- Tap message → Bottom sheet slides up

### Turn Detail (Mobile Bottom Sheet)
- Slides up from bottom (85vh height)
- Shows same content as desktop Panel 4
- **Scrollable** with iOS momentum scrolling
- Close button or swipe down

---

## Data Model

### Database Schema (SQLite)

**conversation_sessions:**
```sql
session_id TEXT PRIMARY KEY
chat_id TEXT
started_at TIMESTAMP
ended_at TIMESTAMP
turn_count INTEGER
had_errors INTEGER
quality_score TEXT  -- 'good', 'warn', 'bad'
first_message TEXT
```

**conversation_turns:**
```sql
id INTEGER PRIMARY KEY AUTOINCREMENT
session_id TEXT (FK)
turn_number INTEGER
timestamp TIMESTAMP
user_message TEXT
tool_selected TEXT
tool_params TEXT (JSON)
tool_result_success INTEGER
tool_result_summary TEXT
final_response TEXT
duration_seconds REAL
used_second_pass INTEGER
error TEXT
quality TEXT
llm_raw_response TEXT
failure_stage TEXT
llm_error_code TEXT
execution_trace TEXT (JSON)
full_prompt TEXT
full_llm_response_1 TEXT
full_llm_response_2 TEXT
context_breakdown TEXT (JSON)
timing_breakdown TEXT (JSON)
receive_timestamp REAL
send_timestamp REAL
true_latency_ms REAL
```

---

## API Endpoints

### `/api/conversations`
- **GET:** List all sessions (limit, offset, filters)
- Returns: `{ sessions: [...], total: N }`

### `/api/conversations/<session_id>`
- **GET:** Get session with all turns
- Returns: `{ session: {...}, turns: [...] }`

### `/api/conversations/turns`
- **GET:** List turns with filters
- Query params: limit, offset, quality, tool, search, date, etc.
- Returns: `{ turns: [...], total: N }`

### `/api/conversations/stats`
- **GET:** Analytics statistics
- Returns: Stats object with tool usage, hourly/daily volume, errors

### `/api/audit_log`
- **GET:** Actions audit log
- Query params: limit, filter (all/blocks/approvals/restarts/failed)
- Returns: `{ actions: [...] }`

---

## Key Functionality Details

### Session Loading & Filtering

**loadSessions():**
1. Fetch sessions from API
2. Build session map (group turns by session_id)
3. Filter by search, date, quality, tool, etc.
4. Render session cards
5. Auto-select first session

**applyFilters():**
1. Read all filter inputs
2. Call loadSessions() with filters
3. Re-render sessions list
4. Update turn count badges

**renderSessions():**
- Creates session card HTML
- Shows: time, first message, turn count, quality dot
- Click handler → selectSession(session_id)

### Conversation Rendering

**selectSession(sessionId):**
1. Find session in sessions array
2. Fetch turns from API
3. Call renderChatReplay(turns)
4. Update turns count

**renderChatReplay(turns):**
- Creates chat bubble HTML
- User bubbles: right-aligned, blue
- ARGUS bubbles: left-aligned, dark, with tool badge
- Click handler → selectTurn(turn.id, 'user'/'argus')

### Turn Detail Rendering

**selectTurn(turnId, side):**
1. Find turn in turns array
2. Set selectedTurn = { ...turn, side }
3. Re-render chat (highlight selected bubble)
4. Call showTurnDetail(turn)

**showTurnDetail(turn):**
- Builds HTML for all turn sections
- Execution trace parsed from JSON
- Each trace event rendered with type-specific card
- Expandable sections for large data

### Execution Trace Rendering

**renderExecutionTrace(traceJson):**
1. Parse JSON trace array
2. For each event:
   - Determine event type (context, llm_call, tool, etc.)
   - Set icon and color
   - Build inline detail
   - Build expandable content
   - Add [▶ Show X] buttons for large data
3. Return HTML

**Trace Event Types:**
- `context_injected`: Context size, memories, time context
- `llm_call_1_start`: Prompt sent to LLM
- `llm_call_1_done`: LLM response
- `tool_selected`: Tool name
- `tool_executing`: Tool call details
- `tool_result`: Tool execution result (type-specific)
- `response_ready`: Final response metadata

**Tool Result Types:**
- `presence`: Home/away counts, device states
- `dns`: Device info, domains
- `health`: CPU, temp, services
- `speed`: Download/upload/ping
- `network`: Device counts
- `generic`: Default

---

## CSS Architecture

### CSS Variables (Theme)
```css
--bg-primary: #0a0f1e
--bg-secondary: #0d1426
--bg-tertiary: rgba(13,20,38,0.6)
--text-primary: #f1f5f9
--text-secondary: #94a3b8
--text-muted: #64748b
--accent-blue: #3b82f6
--accent-green: #22c55e
--accent-yellow: #eab308
--accent-red: #ef4444
--nav-height: 72px
--mobile-nav-height: 60px
```

### Responsive Breakpoints
- **Desktop:** min-width: 1025px
- **Tablet:** 769px - 1024px
- **Mobile:** max-width: 768px

### Key CSS Classes
- `.sessions-layout`: 4-panel flex container
- `.resize-handle`: Drag handles between panels
- `.chat-bubble-user`: User message bubbles
- `.chat-bubble-argus`: ARGUS response bubbles
- `.trace-event`: Execution trace event cards
- `.collapsible-header/ content`: Expandable sections
- `.mobile-bottom-sheet`: Mobile turn detail popup

---

## JavaScript Architecture

### Global State
```javascript
let sessions = [];
let turns = [];
let selectedSession = null;
let selectedTurn = null;
let allTurns = [];
let currentTool = null;
let refreshIntervals = {};
let isAuthenticated = false;
```

### Core Functions

**Session Management:**
- `loadSessions()`: Fetch and render sessions
- `renderSessions()`: Build session card HTML
- `selectSession(id)`: Load conversation for session
- `renderChatReplay(turns)`: Build chat bubbles

**Turn Management:**
- `selectTurn(id, side)`: Select and show turn detail
- `showTurnDetail(turn)`: Render turn detail panel
- `renderExecutionTrace(trace)`: Render trace events
- `closeTurnDetail()`: Close turn detail panel

**Filtering:**
- `applyFilters()`: Apply all filters
- `resetFilters()`: Clear all filters
- `filterActions(filter)`: Filter actions table

**Analytics:**
- `loadAnalytics()`: Load stats and charts
- `renderBarChart(id, data, maxBars)`: Render bar charts

**Mobile:**
- `switchMobileTab(tabName)`: Switch mobile views
- `openMobileConversation(id)`: Open conversation on mobile
- `openMobileBottomSheet(turn)`: Show turn detail bottom sheet
- `closeMobileBottomSheet()`: Close bottom sheet

**Utilities:**
- `escapeHtml(text)`: Sanitize HTML
- `formatJson(text)`: Pretty-print JSON
- `updateLastRefresh()`: Update timestamp
- `getToolCategory(name)`: Get tool category for styling

---

## Authentication

**Password:** Configured in settings modal
**Storage:** Session-based (not persistent)
**Check:** `checkAuth()` on page load
**Redirect:** If not authenticated, show login screen

---

## Settings

**Config Storage:** localStorage ('styx-config')
**Settings:**
- API URL (default: http://192.168.2.23:8080)
- Auto Refresh (on/off)
- Time Format (12h/24h)

**Auto-Refresh Intervals:**
- Sessions: 30 seconds
- Analytics: 60 seconds (when tab active)
- Logs: 10 seconds (when tab active + tool selected)

---

## Known Issues & Limitations

### Current Limitations
1. **No panel width persistence:** Reset on refresh
2. **No export functionality:** Can't export conversations
3. **No real-time updates:** Polling only (no WebSocket)
4. **Single user:** No multi-user support
5. **No conversation editing:** Read-only view

### Browser Compatibility
- **Tested:** Chrome, Safari (iOS), Firefox
- **Mobile:** iOS Safari, Android Chrome
- **Desktop:** All modern browsers

---

## Recent Fixes (Latest Commits)

1. **Panel Resize** - Removed `!important` from CSS so JS can override
2. **Right Panel Flush** - body margin/padding set to 0
3. **Desktop Nav Tabs** - Changed from `display: block` to `flex`
4. **Mobile Scroll** - Fixed bottom sheet scrolling
5. **Filters Vertical** - Removed duplicate CSS causing horizontal layout
6. **renderTurns undefined** - Renamed to renderChatReplay
7. **Favicon 404** - Added inline SVG favicon

---

## Development Guidelines

### Adding New Features
1. **No frameworks:** Keep it vanilla JS
2. **Mobile-first:** Ensure mobile works before desktop
3. **Responsive:** Test at 375px, 768px, 1024px, 1920px
4. **Performance:** Lazy load, debounce search, limit results
5. **Accessibility:** Min 44px touch targets, proper ARIA labels

### Code Style
- **CSS:** BEM-like naming, CSS variables for theme
- **JS:** Async/await for API calls, error handling with try/catch
- **HTML:** Semantic tags, proper heading hierarchy

### Testing Checklist
- [ ] Desktop (1920x1080) - all 4 panels visible
- [ ] Tablet (1024x768) - responsive layout
- [ ] Mobile (375x667) - bottom nav, scrollable
- [ ] Panel resize works
- [ ] Filters apply correctly
- [ ] Turn detail shows all data
- [ ] Mobile bottom sheet scrolls
- [ ] No console errors

---

## Quick Reference

### Port Numbers
- **STYX UI:** 8892
- **Backend API:** 8080

### File Locations
- **Frontend:** `/home/pi-nb21/styx/index.html`
- **Backend:** `/home/pi-nb21/systems/argus/dashboard/dashboard_server.py`
- **Database:** `/home/pi-nb21/systems/argus/memory/conversation_logs.db`

### Service Commands
```bash
# Check status
sudo systemctl status argus-dashboard

# Restart
sudo systemctl restart argus-dashboard

# View logs
journalctl -u argus-dashboard -f
```

### Git Commands
```bash
cd /home/pi-nb21/styx
git add -A
git commit -m "fix: description"
git push origin main
```

---

## Contact & Support

**Developer:** Full documentation in PROJECT_OVERVIEW.md
**Repository:** GitHub (@bnikolaos21b/styx)
**Issues:** Check console for errors, review execution trace for debugging

---

*Last Updated: March 15, 2026*
*Version: 4.3 (Mobile Fixed)*
*Lines of Code: 5352 (HTML/CSS/JS in single file)*
