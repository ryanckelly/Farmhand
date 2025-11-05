import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np

# Terminal aesthetic colors
TERMINAL_BG = '#1e1e1e'
TERMINAL_GREEN = '#00ff00'
TERMINAL_GOLD = '#ffd700'
TERMINAL_RED = '#ff3333'

# Configure matplotlib for terminal aesthetic
plt.rcParams['figure.facecolor'] = TERMINAL_BG
plt.rcParams['axes.facecolor'] = TERMINAL_BG
plt.rcParams['axes.edgecolor'] = TERMINAL_GREEN
plt.rcParams['axes.labelcolor'] = TERMINAL_GREEN
plt.rcParams['text.color'] = TERMINAL_GREEN
plt.rcParams['xtick.color'] = TERMINAL_GREEN
plt.rcParams['ytick.color'] = TERMINAL_GREEN
plt.rcParams['grid.color'] = TERMINAL_GREEN
plt.rcParams['font.family'] = 'monospace'
plt.rcParams['savefig.facecolor'] = TERMINAL_BG
plt.rcParams['savefig.edgecolor'] = TERMINAL_BG

# Load diary data
with open('diary.json', 'r') as f:
    data = json.load(f)

entries = data['entries']

# Extract data for charts
sessions = []
dates = []
money_changes = []
farming_xp = []
fishing_xp = []
foraging_xp = []
mining_xp = []
combat_xp = []
bundles_completed = []
cumulative_bundles = 0
abigail_hearts = []
total_xp = []

for entry in entries:
    sessions.append(entry['session_id'])
    dates.append(datetime.fromisoformat(entry['detected_at']))
    money_changes.append(entry['financial']['change'])

    skills = entry['changes_detail']['skill_changes']
    farming = skills.get('farming', {}).get('xp_gained', 0)
    fishing = skills.get('fishing', {}).get('xp_gained', 0)
    foraging = skills.get('foraging', {}).get('xp_gained', 0)
    mining = skills.get('mining', {}).get('xp_gained', 0)
    combat = skills.get('combat', {}).get('xp_gained', 0)

    farming_xp.append(farming)
    fishing_xp.append(fishing)
    foraging_xp.append(foraging)
    mining_xp.append(mining)
    combat_xp.append(combat)
    total_xp.append(farming + fishing + foraging + mining + combat)

    bundles = entry['changes_detail']['bundles_completed']
    bundles_completed.append(bundles)
    cumulative_bundles += bundles

    # Get Abigail hearts
    friendships = entry['changes_detail']['friendship_changes']
    if 'Abigail' in friendships:
        abigail_hearts.append(friendships['Abigail']['new_hearts'])
    else:
        abigail_hearts.append(abigail_hearts[-1] if abigail_hearts else 0)

# Create figure with subplots
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Stardew Valley Play Session Trends', fontsize=16, fontweight='bold', color=TERMINAL_GOLD)

# Chart 1: Money Changes Per Session
colors = [TERMINAL_GREEN if x > 0 else TERMINAL_RED for x in money_changes]
ax1.bar(range(len(money_changes)), money_changes, color=colors, alpha=0.8, edgecolor=TERMINAL_GREEN, linewidth=0.5)
ax1.axhline(y=0, color=TERMINAL_GREEN, linestyle='--', linewidth=0.5, alpha=0.5)
ax1.set_title('Net Money Change Per Session', fontweight='bold', color=TERMINAL_GOLD)
ax1.set_xlabel('Session Number')
ax1.set_ylabel('Gold (g)')
ax1.grid(axis='y', alpha=0.2, linestyle=':')
# Add value labels on bars
for i, v in enumerate(money_changes):
    label_color = TERMINAL_GREEN if v > 0 else TERMINAL_RED
    if v > 0:
        ax1.text(i, v + 5000, f'{v:,.0f}g', ha='center', va='bottom', fontsize=8, color=label_color)
    else:
        ax1.text(i, v - 5000, f'{v:,.0f}g', ha='center', va='top', fontsize=8, color=label_color)

# Chart 2: XP Gains by Skill (Stacked Area)
skill_colors = ['#00ff00', '#00ccff', '#33ff33', '#ffff00', '#ff6600']
ax2.stackplot(range(len(sessions)),
              farming_xp, fishing_xp, foraging_xp, mining_xp, combat_xp,
              labels=['Farming', 'Fishing', 'Foraging', 'Mining', 'Combat'],
              colors=skill_colors, alpha=0.7)
ax2.set_title('XP Gains by Skill Per Session', fontweight='bold', color=TERMINAL_GOLD)
ax2.set_xlabel('Session Number')
ax2.set_ylabel('Experience Points')
legend = ax2.legend(loc='upper left', facecolor=TERMINAL_BG, edgecolor=TERMINAL_GREEN)
for text in legend.get_texts():
    text.set_color(TERMINAL_GREEN)
ax2.grid(axis='y', alpha=0.2, linestyle=':')

# Chart 3: Total XP Per Session
ax3.plot(range(len(total_xp)), total_xp, marker='o', linewidth=2, markersize=6,
         color=TERMINAL_GREEN, markerfacecolor=TERMINAL_GREEN, markeredgecolor=TERMINAL_GOLD)
