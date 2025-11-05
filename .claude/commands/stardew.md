Run the Stardew Valley session tracker and display the Farmhand Dashboard:

1. Run session tracker using relative path:
   ```bash
   python session_tracker.py
   ```

2. Generate and display the colored terminal dashboard:
   ```bash
   python dashboard/dashboard_generator.py --terminal
   ```
   **CRITICAL - DISPLAY IN RESPONSE**:
   - **COPY the entire dashboard output into your response text** (not just tool results)
   - Users cannot see collapsed tool results - the dashboard MUST appear in the response body
   - Display the dashboard as a code block at the very top of your response
   - Preserve ANSI escape codes (they will render as green in the terminal)
   - Example format:
     ```
     [Dashboard output here with ANSI codes]
     ```
   - Then below the dashboard, continue with other text/questions

3. **ASK USER FOR PERMISSION**: After displaying the dashboard, ask "Would you like me to proceed to generate recommendations for your session today?"
   - If user says NO or wants to stop, end here (they may just want a quick status check)
   - If user says YES, continue to step 4

4. Read core files to understand context (only if user grants permission):
   - `dashboard/dashboard_state.json` - Progress metrics and momentum analysis
   - `diary.json` - Recent play sessions and bundle readiness
   - `goals.md` - Current strategic objectives
   - `metrics.json` - Trends and growth patterns

5. **VALIDATE recommendations using a subagent** (see CLAUDE.md for details):
   - Launch validation subagent BEFORE presenting strategy
   - **Use haiku model for fast validation** (set model="haiku")
   - Verify Community Center completion status
   - Verify marriage status and heart levels
   - Cross-check goals.md against save_snapshot.json data
   - Correct any errors found before presenting to user

6. Provide customized session strategy including:
   - Progress review from dashboard_state.json (unlocks, financials, momentum)
   - **Highlight momentum insights**: hot streaks to maintain, cold streaks to address
   - **Bundle readiness check**: what can be completed RIGHT NOW from diary.json
   - Tactical recommendations aligned with goals.md
   - Economic analysis and projections
   - Time-sensitive opportunities (birthdays, festivals, last planting days)
   - Specific action items for today's play session
