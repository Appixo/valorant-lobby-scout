# Design brief: Valorant Lobby Scout

I'd like you to redesign the interface of a small Windows desktop app I built for myself: **Valorant Lobby Scout**. Two screenshots of the current version are attached (`current-horizontal.png` and `current-vertical-hover.png`). It works, but it looks like a developer made it. I want it to look and feel like a polished, premium companion app for Valorant players.

## What the app does

The app runs next to the game, usually on a second monitor. When a match starts, it shows all 10 players in two teams (Attackers and Defenders) with their stats, so I can quickly see who I'm playing with and against. The most important moment is **agent select, which lasts about 80 seconds**: in one glance I want to know who is strong, who might be a smurf, who queued together, and whether I've met someone before.

Users look at it between other things, often from a distance and in a dark room. **Readability at a glance matters more than decoration.**

## Information on screen

**Per player (one row each, 5 per team):**
- **Riot ID**: `Name#TAG`. Names can be long and use any script (Greek, Japanese, Cyrillic…)
- **Agent**: e.g. Jett, Omen, Waylay. Shows "—" while a player hasn't picked yet during agent select.
- **Current rank** and **Peak rank**: Iron 1 up to Radiant (25 ranks), or Unranked
- **Account level**: 1 to 500+, or "hidden" when the player hides it
- **Win %** this act
- **K/D** and **headshot %** over the last 5 competitive matches
- **Markers**:
  - **You**: your own row
  - **Hidden name**: the player uses incognito mode. Riot doesn't share their name, so the row shows "Hidden player" (the agent tells them apart). Their stats still load.
  - **Party**: players who queued together share a number. There can be several parties per match.
  - **Possible smurf**: comes with 1–4 reasons, e.g. "Level 31 account already Diamond 3" or "Peaked Immortal 2, now Diamond 2"
  - **Met before**: e.g. "Met 2× before · last 2 days ago on Sunset (opponent, Viper)"
- **Per-row states**: stats loading, stats loaded, and stats unavailable (private or no ranked games). Right now all three show as "—", which is confusing.

**Match level:**
- **Status**: Waiting for Valorant, No active match, Agent Select, or In Game
- **Map**: e.g. Lotus
- **Counts**: number of players, number of hidden names, and matches this session
- **Team header**: "YOUR TEAM" tag, plus a player count per team (fewer than 5 during agent select, when only your own team is known)

**Controls:**
- **Auto mode** on/off: when on, the app detects matches and loads stats by itself
- **Load Stats**: manual stats loading
- **Refresh**
- **Layout toggle**: side by side or stacked
- **Hover a player** to show a detail card with the reasons behind their markers
- **Double-click a player** to open their Tracker.gg profile in the browser
- **Keyboard shortcuts**: F5 refreshes, Ctrl+L switches layout

## Two layouts (both required)

- **Horizontal**: teams side by side. Currently 1420 × 470 px, minimum 1360 × 440.
- **Vertical**: teams stacked, for a vertical second monitor. Currently 720 × 750 px, minimum 690 × 700.

Feel free to propose different sizes if it makes the design better. The window is resizable.

## What I'd like improved

1. **Hierarchy.** Everything has the same weight now. Rank and the warning markers should stand out first.
2. **Ranks are hard to compare at a glance.** Consider rank colours or rank icons, and show the gap between current and peak rank visually.
3. **Markers.** The INFO column uses small text symbols (①, ⚠, ↺) that are easy to miss. Make parties, smurf warnings and "met before" clearly visible without cluttering the table.
4. **Loading, empty and error states.** Distinguish between "not loaded yet", "loading", and "no data".
5. **The header** has 5 controls next to each other. Make it calmer, with a clear primary action.
6. **Hover detail card.** Design it as a proper component.
7. **Agent identity.** Agent portraits or icons would help a lot.

## Style direction

- **Dark theme** only. It should feel at home next to Valorant (sharp, competitive, red #FF4655 for attackers) without copying Riot's UI.
- **Attackers vs defenders** must be instantly distinguishable.
- **Palette:** gold for "you" and purple for hidden names work well today; keep them or propose better ones.
- **Accessibility:** good contrast, with no information shown by colour alone (colour-blind players).
- **No official logos:** don't use the Valorant or Riot logos. Agent and rank icons from the game's assets are fine; the app can download them from valorant-api.com.

## Technical constraints (important)

The app is written in **Python with Tkinter** on Windows, so the design has to be buildable with it.

**Easy to build:**
- Flat colours, borders and 1 px lines
- Any system font, with Segoe UI as the default. Custom fonts are possible if bundled as .ttf.
- PNG icons and images
- Simple hover effects

**Limited in the current table widget (ttk.Treeview):**
- Colours only per whole row, not per cell
- Every row has the same height
- An image can only appear in the first column

**Harder, but possible:**
- Rounded corners, shadows and gradients (these need images or a drawing canvas)
- Custom-drawn rows that replace the table, which would allow per-cell colours and icons

**No animations** beyond simple colour changes.

Ideas that need custom-drawn rows are welcome. Please **mark which parts of the design need custom rows** and which work with a plain table, so I can decide what to build first.

## Deliverables

1. **Mockups of both layouts** in these states:
   - Waiting for Valorant
   - No active match
   - Agent select: own team only, some agents not picked yet, stats loading
   - In game with all stats loaded, showing every marker
2. **The hover detail card**
3. **A small style guide:**
   - Colours as hex values with their role (background, surface, border, text levels, team colours, semantic colours)
   - Type scale: font, size in px, weight
   - Spacing values
   - Row height
   - Icon sizes
4. **Icons I'd need**, exported as PNG at 1× and 2×, or as SVG
5. **Optional:** one "if anything were possible" concept, clearly separated from the buildable version

Use realistic sample data (10 players with varied ranks, two parties, one smurf, a few hidden names), not lorem ipsum.
