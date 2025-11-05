# /finish - End Session and Update Goals

You are ending a Stardew Valley play session. Update goals.md based on all the context you've gathered during this session.

## Steps to Execute:

1. **Review session context:**
   - Check diary.json entry from session_tracker.py (already run at session start)
   - Review conversation history for user accomplishments
   - Note: "I found Dwarf Scroll IV", "I unlocked the boat", skill level ups, etc.

2. **Read current goals.md** to see what needs updating

3. **Update goals.md:**
   - Mark completed goals with `[x]` and move to "Completed Goals" section
   - Update progress notes (e.g., "currently level 9" → "currently level 10")
   - Add any new goals mentioned in conversation
   - Update numeric values (money earned, skill XP, completion dates)
   - Add completion dates for major milestones (e.g., "completed Fall 27, Year 2")

4. **Provide session summary:**
   - List goals that were completed
   - List goals that progressed (but not yet complete)
   - Show what was updated in goals.md
   - Mention any new goals added

## Important Notes:

- Use the context you already have - don't re-run session_tracker.py
- Be conservative - only mark things [x] if confirmed during session
- Preserve user's goal structure and formatting
- Update in-progress indicators accurately

Execute these steps now and update goals.md.
