# Stardew Valley Wiki MCP - Development Roadmap

## Overview

This roadmap outlines the development plan for building a comprehensive MCP server for the Stardew Valley Wiki. The goal is to provide structured data extraction for all major game content categories.

## Current Status (Phase 1 & 2 ✅ Complete)

### Fully Supported Categories
- ✅ **Crops** - seasons, growth time, regrowth, prices
- ✅ **Fish** - location, time, seasons, weather
- ✅ **Bundles** - requirements, quantities (filters rewards)
- ✅ **NPCs** - gift preferences, heart events, marriageable status, address, family, birthday
- ✅ **Recipes** - ingredients, buffs, energy/health, unlock source, recipe type
- ✅ **Animals** - building, purchase price, produce
- ✅ **Items (Generic)** - source, sell/purchase prices
- ✅ **Monsters** - HP, damage, defense, speed, XP, drops, locations (integer stats)

### Coverage Statistics
- **Total wiki categories**: 461 (167 content categories after filtering)
- **Phase 1 & 2 parser coverage**: 8 major categories
- **Parser quality**: Excellent for structured infobox pages

### Known Limitations
- Festival data: Minimal extraction (informational pages)
- Skills: Partial extraction (concatenated field names)
- Achievements: Minimal extraction (list page format)
- Some monster pages: Variable quality depending on structure

## Phase 2: High Priority Custom Parsers ✅ Complete

**Target**: Build custom parsers for frequently-used game content with poor current coverage

### 2.1 Recipe Parser ✅
**Category Size**: 85 pages (Cooking + Crafting)
**Status**: COMPLETE
**Priority**: HIGH

**Completed Goals**:
- ✅ Extract ingredients with quantities
- ✅ Parse buff effects (duration, stats)
- ✅ Capture energy/health restoration
- ✅ Source/unlock requirements
- ✅ Sell prices
- ✅ Automatic recipe type detection (cooking vs. crafting)

**Actual Effort**: Medium (2-3 hours)

### 2.2 NPC Schedule & Events Parser ✅
**Category Size**: 39 NPC pages
**Status**: COMPLETE (schedules deferred)
**Priority**: HIGH

**Completed Goals**:
- ✅ Extract heart event triggers and requirements
- ✅ Birthday information
- ✅ Marriage candidate status
- ✅ Address/residence extraction
- ✅ Family members extraction
- ✅ Favorite/disliked gifts (already working)
- ⏭️ Parse daily schedules by season/weather (deferred - complex)

**Actual Effort**: Medium (3-4 hours)

### 2.3 Monster Combat Parser ✅
**Category Size**: 59 monster pages
**Status**: COMPLETE
**Priority**: HIGH

**Completed Goals**:
- ✅ Standardize HP, damage, defense, speed extraction
- ✅ Integer conversion for all numeric stats
- ✅ Floor/location spawns
- ✅ Drop table extraction
- ⏭️ Variations (dangerous mode, mages, etc.) - handled by existing parser
- ⏭️ Resistances/immunities - not consistently documented on wiki

**Actual Effort**: Low (1-2 hours)

### 2.4 Skills & Professions Parser
**Category Size**: 6 skill pages
**Current Coverage**: Partial (messy field names)
**Priority**: MEDIUM-HIGH
**Status**: DEFERRED TO PHASE 3

**Goals** (unchanged):
- Extract level progression (1-10)
- Parse profession trees (level 5 & 10 choices)
- XP requirements per level
- Unlocked recipes per level
- Profession bonuses

**Estimated Effort**: High (4-5 hours) - complex nested structures

**Phase 2 Total Time**: 6-9 hours (actual)

## Phase 3: Medium Priority Enhancements

**Target**: Enhance existing parsers and add less-frequently-used categories

### 3.1 Building Enhancement
**Category Size**: 15 farm buildings
**Current Coverage**: Excellent (costs, materials, upgrades)
**Priority**: LOW (already good)

**Goals**:
- Add capacity information (animals, items)
- Processing time for machines
- Output products

**Estimated Effort**: Low (1-2 hours)

### 3.2 Location & Shop Inventory
**Category Size**: 25 locations + 18 town locations
**Current Coverage**: Good (addresses, hours, occupants)
**Priority**: MEDIUM

