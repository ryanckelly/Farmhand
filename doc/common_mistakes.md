# Common Mistakes and How to Avoid Them

This document catalogs common data interpretation errors discovered during development and provides guidelines to prevent them.

## Session: 2025-11-02 - Data Misreading Errors

### Mistake 0: Incomplete File Reading with Large JSON Files

**What Happened:**
- Used `Read` tool with offset/limit on save_snapshot.json
- Only read first 500 lines of a 29,955 token file
- Missed critical `ccIsComplete` flag that appeared later in `bundle_reward_flags` array
- Generated entire session strategy based on incomplete data
- Recommended completing CC bundles when CC was already complete

**Root Cause:**
- Large file exceeded token limit, required pagination
- Made recommendations before reading complete data set
- Did not verify critical flags were actually present in read portion
- Confirmation bias: once assumption made, didn't double-check

**How to Avoid:**
- **When reading large files with offset/limit, verify you have all critical sections**
- For save_snapshot.json, always check you've read far enough to see:
  - `bundles.bundle_reward_flags` array (includes `ccIsComplete`)
  - `marriage` object
  - `museum` object
- Better: use targeted extraction commands instead of reading partial files
- **Use validation subagent** to check recommendations against data (now mandatory per CLAUDE.md step 4)

**Fix Applied:**
- Added mandatory validation step to CLAUDE.md workflow
- Requires independent subagent to verify recommendations before presenting
- Prevents confirmation bias by having different agent check the work

---

### Mistake 1: Misinterpreting Bundle Completion Status

**What Happened:**
- Read `bundles_complete: 30` and assumed Community Center was incomplete (30/31)
- Overlooked `ccIsComplete` flag in `bundle_reward_flags` array
- Gave incorrect recommendations about completing "The Missing Bundle"

**Root Cause:**
- Focused on numerical count without checking completion flags
- Did not verify against multiple data sources

**How to Avoid:**
```python
# WRONG: Only checking count
if bundles_complete < 31:
    print("Community Center incomplete")

# RIGHT: Check completion flags first
if 'ccIsComplete' in bundle_reward_flags:
    print("Community Center COMPLETE")
elif bundles_complete < total_bundles:
    print(f"Community Center incomplete: {bundles_complete}/{total_bundles}")
```

**Fix Applied:**
- Added explicit check in CLAUDE.md: "If ccIsComplete is present, Community Center is DONE"
- Updated save_analyzer.py output to include `bundle_reward_flags` prominently

---

### Mistake 2: Not Recognizing Marriage Status from Heart Count

**What Happened:**
- Saw "Abigail: 11 hearts" in friendships data
- Recommended buying Mermaid's Pendant to marry Abigail
- User was already married (11 hearts exceeds 10-heart dating cap)

**Root Cause:**
- Did not understand heart cap mechanics (10 for dating, 14 for married)
- Did not check `spouse` field in save data

**How to Avoid:**
- **Key Rule:** 11+ hearts = ALREADY MARRIED (impossible to reach while dating)
- Always check `marriage.married` and `marriage.spouse` fields
- Cross-reference: If anyone has 11+ hearts, they are the spouse

**Fix Applied:**
- Added marriage status detection to save_analyzer.py
- Detects via both `spouse` field and 11+ heart logic
- Added marriage interpretation guidelines to CLAUDE.md

---

### Mistake 3: Missing Profession in Professions List

**What Happened:**
- Recommended switching to Botanist profession via Statue of Uncertainty
- User had already switched to Botanist
- "Botanist" was clearly visible in `professions` array: `["Artisan", "Gatherer", "Miner", "Fisher", "Tiller", "Scout", "Botanist", "Prospector"]`

**Root Cause:**
- Did not read the professions list carefully
- Made assumption without verifying data

**How to Avoid:**
- **Always read the full professions array**
- Don't assume - verify profession exists in list
- Search for profession name before recommending unlocking it

**Fix Applied:**
- Added profession verification guideline to CLAUDE.md
- Reminder to check professions list before recommendations

