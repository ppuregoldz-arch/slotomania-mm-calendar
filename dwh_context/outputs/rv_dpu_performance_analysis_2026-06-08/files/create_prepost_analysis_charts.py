import matplotlib.pyplot as plt
import numpy as np

# Set style
plt.rcParams['font.family'] = 'Calibri'
plt.rcParams['font.weight'] = 'bold'
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.labelweight'] = 'bold'

# Create figure with cream background
fig = plt.figure(figsize=(20, 16))
fig.patch.set_facecolor('#faf6f1')

# Colors
cream = '#faf6f1'
tableau_colors = ["#4e79a7", "#f28e2b", "#59a14f", "#e15759"]
test_a_color = tableau_colors[0]  # Blue
test_c_color = tableau_colors[1]  # Orange

# Raw Data
test_a_before_dau = 14033
test_a_during_dau = 13518
test_a_before_revenue = 7.25
test_a_during_base_revenue = 7.14
test_a_during_rv_revenue = 63.19
test_a_during_total_revenue = test_a_during_base_revenue + test_a_during_rv_revenue

test_c_before_dau = 13982
test_c_during_dau = 13517
test_c_before_revenue = 8.45
test_c_during_revenue = 3.05

# Calculate changes
test_a_dau_change = ((test_a_during_dau - test_a_before_dau) / test_a_before_dau) * 100
test_a_revenue_change = ((test_a_during_total_revenue - test_a_before_revenue) / test_a_before_revenue) * 100

test_c_dau_change = ((test_c_during_dau - test_c_before_dau) / test_c_before_dau) * 100
test_c_revenue_change = ((test_c_during_revenue - test_c_before_revenue) / test_c_before_revenue) * 100

# Net impacts
net_dau_impact = test_a_dau_change - test_c_dau_change
net_revenue_impact = test_a_revenue_change - test_c_revenue_change

# Create subplots
gs = fig.add_gridspec(3, 2, height_ratios=[1, 1, 0.8], hspace=0.3, wspace=0.25)

# Subplot 1: DAU Before vs During
ax1 = fig.add_subplot(gs[0, 0])
ax1.set_facecolor(cream)

groups = ['Test_A\n(RV)', 'Test_C\n(Control)']
before_dau = [test_a_before_dau, test_c_before_dau]
during_dau = [test_a_during_dau, test_c_during_dau]

x = np.arange(len(groups))
width = 0.35

bars1 = ax1.bar(x - width/2, before_dau, width, label='Before Test', color='#cccccc', alpha=0.8)
bars2 = ax1.bar(x + width/2, during_dau, width, label='During Test', 
                color=[test_a_color, test_c_color], alpha=0.8)

ax1.set_title('Daily Active Users: Before vs During Test\n(2-week periods)', fontsize=16, color='#2d2d2d', pad=20)
ax1.set_ylabel('Daily Active Users', fontsize=12, color='#444444')
ax1.grid(True, axis='y', color='#e0dbd5', linewidth=0.8, alpha=0.7)
ax1.legend(frameon=False, fontsize=10)

# Add value labels
for i, (before, during) in enumerate(zip(before_dau, during_dau)):
    ax1.text(i - width/2, before + 200, f'{before:,}', ha='center', va='bottom', fontweight='bold', fontsize=9)
    ax1.text(i + width/2, during + 200, f'{during:,}', ha='center', va='bottom', fontweight='bold', fontsize=9)

# Subplot 2: Revenue Before vs During
ax2 = fig.add_subplot(gs[0, 1])
ax2.set_facecolor(cream)

before_revenue = [test_a_before_revenue, test_c_before_revenue]
during_base_revenue = [test_a_during_base_revenue, test_c_during_revenue]
during_rv_revenue = [test_a_during_rv_revenue, 0]

bars1 = ax2.bar(x - width/2, before_revenue, width, label='Before Test', color='#cccccc', alpha=0.8)
bars2 = ax2.bar(x + width/2, during_base_revenue, width, label='Base Revenue (During)', 
                color=[test_a_color, test_c_color], alpha=0.8)
