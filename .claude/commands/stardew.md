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

2.5. Regenerate HTML files for Railway deployment (silent background step):
   ```bash
   python dashboard/dashboard_generator.py --with-trends
   ```
   - This ensures Railway deployments always have the latest data
   - Run this silently in the background (don't display output to user)
   - Keeps dashboard.html and trends.html in sync with game state

3. **ASK USER FOR PERMISSION**: After displaying the dashboard, ask "Would you like me to proceed to generate recommendations for your session today?"
   - If user says NO or wants to stop, end here (they may just want a quick status check)
   - If user says YES, continue to step 4

4. Read core files to understand context (only if user grants permission):
   - `dashboard/dashboard_state.json` - Progress metrics and momentum analysis
   - `diary.json` - Recent play sessions and bundle readiness
   - `goals.md` - Current strategic objectives
   - `metrics.json` - Trends and growth patterns
   - `save_snapshot.json` - Full save state including unlockables_status

5. **SELECT TOP 5 ACTIVE UNLOCKS** (manual Claude decision):
   - Review all 45+ unlockables in `save_snapshot.json['unlockables_status']`
   - Analyze each unlockable's:
     - `completion_percent` (0-100%)
     - `next_step` (what needs to be done)
     - `category` (Map Access, Progression, Island Features, etc.)
   - Select the 5 most relevant unlockables based on:
     - **Proximity to completion** (80%+ = high priority)
     - **Goal alignment** (matches goals.md objectives)
     - **Recent activity** (worked on in last 3 sessions from diary.json)
     - **Dependency chains** (unlocks that block other progress)
     - **Player intent** (inferred from play patterns)
   - Write selection to `dashboard/top5_unlocks.json`:
     ```json
     {
       "selected_at": "<timestamp>",
       "reasoning": "Brief explanation of why these 5 were chosen",
       "unlocks": [
         {
           "name": "Combat Level 10",
           "completion_percent": 0,
           "next_step": "Reach Combat Level 10",
           "category": "Skills"
         },
         ...4 more
       ]
     }
     ```
   - **IMPORTANT**: Always select exactly 5 unlockables, even if some are 0% or 100%
   - Include mix of: near-completion (for motivation), long-term (for planning), blockers (for strategy)

6. **VALIDATE recommendations using a subagent** (see CLAUDE.md for details):
   - Launch validation subagent BEFORE presenting strategy
   - **Use haiku model for fast validation** (set model="haiku")
   - Verify Community Center completion status
   - Verify marriage status and heart levels
   - Cross-check goals.md against save_snapshot.json data
   - Correct any errors found before presenting to user

7. Provide customized session strategy including:
   - **Top 5 Active Unlocks review**: Explain why each was selected and tactical approach
   - Progress review from dashboard_state.json (financials, momentum)
   - **Highlight momentum insights**: hot streaks to maintain, cold streaks to address
   - **Bundle readiness check**: what can be completed RIGHT NOW from diary.json
   - Tactical recommendations aligned with goals.md and selected unlocks
   - Economic analysis and projections
   - Time-sensitive opportunities (birthdays, festivals, last planting days)
   - Specific action items for today's play session (prioritize top 5 unlocks)
