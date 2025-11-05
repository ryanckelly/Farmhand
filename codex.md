# Stardew Bundle Parsing – Change Summary

- Goal: Fix Community Center bundle parsing to report completion based on the number of submitted items required, not whether all bundle slots are filled.

## What Changed
- Updated `save_analyzer.py` to compute bundle completion using definitions:
  - Uses `required` and `all_required` from `bundle_definitions`.
  - Considers a bundle complete when `filled_count >= required` (unless `all_required` is true, then all slots must be filled).
  - Falls back to strict "all slots filled" for unknown/remixed bundles.
- Improved `bundle_definitions.py:get_missing_items_for_bundle`:
  - Respects `all_required`.
  - Returns only the number of items still needed (`remaining_needed`) for choose-N bundles.
  - Handles cases where the save may have fewer boolean slots than defined items.
- Adjusted helpers to reflect the logic:
  - `debug_bundles.py` now imports bundle definitions and prints completion using required-of logic.
  - Rewrote `check_bundles_simple.py` to show slot booleans, filled vs required, and correct completion status for Enchanter’s/Fodder.

## Files Touched
- save_analyzer.py: corrected completion logic and missing-items computation inside `get_detailed_bundle_info`.
- bundle_definitions.py: refined `get_missing_items_for_bundle` behavior.
- debug_bundles.py: aligned display and completion calculation with new logic.
- check_bundles_simple.py: replaced with clearer required-of reporting.

## Why This Fixes It
- Previously, bundles that require only a subset (e.g., 3 of 4) were misreported as incomplete unless all slots were true. This led to incorrect “outstanding bundles” and missing-item lists.
- Now, completion and missing items are derived from the bundle’s `required` count, matching in-game logic.

## Quick Verification
- Summary check:
  - `python -c "import json, save_analyzer as sa; s=sa.analyze_save(); import json; print(json.dumps({'complete': s['bundles']['complete_count'], 'total': s['bundles']['total_count'], 'incomplete': [b['name'] for b in s['bundles']['incomplete_bundles']]}, indent=2))"`
- Focused check (Enchanter’s/Fodder):
  - `python check_bundles_simple.py`
- Full flow:
  - `python session_tracker.py` then inspect `current_state.json` bundle section.

## Observed Result After Fix
- Bundles complete/total reflects required-of logic (e.g., `26/31`).
- Only Enchanter’s shows as incomplete, with `missing_items` indicating one animal product (Rabbit’s Foot). No fish or fruit are falsely flagged.

## Notes
- Unknown/remixed bundles (not in our definitions) still use strict all-slots completion as a safe fallback.
- If you want dynamic requirements pulled from game data, we can wire in content parsing of `Content/Data/Bundles` (via an extractor) and replace the static map.