bars3 = ax2.bar(x + width/2, during_rv_revenue, width, bottom=during_base_revenue, 
                label='RV Revenue (During)', color='#59a14f', alpha=0.8)

ax2.set_title('Daily Revenue: Before vs During Test\n(Base + RV Revenue)', fontsize=16, color='#2d2d2d', pad=20)
ax2.set_ylabel('Daily Revenue ($)', fontsize=12, color='#444444')
ax2.grid(True, axis='y', color='#e0dbd5', linewidth=0.8, alpha=0.7)
ax2.legend(frameon=False, fontsize=10)

# Add value labels
for i, (before, base, rv) in enumerate(zip(before_revenue, during_base_revenue, during_rv_revenue)):
    total = base + rv
    ax2.text(i - width/2, before + 2, f'${before:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=9)
    ax2.text(i + width/2, total + 2, f'${total:.0f}', ha='center', va='bottom', fontweight='bold', fontsize=9)

# Subplot 3: Percentage Changes
ax3 = fig.add_subplot(gs[1, 0])
ax3.set_facecolor(cream)

change_categories = ['DAU Change %', 'Revenue Change %']
test_a_changes = [test_a_dau_change, test_a_revenue_change]
test_c_changes = [test_c_dau_change, test_c_revenue_change]

x_change = np.arange(len(change_categories))
bars1 = ax3.bar(x_change - width/2, test_a_changes, width, label='Test_A (RV)', 
                color=test_a_color, alpha=0.8)
bars2 = ax3.bar(x_change + width/2, test_c_changes, width, label='Test_C (Control)', 
                color=test_c_color, alpha=0.8)

ax3.set_title('Pre-Post Percentage Changes by Group\n((During - Before) / Before × 100)', 
              fontsize=16, color='#2d2d2d', pad=20)
ax3.set_ylabel('Percentage Change (%)', fontsize=12, color='#444444')
ax3.set_xticks(x_change)
ax3.set_xticklabels(change_categories)
ax3.grid(True, axis='y', color='#e0dbd5', linewidth=0.8, alpha=0.7)
ax3.legend(frameon=False, fontsize=10)
ax3.axhline(y=0, color='black', linewidth=1, alpha=0.5)

# Add value labels
for i, (test_a, test_c) in enumerate(zip(test_a_changes, test_c_changes)):
    ax3.text(i - width/2, test_a + (30 if test_a > 0 else -50), f'{test_a:.1f}%', 
             ha='center', va='bottom' if test_a > 0 else 'top', fontweight='bold', fontsize=9)
    ax3.text(i + width/2, test_c + (30 if test_c > 0 else -50), f'{test_c:.1f}%', 
             ha='center', va='bottom' if test_c > 0 else 'top', fontweight='bold', fontsize=9)

# Subplot 4: Net Impact (Difference Between Groups)
ax4 = fig.add_subplot(gs[1, 1])
ax4.set_facecolor(cream)

net_categories = ['DAU\nNet Impact', 'Revenue\nNet Impact']
net_impacts = [net_dau_impact, net_revenue_impact]
colors = ['#59a14f' if x > 0 else '#e15759' for x in net_impacts]

bars = ax4.bar(net_categories, net_impacts, color=colors, alpha=0.8, width=0.6)
ax4.set_title('Net RV Impact vs Control\n(Test_A Change - Test_C Change)', 
              fontsize=16, color='#2d2d2d', pad=20)
ax4.set_ylabel('Net Impact (%)', fontsize=12, color='#444444')
ax4.grid(True, axis='y', color='#e0dbd5', linewidth=0.8, alpha=0.7)
ax4.axhline(y=0, color='black', linewidth=1, alpha=0.5)

# Add value labels
for bar, value in zip(bars, net_impacts):
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height + (30 if height > 0 else -50),
             f'{value:.1f}%', ha='center', va='bottom' if height > 0 else 'top', 
             fontweight='bold', fontsize=11, color='#2d2d2d')

