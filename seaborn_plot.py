import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Rectangle
from matplotlib.transforms import blended_transform_factory

# Set font size
plt.rcParams['font.size'] = 14

# Read the data
df = pd.read_csv('outputs/tables/table_5_proportion_cycle_access.csv')

# Remove the Total row
df = df[df['Municipality'] != 'Total'].reset_index(drop=True)

# Reverse the order for plotting
df = df.iloc[::-1].reset_index(drop=True)

# Create the figure
fig, ax = plt.subplots(figsize=(12, 7))

# Add background colors based on comfort level
colors = {'high': '#c8e6c9', 'medium': '#fff9c4', 'low': '#ffcccc'}

# Create blended transform for x in axes coords, y in data coords
trans = blended_transform_factory(ax.transAxes, ax.transData)

# Plot the grey connecting lines
for idx, row in df.iterrows():
    ax.plot([row['% nearby access 2019'], row['% nearby access 2024']], [idx, idx], 
            color='#e8e8e8', linewidth=5, zorder=1)

# Plot the 2019 dots (light blue)
ax.scatter(df['% nearby access 2019'], range(len(df)), 
          color='#4A90E2', s=100, zorder=2, label='2019')

# Plot the 2024 dots (dark navy)
ax.scatter(df['% nearby access 2024'], range(len(df)), 
          color='#001F3F', s=100, zorder=2, label='2024')

# Add population labels on the right
for idx, row in df.iterrows():
    pop_text = f"{int(row['Population (2021)']):,}"
    ax.text(102, idx, pop_text, 
            va='center', fontsize=11, alpha=0.7)

# Add labels to the axes
ax.text(102, len(df) - 0.2, 'Population (2021)', 
        fontsize=11, alpha=0.7, weight='bold')

# Set y-axis labels to municipality names
ax.set_yticks(range(len(df)))
ax.set_yticklabels(df['Municipality'])

# Set x-axis to 0-100 with 10 unit intervals, but extend left for dot padding
ax.set_xlim(-5, 100)
ax.set_xticks(range(0, 101, 10))

# Labels and legend
ax.set_xlabel('% Population Within 300m of High Comfort Infrastructure', labelpad=15)
ax.legend(loc='upper right')

# Clean up
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.grid(axis='y', alpha=1, linestyle='-', linewidth=0.8, color='#e8e8e8')
ax.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.subplots_adjust(left=0.15, right=0.75)
plt.savefig('outputs/figures/figure_2.png', dpi=300, bbox_inches='tight')
plt.show()
