# encounter-tracker
DnD combat encounter tracker

This README is gonna double as a design doc and a HowTo at the same time.

I like DnD and wanted to tie in a personal interest into my portfolio projects so here we are.

The Enounter Logic: The encounter logic will be using the 2014 5th edition rules instead of the new 2024 ones because it'll be more interesting to code.
- Each character has four XP thresholds by level (easy / medium / hard / deadly). Sum across the party → party thresholds.
- Each monster has an XP value from its CR.
- Sum raw monster XP.
- Multiply by a factor based on monster count — because six goblins are harder than one goblin worth six times the XP. Action economy.
- Compare adjusted XP against the party thresholds.


The Stack:
Frontend
  - React 
  - TypeScript 
  - Vite 
  - Tailwind  
Backend
  - FastAPI 
  - Postgres

The Plan:

For the backend we've got:
Logic - 
- Encounter difficulty: XP budgets by party level and size, CR-to-XP tables, multi-monster multipliers, adjusting for the adventuring day rather than a single fight
- Action economy warnings (party of 4 vs. 12 goblins is "medium" on paper but tedious regardless)
- Initiative order with ties, conditions with durations and checks, concentration checks with the DC derived from damage taken, death saves, legendary actions/resistances

API Integrations -
- Open5e or dnd5eapi.co for SRD monsters and spells, with your own caching layer so you're not hammering them per keystroke on search. That's a legitimate reason to have a backend rather than a decorative one.

The Frontend:
  - Drag-to-reorder initiative
  - Inline HP adjustment
  - Condition badges with hover context
  - Monster stat block panel that doesn't require leaving the combat view

Stretch Goal:
  - WebSockets so the DM's board and the players' view stay in sync