# Subplot 5: Calculation Details
ax5 = fig.add_subplot(gs[2, :])
ax5.set_facecolor(cream)
ax5.axis('off')

calculation_text = f"""
DETAILED CALCULATIONS - How Each Number Was Computed

RAW DATA (2-week averages):
• Test_A Before: {test_a_before_dau:,} DAU, ${test_a_before_revenue:.2f} revenue
• Test_A During: {test_a_during_dau:,} DAU, ${test_a_during_base_revenue:.2f} base + ${test_a_during_rv_revenue:.2f} RV = ${test_a_during_total_revenue:.2f} total
• Test_C Before: {test_c_before_dau:,} DAU, ${test_c_before_revenue:.2f} revenue  
• Test_C During: {test_c_during_dau:,} DAU, ${test_c_during_revenue:.2f} revenue

STEP 1 - Individual Group Changes:
• Test_A DAU Change = ({test_a_during_dau:,} - {test_a_before_dau:,}) ÷ {test_a_before_dau:,} × 100 = {test_a_dau_change:.2f}%
• Test_A Revenue Change = (${test_a_during_total_revenue:.2f} - ${test_a_before_revenue:.2f}) ÷ ${test_a_before_revenue:.2f} × 100 = {test_a_revenue_change:.1f}%
• Test_C DAU Change = ({test_c_during_dau:,} - {test_c_before_dau:,}) ÷ {test_c_before_dau:,} × 100 = {test_c_dau_change:.2f}%
• Test_C Revenue Change = (${test_c_during_revenue:.2f} - ${test_c_before_revenue:.2f}) ÷ ${test_c_before_revenue:.2f} × 100 = {test_c_revenue_change:.1f}%

STEP 2 - Net Impact (Test_A - Test_C):
• Net DAU Impact = {test_a_dau_change:.2f}% - ({test_c_dau_change:.2f}%) = {net_dau_impact:.2f}% (minimal additional decline from RV)
• Net Revenue Impact = {test_a_revenue_change:.1f}% - ({test_c_revenue_change:.1f}%) = {net_revenue_impact:.1f}% (massive incremental benefit from RV)

BUSINESS INTERPRETATION:
✓ RV causes only {abs(net_dau_impact):.1f}% additional DAU decline (minimal engagement cost)
✓ RV delivers {net_revenue_impact:.0f}% incremental revenue benefit (prevents revenue collapse + adds RV income)
✓ Strong case for DPU expansion: Huge revenue upside with minimal user impact
"""

ax5.text(0.02, 0.95, calculation_text, transform=ax5.transAxes, fontsize=10, 
         verticalalignment='top', color='#2d2d2d', fontweight='normal',
         bbox=dict(boxstyle="round,pad=0.5", facecolor='white', alpha=0.9))

# Remove spines for chart axes
for ax in [ax1, ax2, ax3, ax4]:
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cccccc')
    ax.spines['bottom'].set_color('#cccccc')
    ax.tick_params(length=0, colors='#444444', labelsize=10)

plt.savefig('c:/Users/mayed/OneDrive - Playtika Ltd/Desktop/My Cursor Projects/General -31.03/outputs/rv_dpu_performance_analysis_2026-06-08/files/prepost_analysis_detailed.png', 
            dpi=180, facecolor=cream, edgecolor='none', bbox_inches='tight')

print("+ Pre-Post Analysis charts created successfully")
print(f"+ Test_A DAU change: {test_a_dau_change:.2f}% | Test_C DAU change: {test_c_dau_change:.2f}%")
print(f"+ Test_A revenue change: {test_a_revenue_change:.1f}% | Test_C revenue change: {test_c_revenue_change:.1f}%")
print(f"+ Net DAU impact: {net_dau_impact:.2f}% | Net revenue impact: {net_revenue_impact:.1f}%")
print("+ Shows detailed calculations for each step of the analysis")