import pandas as pd
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Image, PageBreak
from reportlab.lib.pagesizes import letter
import os
import matplotlib.colors as mcolors
import matplotlib.dates as mdates

# =========================================================
# CLEAN STYLE
# =========================================================
plt.rcParams.update({
    'font.size': 7,
    'axes.labelsize': 7,
    'xtick.labelsize': 7,
    'ytick.labelsize': 7,
    'legend.fontsize': 6
})

# =========================================================
# PATH SETUP
# =========================================================
base_dir = os.path.dirname(os.path.abspath(__file__))
csv_file = os.path.join(base_dir, "all_nodes_combined.csv")

output_folder = os.path.join(base_dir, "gamma")
temp_folder = os.path.join(output_folder, "temp_images")

if os.path.exists(output_folder) and not os.path.isdir(output_folder):
    os.rename(output_folder, output_folder + "_old")

os.makedirs(output_folder, exist_ok=True)
os.makedirs(temp_folder, exist_ok=True)

main_pdf = os.path.join(output_folder, "gamma_overview.pdf")

# =========================================================
# LOAD DATA
# =========================================================
df = pd.read_csv(csv_file, low_memory=False)
df.columns = df.columns.str.strip().str.lower()

df['timestamp'] = pd.to_datetime(df['time'], errors='coerce')
df['gamma_cpm'] = pd.to_numeric(df['gamma_cpm'], errors='coerce')
df['gamma_raw'] = pd.to_numeric(df['gamma_raw'], errors='coerce')
df['neighbourhood'] = df['location']

df = df.dropna(subset=['timestamp', 'gamma_cpm', 'gamma_raw'])
df['date'] = df['timestamp'].dt.date

# Clip spikes
df['gamma_cpm'] = df['gamma_cpm'].clip(upper=df['gamma_cpm'].quantile(0.98))
df['gamma_raw'] = df['gamma_raw'].clip(upper=df['gamma_raw'].quantile(0.98))

# =========================================================
# COLORS
# =========================================================
neighbourhoods = sorted(df['neighbourhood'].unique())
cmap = plt.get_cmap('nipy_spectral')

def lighten(c): return [1 - (1 - x)*0.4 for x in mcolors.to_rgb(c)]
def darken(c): return [x*0.8 for x in mcolors.to_rgb(c)]

colors = {n: cmap(i/len(neighbourhoods)) for i,n in enumerate(neighbourhoods)}

# =========================================================
# PLOT (FIXED SIZE)
# =========================================================
main_img = os.path.join(temp_folder, "main_plot.png")

fig, (ax1, ax2) = plt.subplots(
    2, 1,
    figsize=(12, 5),   # ✅ WIDE + SHORT (KEY FIX)
    sharex=True
)

# CPM
for name, g in df.groupby('neighbourhood'):
    ax1.plot(g['timestamp'], g['gamma_cpm'],
             linewidth=0.4,
             color=lighten(colors[name]),
             label=name.replace("Sofia_", ""))

ax1.set_ylabel("CPM")
ax1.grid(True, alpha=0.2)

# RAW
for name, g in df.groupby('neighbourhood'):
    ax2.plot(g['timestamp'], g['gamma_raw'],
             linewidth=0.4,
             color=darken(colors[name]))

ax2.set_ylabel("RAW")
ax2.grid(True, alpha=0.2)

# X axis formatting
ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.setp(ax2.get_xticklabels(), rotation=30, ha='right')

# =========================================================
# LEGEND OUTSIDE (CRITICAL)
# =========================================================
ax1.legend(
    loc='center left',
    bbox_to_anchor=(1.01, 0.5),
    frameon=False
)

# Adjust layout for legend space
plt.tight_layout(rect=[0, 0, 0.85, 1])

plt.savefig(main_img, dpi=300)
plt.close()

# =========================================================
# PDF EXPORT
# =========================================================
doc = SimpleDocTemplate(main_pdf, pagesize=letter)

img = Image(main_img)
img.drawWidth = 500
img.drawHeight = img.imageHeight * (500 / img.imageWidth)

doc.build([img])

print("✅ CLEAN LEGEND-BASED PLOT READY!")