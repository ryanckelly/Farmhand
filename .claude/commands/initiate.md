# Stardew Valley Session Initiation

Execute the following steps to start a new play session:

1. **Run session tracker** to detect changes since last play:
   ```bash
   python session_tracker.py
   ```

2. **Read core files** in parallel:
   - diary.json (recent sessions and bundle readiness)
   - goals.md (current objectives)
   - metrics.json (trends and patterns)
   - save_snapshot.json (current game state)

3. **Draft session strategy** including:
   - Progress review (if played since last check)
   - Bundle readiness check (what can be completed RIGHT NOW)
   - Tactical recommendations aligned with goals.md
   - Economic analysis and projections
   - Time-sensitive opportunities (birthdays, festivals, last planting days)
   - Specific action items for today's session

4. **VALIDATE recommendations** using a subagent:
   - Launch validation subagent (general-purpose or debugger)
   - Verify: CC completion status, marriage status, professions, achievements
   - Cross-check against save_snapshot.json data
   - Correct any errors before presenting

5. **Present corrected strategy** to user with actionable recommendations.