**Goals**:
- Parse shop inventories (items, prices, stock)
- Seasonal availability
- Unlock requirements

**Estimated Effort**: Medium (3-4 hours)

### 3.3 Quest Parser
**Category Size**: Unknown (needs discovery)
**Current Coverage**: Not tested
**Priority**: MEDIUM

**Goals**:
- Quest requirements (items, conditions)
- Rewards (items, gold, friendship)
- Quest givers and triggers
- Time limits

**Estimated Effort**: Medium (3-4 hours)

### 3.4 Achievement Tracker
**Category Size**: 13 achievements
**Current Coverage**: Minimal (list page)
**Priority**: MEDIUM

**Goals**:
- Parse achievement requirements
- Track completion criteria
- Associated Steam/console achievements

**Estimated Effort**: Low (1-2 hours)

### 3.5 Collections Parser
**Category Size**: Unknown (Museum, Fish, Cooking, Shipping)
**Current Coverage**: Not tested
**Priority**: MEDIUM

**Goals**:
- Museum artifact/mineral collections
- Fish collection tracking
- Cooking/crafting recipe collections
- Shipping collection

**Estimated Effort**: Medium (2-3 hours)

### 3.6 Comprehensive Parser QA Testing
**Priority**: HIGH (Gatekeeper for Phase 4)
**Current Coverage**: Not started

**Goals**:
Design and execute adversarial test cases to identify parser weaknesses before production deployment. Each parser will be tested with edge cases, malformed data, missing sections, and unusual wiki formatting.

**Test Strategy by Parser**:

**Crops Parser**
- [ ] Crops with no regrowth (one-time harvest)
- [ ] Multi-season crops (e.g., Coffee)
- [ ] Crops with giant variants
- [ ] Trellis crops vs. normal crops
- [ ] Paddy crops (rice)

**Fish Parser**
- [ ] Legendary fish (unique catch conditions)
- [ ] Fish with complex time windows
- [ ] Fish requiring specific weather + season combinations
- [ ] Crab pot catches vs. rod catches
- [ ] Fish with fishing level requirements

