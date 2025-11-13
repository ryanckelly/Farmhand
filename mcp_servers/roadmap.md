# Stardew Valley Wiki MCP - Development Roadmap

## Overview

This roadmap outlines the development plan for building a comprehensive MCP server for the Stardew Valley Wiki. The goal is to provide structured data extraction for all major game content categories.

## Current Status (Phase 1 ✅ Complete)

### Fully Supported Categories
- ✅ **Crops** - seasons, growth time, regrowth, prices
- ✅ **Fish** - location, time, seasons, weather
- ✅ **Bundles** - requirements, quantities (filters rewards)
- ✅ **NPCs (Gifts)** - loved/liked/neutral/disliked/hated gifts
- ✅ **Animals** - building, purchase price, produce
- ✅ **Items (Generic)** - source, sell/purchase prices
- ✅ **Monsters (Partial)** - stats, drops, locations (when structured)

### Coverage Statistics
- **Total wiki categories**: 461 (167 content categories after filtering)
- **Phase 1 parser coverage**: ~7 major categories
- **Parser quality**: Excellent for structured infobox pages

### Known Limitations
- Festival data: Minimal extraction (informational pages)
- Skills: Partial extraction (concatenated field names)
- Achievements: Minimal extraction (list page format)
- Some monster pages: Variable quality depending on structure

## Phase 2: High Priority Custom Parsers

**Target**: Build custom parsers for frequently-used game content with poor current coverage

### 2.1 Recipe Parser
**Category Size**: 85 pages (Cooking + Crafting)
**Current Coverage**: Excellent structure, needs enhancement
**Priority**: HIGH

**Goals**:
- Extract ingredients with quantities
- Parse buff effects (duration, stats)
- Capture energy/health restoration
- Source/unlock requirements
- Sell prices

**Estimated Effort**: Medium (2-3 hours)

### 2.2 NPC Schedule & Events Parser
**Category Size**: 39 NPC pages
**Current Coverage**: Minimal (type/name only)
**Priority**: HIGH

**Goals**:
- Parse daily schedules by season/weather
- Extract heart event triggers and requirements
- Birthday information
- Marriage candidate status
- Favorite/disliked gifts (already working)

**Estimated Effort**: High (4-6 hours) - complex table structures

### 2.3 Monster Combat Parser
**Category Size**: 59 monster pages
**Current Coverage**: Variable (excellent for some, minimal for others)
**Priority**: HIGH

**Goals**:
- Standardize HP, damage, defense, speed extraction
- Parse drop tables with probabilities
- Floor/location spawns
- Variations (dangerous mode, mages, etc.)
- Resistances/immunities

**Estimated Effort**: Medium (2-3 hours)

### 2.4 Skills & Professions Parser
**Category Size**: 6 skill pages
**Current Coverage**: Partial (messy field names)
**Priority**: MEDIUM-HIGH

**Goals**:
- Extract level progression (1-10)
- Parse profession trees (level 5 & 10 choices)
- XP requirements per level
- Unlocked recipes per level
- Profession bonuses

**Estimated Effort**: High (4-5 hours) - complex nested structures

**Phase 2 Total Estimated Time**: 12-17 hours

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

**Phase 3 Total Estimated Time**: 10-15 hours

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

### Phase 2 Goals
- [ ] 11+ major categories supported
- [ ] NPC schedules parseable
- [ ] Recipe ingredients structured
- [ ] Monster stats standardized

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

**Phase 2**: 2-3 development sessions (12-17 hours)
**Phase 3**: 2-3 development sessions (10-15 hours)
**Phase 4**: 1-2 development sessions (8-12 hours)
**Phase 5**: Optional, based on need

**Total Estimated Time to Production-Ready**: 30-44 hours

## Next Steps

1. ✅ Complete Phase 1 (Done)
2. ✅ Create roadmap.md (This document)
3. ✅ Create plan.md with detailed execution instructions
4. ✅ Update README with current support
5. → Begin Phase 2.1: Recipe Parser