ax3.fill_between(range(len(total_xp)), total_xp, alpha=0.2, color=TERMINAL_GREEN)
ax3.set_title('Total XP Gains Per Session', fontweight='bold', color=TERMINAL_GOLD)
ax3.set_xlabel('Session Number')
ax3.set_ylabel('Total Experience Points')
ax3.grid(alpha=0.2, linestyle=':')
# Add average line
avg_xp = np.mean(total_xp)
ax3.axhline(y=avg_xp, color=TERMINAL_GOLD, linestyle='--', linewidth=1, label=f'Average: {avg_xp:.0f} XP')
legend = ax3.legend(facecolor=TERMINAL_BG, edgecolor=TERMINAL_GREEN)
for text in legend.get_texts():
    text.set_color(TERMINAL_GREEN)

# Chart 4: Abigail Friendship Progression
ax4.plot(range(len(abigail_hearts)), abigail_hearts, marker='D', linewidth=3,
         markersize=8, color='#ff1493', markerfacecolor='#ff1493', markeredgecolor=TERMINAL_GOLD)
ax4.set_title('Abigail Relationship Progress', fontweight='bold', color=TERMINAL_GOLD)
ax4.set_xlabel('Session Number')
ax4.set_ylabel('Heart Level')
ax4.set_ylim(0, 14)
ax4.grid(alpha=0.2, linestyle=':')
# Add milestone markers
for i, hearts in enumerate(abigail_hearts):
    if hearts in [8, 10, 11] and (i == 0 or abigail_hearts[i-1] != hearts):
        ax4.annotate(f'{hearts} hearts', xy=(i, hearts), xytext=(5, 10),
                    textcoords='offset points', fontsize=9, fontweight='bold', color='#ff1493')

plt.tight_layout()
plt.savefig('dashboard/stardew_trends.png', dpi=300, bbox_inches='tight')
print("Chart saved as 'dashboard/stardew_trends.png'")

# Create a second figure for bundle and financial overview
fig2, (ax5, ax6) = plt.subplots(1, 2, figsize=(16, 6))
fig2.suptitle('Bundle Progress & Financial Trends', fontsize=16, fontweight='bold', color=TERMINAL_GOLD)

# Chart 5: Bundles Completed Per Session
cumulative = np.cumsum(bundles_completed)
ax5.bar(range(len(bundles_completed)), bundles_completed, alpha=0.8, color=TERMINAL_GREEN,
        edgecolor=TERMINAL_GOLD, linewidth=0.5, label='Per Session')
ax5.plot(range(len(cumulative)), cumulative, marker='o', linewidth=2,
         markersize=6, color=TERMINAL_GOLD, markerfacecolor=TERMINAL_GOLD,
         markeredgecolor=TERMINAL_GREEN, label='Cumulative')
ax5.set_title('Community Center Bundles Completed', fontweight='bold', color=TERMINAL_GOLD)
ax5.set_xlabel('Session Number')
ax5.set_ylabel('Bundles')
legend = ax5.legend(facecolor=TERMINAL_BG, edgecolor=TERMINAL_GREEN)
for text in legend.get_texts():
    text.set_color(TERMINAL_GREEN)
ax5.grid(axis='y', alpha=0.2, linestyle=':')
# Add total
ax5.text(len(cumulative)-1, cumulative[-1] + 0.5, f'Total: {cumulative[-1]}/31',
         fontweight='bold', fontsize=10, color=TERMINAL_GOLD)

# Chart 6: Cumulative Earnings Over Time
cumulative_money = np.cumsum(money_changes)
starting_money = entries[0]['financial']['starting_money']
total_money = [starting_money + cm for cm in cumulative_money]

ax6.plot(range(len(total_money)), total_money, marker='o', linewidth=2,
         markersize=6, color=TERMINAL_GOLD, markerfacecolor=TERMINAL_GOLD, markeredgecolor=TERMINAL_GREEN)
ax6.fill_between(range(len(total_money)), total_money, alpha=0.2, color=TERMINAL_GOLD)
ax6.set_title('Total Money Over Sessions', fontweight='bold', color=TERMINAL_GOLD)
ax6.set_xlabel('Session Number')
ax6.set_ylabel('Total Gold')
ax6.grid(alpha=0.2, linestyle=':')
# Format y-axis with commas
ax6.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}g'))

plt.tight_layout()
plt.savefig('dashboard/stardew_bundles_money.png', dpi=300, bbox_inches='tight')
print("Chart saved as 'dashboard/stardew_bundles_money.png'")

# Print summary statistics
print("\n" + "="*60)
print("SUMMARY STATISTICS")
print("="*60)
print(f"Total Sessions: {len(entries)}")
print(f"Total Money Earned: {sum(money_changes):,}g")
print(f"Average Money Per Session: {np.mean(money_changes):,.0f}g")
print(f"Best Session: {max(money_changes):,}g")
print(f"Total XP Gained: {sum(total_xp):,}")
print(f"Average XP Per Session: {np.mean(total_xp):,.0f}")
print(f"Total Bundles Completed: {sum(bundles_completed)}")
print(f"Abigail: {abigail_hearts[0]} -> {abigail_hearts[-1]} hearts")
print("="*60)
