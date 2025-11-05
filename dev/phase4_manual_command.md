# Phase 4: Manual Command Interface

**Status:** ✅ COMPLETE
**Estimated Time:** 1 hour
**Dependencies:** Phase 1-3 complete

## Goals

- Create simple, user-friendly CLI
- Generate dashboard with one command
- Provide helpful feedback and error messages

## Tasks

### 4.1 CLI Interface
- [ ] Add `if __name__ == "__main__"` block
- [ ] Create welcome banner
- [ ] Add command-line arguments parser
- [ ] Implement `--preview` flag for terminal output

### 4.2 File Generation Flow
- [ ] Run data extraction
- [ ] Generate `dashboard_state.json`
- [ ] Render ASCII dashboard to HTML
- [ ] Save `dashboard.html`
- [ ] Print success message with path

### 4.3 Error Handling
- [ ] Check for required files (save_snapshot.json, diary.json)
- [ ] Provide helpful error messages
- [ ] Suggest running `session_tracker.py` if data missing
- [ ] Handle JSON parsing errors gracefully

### 4.4 Documentation
- [ ] Create usage instructions
- [ ] Add examples to docstring
- [ ] Create README section for dashboard

## Technical Details

### CLI Implementation

```python
# dashboard_generator.py

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate Stardew Valley Focus Flow Dashboard',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python dashboard_generator.py              # Generate dashboard
  python dashboard_generator.py --preview    # Show preview in terminal
  python dashboard_generator.py --output custom.html
        """
    )

    parser.add_argument('--preview', action='store_true',
                       help='Show ASCII preview in terminal')
    parser.add_argument('--output', default='dashboard.html',
                       help='Output HTML filename')

    args = parser.parse_args()

    print("=" * 65)
    print("  STARDEW VALLEY FOCUS FLOW DASHBOARD")
    print("=" * 65)
    print()

    try:
        generator = DashboardGenerator()

        # Generate state
        print("📊 Analyzing save data...")
        state = generator.generate_state()

        print("✓ Unlocks calculated")
        print("✓ Financials analyzed")
        print("✓ Momentum detected")
        print()

        # Generate HTML
        print("🎨 Rendering dashboard...")
        html_path = generator.render_html(state, args.output)

        print(f"✓ Dashboard saved to: {html_path}")
        print()
        print("Open dashboard.html in your browser to view!")

        # Optional preview
        if args.preview:
            print("\n" + "=" * 65)
            print("TERMINAL PREVIEW:")
            print("=" * 65)
            print(generator.get_ascii_preview(state))

    except FileNotFoundError as e:
        print(f"✗ Error: Required file not found")
        print(f"  {e}")
        print()
        print("💡 Tip: Run 'python session_tracker.py' first to generate save data")
        sys.exit(1)

    except json.JSONDecodeError as e:
        print(f"✗ Error: Invalid JSON in save files")
        print(f"  {e}")
        sys.exit(1)

    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### Expected Output

```
=================================================================
  STARDEW VALLEY FOCUS FLOW DASHBOARD
=================================================================

📊 Analyzing save data...
✓ Unlocks calculated
✓ Financials analyzed
✓ Momentum detected

🎨 Rendering dashboard...
✓ Dashboard saved to: C:\opt\stardew\dashboard.html

Open dashboard.html in your browser to view!
```

### With Preview Flag

```bash
python dashboard_generator.py --preview
```

```
=================================================================
  STARDEW VALLEY FOCUS FLOW DASHBOARD
=================================================================

📊 Analyzing save data...
✓ Unlocks calculated
✓ Financials analyzed
✓ Momentum detected

🎨 Rendering dashboard...
✓ Dashboard saved to: C:\opt\stardew\dashboard.html

Open dashboard.html in your browser to view!

=================================================================
TERMINAL PREVIEW:
=================================================================
╔═══════════════════════════════════════════════════════════════╗
║  STARDEW VALLEY FOCUS FLOW DASHBOARD                         ║
║  Generated: 2025-11-03 18:45:23 | Fall 26, Year 2            ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  UNLOCKS PROGRESS                                             ║
...
```

## Completion Criteria

- [ ] `python dashboard_generator.py` runs successfully
- [ ] Dashboard opens in browser (or provides clear path)
- [ ] Error messages are helpful and actionable
- [ ] `--preview` flag works correctly
- [ ] Documentation is clear

## Notes

- Keep command interface simple - one primary use case
- Error messages should guide users to solutions
- Consider adding `--help` output examples
- Future: Could add `--watch` mode for auto-regeneration

---

**Status:** ⏳ Pending
**Last Updated:** 2025-11-03