**Bundle Parser**
- [ ] Remixed bundles vs. standard bundles
- [ ] Bundles with quality requirements (gold star items)
- [ ] Bundles with choice slots (pick X of Y items)
- [ ] Partially completed bundles
- [ ] Missing Bundle (#36 post-CC content)

**NPC Parser**
- [ ] Marriage candidates (12 NPCs with 14-heart events)
- [ ] Non-marriage candidates (no heart events)
- [ ] Children (Jas, Vincent - limited events)
- [ ] Secret NPCs (Krobus, Dwarf)
- [ ] NPCs with complex family trees
- [ ] NPCs with no fixed address (traveling merchants)
- [ ] Gift preferences with "All Universal X" entries

**Recipe Parser**
- [ ] Recipes with complex ingredient counts (10+ items)
- [ ] Recipes with no sell price (uncraftable items)
- [ ] Recipes unlocked via events (not shops/leveling)
- [ ] Recipes with multiple unlock methods
- [ ] Recipes with buffs but no energy/health
- [ ] Crafting recipes for machines vs. placeable items

**Monster Parser**
- [ ] Monsters with variants (Slimes by color)
- [ ] Monsters with conditional stats (Dangerous mode)
- [ ] Monsters with complex drop tables
- [ ] Monsters in multiple locations
- [ ] Monsters with special abilities/immunities
- [ ] Boss monsters vs. regular monsters

**Animal Parser**
- [ ] Animals requiring building upgrades (Deluxe Barn/Coop)
- [ ] Animals with seasonal restrictions
- [ ] Animals with multiple product types
- [ ] Animals with quality modifiers (Large Egg, etc.)

**Item Parser**
- [ ] Items with no purchase price (forage only)
- [ ] Items with no sell price (quest items)
- [ ] Items with seasonal availability
- [ ] Items with multiple sources
- [ ] Items that are both crafted and purchased

**Edge Cases (All Parsers)**
- [ ] Pages with missing infoboxes
- [ ] Pages with malformed tables
- [ ] Pages with embedded templates/transclusions
- [ ] Stub pages with minimal data
- [ ] Redirect pages
- [ ] Disambiguation pages
- [ ] Pages with special characters in names
- [ ] Pages with version-specific content (1.5 vs 1.6)

**Evaluation Criteria**:
- **Data completeness**: Did parser extract all expected fields?
- **Data accuracy**: Are extracted values correct?
- **Error handling**: Does parser fail gracefully on missing data?
- **Edge case handling**: Does parser handle unusual formats?
- **Performance**: Does parser complete in reasonable time?

**Deliverables**:
- Comprehensive test script for each parser
- Test results matrix (pass/fail for each test case)
- List of identified bugs/improvements
- Fixes implemented for critical issues
- Known limitations documented

**Estimated Effort**: High (6-8 hours)

**Phase 3 Total Estimated Time**: 16-23 hours (including QA)

## Phase 4: Polish & Documentation

**Target**: Production-ready MCP server with comprehensive documentation

### 4.1 Error Handling
- Graceful degradation for missing data
- Better error messages for failed parses
- Retry logic for API failures

### 4.2 Performance Optimization
- Caching frequently accessed pages
- Batch API requests where possible
- Rate limiting to avoid wiki throttling

### 4.3 Testing Suite
- Unit tests for each parser
- Integration tests for MCP tools
- Regression tests for wiki structure changes

### 4.4 Documentation
- API reference for all tools
- Parser coverage matrix
- Contributing guide for new parsers
- Troubleshooting guide

**Phase 4 Total Estimated Time**: 8-12 hours

## Phase 5: Advanced Features (Optional)

**Target**: Enhanced functionality beyond basic data extraction

### 5.1 Search Enhancement
- Fuzzy matching for typos
- Category-specific search
- Multi-page batch queries

### 5.2 Data Enrichment
- Cross-reference related pages
- Calculate derived stats (profit/day, etc.)
- Provide contextual recommendations

### 5.3 Real-time Updates
- Wiki change notifications
- Auto-refresh cached data
- Version compatibility tracking

**Phase 5 Total Estimated Time**: 15-20 hours

## Success Metrics

### Phase 1 (Current) ✅
- [x] 7+ major categories supported
- [x] Tool descriptions guide LLM selection
- [x] Price data cleaned to integers

### Phase 2 ✅
- [x] 8 major categories supported (deferred 11+ to Phase 3)
- [x] NPC heart events parseable (schedules deferred)
- [x] NPC marriageable status, address, family extracted
- [x] Recipe ingredients structured
- [x] Monster stats standardized (integer conversion)

### Phase 3 Goals
- [ ] 16+ major categories supported
- [ ] Quest requirements structured
- [ ] Achievement tracking available
- [ ] Collection progress trackable

### Phase 4 Goals
- [ ] >90% uptime reliability
- [ ] <500ms average response time
- [ ] Comprehensive test coverage
- [ ] Full API documentation

## Prioritization Strategy

**Decision Factors**:
1. **Category size** (number of pages) - Proxy for importance
2. **Player usage patterns** - Items > Mechanics > Locations
3. **Current coverage quality** - Prioritize gaps
4. **Implementation complexity** - Balance effort vs. value

**Dependencies**:
- Phase 2 builds custom parsers for high-value gaps
- Phase 3 enhances existing + adds medium-value categories
- Phase 4 prepares for production use
- Phase 5 adds advanced features based on actual usage

## Timeline

**Phase 2**: ✅ Complete (6-9 hours actual)
**Phase 3**: 3-4 development sessions (16-23 hours estimated)
**Phase 4**: 1-2 development sessions (8-12 hours)
**Phase 5**: Optional, based on need

**Total Estimated Time to Production-Ready**: 30-44 hours

## Next Steps

1. ✅ Complete Phase 1 (Done)
2. ✅ Create roadmap.md (This document)
3. ✅ Create plan.md with detailed execution instructions
4. ✅ Update README with current support
5. ✅ Complete Phase 2: Recipe Parser, Enhanced NPC Parser, Monster Stats
6. ✅ Add Phase 3.6: Comprehensive Parser QA Testing
7. → Begin Phase 3: Skills, Quests, Collections, QA Testing
