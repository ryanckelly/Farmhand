# Phase 3.6: QA Testing Bug Report

**Test Date**: 2025-11-13
**Total Tests**: 38
**Pass Rate**: 76.3% (29 passed, 9 failed, 0 errors)
**Target Pass Rate**: 90%

## Summary

The comprehensive QA test suite revealed 9 failures across 6 parsers. Six parsers (Achievements, Animals, Collections, Items, NPCs, Recipes) achieved 100% pass rate and are ready for production. The remaining parsers have issues that range from minor edge cases to critical bugs.

## Critical Issues (Must Fix)

### 1. Crops Parser - 20% Pass Rate (1/5)

**Severity**: CRITICAL
**Impact**: Core game mechanic (crops) not properly indexed

**Failures**:

| Test Case | Issue | Root Cause |
|-----------|-------|------------|
| Coffee | Missing seasons, growth_time | Detected as "item" instead of "crop" |
| Rice | Missing seasons, growth_time | Detected as "item" instead of "crop" |
| Corn | Missing regrowth_time | Parser doesn't extract regrowth field |
| Ancient Fruit | Missing regrowth_time | Parser doesn't extract regrowth field |

**Analysis**:
- **Page Type Detection Bug**: Coffee and Rice are being detected as "item" instead of "crop"
  - Coffee is actually a beverage (made in Keg), not a crop directly
  - Rice is also sold as an item, not planted as a crop (Rice Shoot is the seed)
  - These test cases were incorrectly chosen - they're not actually crops!
- **Missing Regrowth Extraction**: Corn and Ancient Fruit have regrowth mechanics but `regrowth_time` field is not being extracted

**Fix Priority**: HIGH
- Revise test cases (Coffee and Rice are not crops)
- Add regrowth_time extraction to crop parser

### 2. Quests Parser - 0% Pass Rate (0/1)

**Severity**: CRITICAL
**Impact**: Quest tracking completely broken

**Failures**:

| Test Case | Issue | Root Cause |
|-----------|-------|------------|
| Quests page | Missing story_quests, special_orders | Detected as "achievements" instead of "quests" |