---

### Mistake 4: Incorrect Museum Data Interpretation

**What Happened:**
- Ran custom query against save file for museum data
- Query returned 0 museum donations for Year 2 player (impossible)
- Incorrectly told user they had 0 Dwarf Scrolls donated

**Root Cause:**
- save_analyzer.py did not include museum donation tracking
- Relied on ad-hoc XML queries that failed silently
- Did not trust user's statement about being able to trade with Dwarf

**How to Avoid:**
- **Trust the user when they correct you**
- Add missing data tracking to save_analyzer.py rather than running queries
- If data seems implausible, investigate the extraction code

**Fix Applied:**
- Added `get_museum_donations()` function to save_analyzer.py
- Tracks total donations and all 4 Dwarf Scroll statuses
- Includes `can_trade_with_dwarf` boolean flag

---

### Mistake 5: Relying on Outdated goals.md

**What Happened:**
- Read goals.md which said "Marry Abigail (currently 8 hearts)"
- Used this as source of truth despite save file showing 11 hearts
- Did not recognize the discrepancy

**Root Cause:**
- goals.md is user-editable and becomes stale
- Did not prioritize save_snapshot.json data over goals.md

**How to Avoid:**
- **Save data is truth, goals.md is intentions**
- Always trust save_snapshot.json over goals.md
- If discrepancy found, offer to update goals.md
- Check goals.md last modified date vs save file

**Fix Applied:**
- Added explicit guideline to CLAUDE.md about goals.md synchronization
- Updated goals.md to reflect actual completion status

---

## General Principles

### 1. Verify Before Claiming
- Don't state facts without checking the data
- Read arrays completely, not just first element
- Cross-reference multiple data sources

### 2. Trust the User
- If user says "I already did X", believe them
- Investigate why data might not show it
- Apologize and fix the interpretation

### 3. Understand Game Mechanics
- Learn heart cap rules (10 dating, 14 married)
- Understand completion flags vs counts
- Know unlock requirements (scrolls, keys, etc.)

### 4. Priority of Data Sources
1. **save_snapshot.json** - Ground truth (current save state)
2. **diary.json** - Historical truth (what happened)
3. **metrics.json** - Trend analysis
4. **goals.md** - User intentions (may be outdated)

### 5. When in Doubt
- Ask the user instead of guessing
- Say "Let me check the data" and actually check it
- Admit when data is unclear or missing

---

## Checklist for Session Recommendations

Before providing recommendations:

**Step 1: Data Gathering**
- [ ] Read complete save_snapshot.json (or use targeted extraction)
- [ ] Verify you have `marriage`, `museum`, and `bundles.bundle_reward_flags` sections
- [ ] Read diary.json for recent session history
- [ ] Read goals.md for user intentions

**Step 2: Manual Verification**
- [ ] Is Community Center complete? (check `ccIsComplete` flag)
- [ ] Is player married? (check for 11+ hearts or `marriage.spouse`)
- [ ] What professions are unlocked? (read full `professions` array)
- [ ] Can they trade with Dwarf? (check `museum.dwarf_scrolls.can_trade_with_dwarf`)
- [ ] Is goals.md current? (compare dates, check for completed items)
- [ ] Are there discrepancies between goals.md and save data?

**Step 3: Validation (MANDATORY)**
- [ ] Launch validation subagent with Task tool
- [ ] Provide subagent with your draft recommendations
- [ ] Subagent checks recommendations against save_snapshot.json
- [ ] Address any errors found before presenting to user

---

## Future Improvements

**Potential Enhancements:**
1. Add goals.md validation check to session_tracker.py
2. Auto-update goals.md when major milestones detected
3. Add "data quality report" to show stale or conflicting data
4. Implement data source timestamps for freshness checking
5. Create user-facing report of "what changed" that highlights completions

**Lessons for Development:**
- Build comprehensive data extraction first
- Don't rely on ad-hoc queries
- Test data interpretation against edge cases
- Document data source priority clearly
