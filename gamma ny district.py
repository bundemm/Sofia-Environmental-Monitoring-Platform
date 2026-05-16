import pandas as pd
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Image, PageBreak
from reportlab.lib.pagesizes import letter
import os
import matplotlib.colors as mcolors
import matplotlib.dates as mdates

# =========================================================
# PATH SETUP
# =========================================================
base_dir = os.path.dirname(os.path.abspath(__file__))

input_folder = os.path.join(base_dir, "Sofia")
output_folder = os.path.join(base_dir, "gamma")
temp_folder = os.path.join(output_folder, "temp_images")

csv_file = os.path.join(input_folder, "all_nodes_combined.csv")
district_pdf = os.path.join(output_folder, "gamma_by_district.pdf")

# Create folders
os.makedirs(output_folder, exist_ok=True)
os.makedirs(temp_folder, exist_ok=True)

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

# Clip extreme spikes (keeps plots readable)
df['gamma_cpm'] = df['gamma_cpm'].clip(upper=df['gamma_cpm'].quantile(0.98))
df['gamma_raw'] = df['gamma_raw'].clip(upper=df['gamma_raw'].quantile(0.98))

# =========================================================
# COLOR SYSTEM
# =========================================================
locations = sorted(df['neighbourhood'].unique())
cmap = plt.get_cmap('nipy_spectral')

def lighten(c): return [1 - (1 - x)*0.4 for x in mcolors.to_rgb(c)]
def darken(c): return [x*0.8 for x in mcolors.to_rgb(c)]

color_map = {loc: cmap(i/len(locations)) for i, loc in enumerate(locations)}

# =========================================================
# CREATE PDF
# =========================================================
doc = SimpleDocTemplate(district_pdf, pagesize=letter)
elements = []

for loc in locations:
    data = df[df['neighbourhood'] == loc].sort_values('timestamp')

    if data.empty:
        continue

    img_path = os.path.join(temp_folder, f"{loc}.png")

    # =====================================================
    # PLOT (clean + readable)
    # =====================================================
    fig, (ax1, ax2) = plt.subplots(
        2, 1,
        figsize=(12, 5),
        sharex=True
    )

    base = color_map[loc]

    # CPM
    ax1.plot(data['timestamp'], data['gamma_cpm'],
             linewidth=0.4,
             color=lighten(base))
    ax1.set_ylabel("CPM")
    ax1.grid(True, alpha=0.2)

    # RAW
    ax2.plot(data['timestamp'], data['gamma_raw'],
             linewidth=0.4,
             color=darken(base))
    ax2.set_ylabel("RAW")
    ax2.grid(True, alpha=0.2)

    # X-axis formatting
    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.setp(ax2.get_xticklabels(), rotation=30, ha='right')

    plt.tight_layout(pad=0.8)
    plt.savefig(img_path, dpi=300)
    plt.close()

    # =====================================================
    # ADD TO PDF
    # =====================================================
    img = Image(img_path)
    img.drawWidth = 500
    img.drawHeight = img.imageHeight * (500 / img.imageWidth)

    elements.append(img)
    elements.append(PageBreak())

# Build PDF
doc.build(elements)

# Cleanup temp images
for f in os.listdir(temp_folder):
    os.remove(os.path.join(temp_folder, f))

os.rmdir(temp_folder)

# =========================================================
# DONE
# =========================================================
print("✅ Gamma district PDF created successfully!")
print("📄 Output:", district_pdf)