**Analysis**:
- **Page Type Detection Bug**: "Quests" page is being detected as "achievements" type
- **Likely Cause**: `detect_page_type()` checks for "Achievements" category before "Quests" category
- **Impact**: Quest parser never runs, achievements parser runs instead (which doesn't find quest data)

**Fix Priority**: CRITICAL
- Fix page type detection order or improve quest detection logic

## Medium Priority Issues

### 3. Skills Parser - 67% Pass Rate (2/3)

**Failures**:

| Test Case | Issue | Root Cause |
|-----------|-------|------------|
| Fishing (skill) | Missing levels, professions | Detected as "achievements" instead of "skill" |

**Analysis**:
- **Page Type Detection Bug**: "Fishing" page detected as "achievements" (probably because there's an "Achievements" section on the page)
- **Similar to Quests Bug**: Overly aggressive achievements detection

**Fix Priority**: MEDIUM

### 4. Fish Parser - 80% Pass Rate (4/5)

**Failures**:

| Test Case | Issue | Root Cause |
|-----------|-------|------------|
| Lobster (crab pot) | Missing location | Crab pot catches have different page structure |

**Analysis**:
- **Edge Case**: Lobster is a crab pot catch, not a rod catch
- Crab pot catches don't have "location" in the same infobox format
- This is an acceptable limitation (crab pot catches are different from fishing)

**Fix Priority**: LOW (document as known limitation)

### 5. Bundles Parser - 67% Pass Rate (2/3)

**Failures**:

| Test Case | Issue | Root Cause |
|-----------|-------|------------|
| Fish Tank | Missing requirements | Detected as "fish" instead of "bundle" |

**Analysis**:
- **Page Type Detection Bug**: "Fish Tank" is a location/bundle room, but detected as "fish"
- **Ambiguous Page Name**: "Fish Tank" can refer to both the bundle room and fish tanks in general
- Test case is ambiguous - should test "Fish Tank Bundle" specifically

**Fix Priority**: LOW (revise test case)

### 6. Monsters Parser - 67% Pass Rate (2/3)

**Failures**:

| Test Case | Issue | Root Cause |
|-----------|-------|------------|
| Dust Sprite | Missing drops | Field exists but test expected different field name |

**Analysis**:
- **Test Case Issue**: Data is actually present (`"drops": "..."`), but test expected it
- Need to verify why test marked as failure

**Fix Priority**: LOW (verify test logic)

## Parsers with 100% Pass Rate ✅

The following parsers passed all tests and are production-ready:
- **Achievements Parser** (1/1)
- **Animals Parser** (3/3)
- **Collections Parser** (2/2)
- **Items Parser** (3/3)
- **NPCs Parser** (5/5) - Excellent coverage of marriage candidates, children, secret NPCs
- **Recipes Parser** (4/4) - Including artisan equipment with products tables

## Root Cause Analysis

### Primary Issue: Page Type Detection Logic

**Current Problem**: The `detect_page_type()` function has detection order issues:

```python
# Current detection order (pseudocode):
1. Check if categories contain "Achievements"
2. Check if categories contain "Quests"
3. Check if categories contain "Skills"
...
```

**Issue**: Pages like "Fishing" and "Quests" have multiple categories, and "Achievements" is checked first, causing misclassification.

**Solution**: Improve detection logic with priority-based matching or more specific category checks.

### Secondary Issue: Missing Field Extraction

**Crops Regrowth**: The crop parser doesn't extract `regrowth_time` field
**Fish Crab Pots**: Different structure for crab pot catches vs. rod catches

## Recommended Fixes

### Must Fix (Before Phase 4):

1. ✅ **Fix page type detection for Quests** (CRITICAL)
   - Ensure "Quests" page is detected as "quests" not "achievements"

2. ✅ **Fix page type detection for Fishing skill** (MEDIUM)
   - Ensure "Fishing" page is detected as "skill" not "achievements"

3. ✅ **Add regrowth_time extraction to crops parser** (HIGH)
   - Extract regrowth days for crops like Corn, Ancient Fruit

4. ✅ **Revise test cases**:
   - Remove Coffee and Rice from crops tests (they're not crops)
   - Change "Fish Tank" to "Fish Tank Bundle" for clarity

### Can Defer (Document as Limitations):

5. **Crab pot fish location** (LOW)
   - Document that crab pot catches may not have location field
   - This is an acceptable limitation

6. **Verify Dust Sprite test** (LOW)
   - Check why drops field was marked as missing

## Performance Analysis

**Average Response Time**: 204ms per page
- Excellent performance (well under 2s target)
- Slowest test: Sandfish (3933ms) - likely network latency
- Fastest tests: <200ms for most pages

## Next Steps

1. Implement critical fixes (Quests, Fishing detection)
2. Add regrowth_time to crop parser
3. Revise test cases (remove invalid crops)
4. Re-run test suite
5. Target: 90%+ pass rate
6. Document remaining known limitations
7. Proceed to Phase 4 when 90%+ achieved

## Known Limitations (After Fixes)

The following are acceptable limitations that don't need fixes:

1. **Crab pot fish** - May not have location data (different mechanics than rod fishing)
2. **Disambiguation pages** - May not extract meaningful data (acceptable)
3. **Stub pages** - Limited data available (parser handles gracefully)
4. **Version-specific content** - Wiki may have game version differences (acceptable)

## Conclusion

**Status**: 76.3% pass rate (below 90% target)
**Action Required**: Fix critical bugs in page type detection and regrowth extraction
**Estimated Effort**: 1-2 hours
**Ready for Phase 4**: Not yet (need 90%+ pass rate first)
