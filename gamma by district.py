import pandas as pd
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Image, PageBreak
from reportlab.lib.pagesizes import letter
import os
import matplotlib.colors as mcolors

# =========================================================
# PATH SETUP
# =========================================================
base_dir = os.path.dirname(os.path.abspath(__file__))
csv_file = os.path.join(base_dir, "all_nodes_combined.csv")

output_root = os.path.join(base_dir, "gamma")
images_folder = os.path.join(output_root, "gamma_by_district")
pdf_path = os.path.join(output_root, "gamma_by_district.pdf")

os.makedirs(images_folder, exist_ok=True)

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

# Clean spikes
df['gamma_cpm'] = df['gamma_cpm'].clip(upper=df['gamma_cpm'].quantile(0.98))
df['gamma_raw'] = df['gamma_raw'].clip(upper=df['gamma_raw'].quantile(0.98))

locations = sorted(df['neighbourhood'].unique())

# =========================================================
# COLORS
# =========================================================
cmap = plt.get_cmap('tab20')

def lighten(c): return [1 - (1 - x)*0.4 for x in mcolors.to_rgb(c)]
def darken(c): return [x*0.8 for x in mcolors.to_rgb(c)]

color_map = {loc: cmap(i/len(locations)) for i, loc in enumerate(locations)}

# =========================================================
# CREATE PDF
# =========================================================
doc = SimpleDocTemplate(pdf_path, pagesize=letter)
elements = []

for loc in locations:
    data = df[df['neighbourhood'] == loc].sort_values('timestamp')

    if data.empty:
        continue

    data = data.iloc[::5]

    safe_name = loc.replace(" ", "_").replace("/", "_")
    img_path = os.path.join(images_folder, f"{safe_name}.png")

    base_color = color_map[loc]

    fig, (ax1, ax2) = plt.subplots(
        2, 1,
        figsize=(12, 4),
        sharex=True
    )

    start = data['timestamp'].min().date()
    end = data['timestamp'].max().date()

    base_label = f"{loc.replace('Sofia_', '')} | {start} → {end}"

    # CPM
    line1, = ax1.plot(
        data['timestamp'], data['gamma_cpm'],
        color=lighten(base_color),
        linewidth=0.25,
        alpha=0.8
    )

    # RAW
    line2, = ax2.plot(
        data['timestamp'], data['gamma_raw'],
        color=darken(base_color),
        linewidth=0.25,
        alpha=0.8
    )

    # Remove all text
    ax1.set_title("")
    ax2.set_title("")
    ax1.set_ylabel("")
    ax2.set_ylabel("")
    ax1.set_xlabel("")
    ax2.set_xlabel("")
    ax2.set_xticks([])

    ax1.grid(True, alpha=0.15)
    ax2.grid(True, alpha=0.15)

    # =====================================================
    # LEGEND (BOTH CPM + RAW)
    # =====================================================
    legend = ax1.legend(
        [line1, line2],
        [f"{base_label} (CPM)", f"{base_label} (RAW)"],
        loc='center left',
        bbox_to_anchor=(1.02, 0.5),
        frameon=False
    )

    # Make legend lines visible
    for l in legend.get_lines():
        l.set_linewidth(1.5)

    plt.tight_layout(rect=[0, 0, 0.85, 1])
    plt.savefig(img_path, dpi=300)
    plt.close()

    # Add to PDF
    img = Image(img_path)
    img.drawWidth = 520
    img.drawHeight = img.imageHeight * (520 / img.imageWidth)

    elements.append(img)
    elements.append(PageBreak())

doc.build(elements)

print("✅ FINAL VERSION WITH CPM + RAW LEGEND READY!")
print("📁 Images:", images_folder)
print("📄 PDF:", pdf_path)