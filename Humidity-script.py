import pandas as pd
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Image, PageBreak
from reportlab.lib.pagesizes import letter
import os

# =========================================================
# PATH SETUP
# =========================================================
base_dir = os.path.dirname(os.path.abspath(__file__))

csv_file = os.path.join(base_dir, "all_nodes_combined.csv")

output_folder = os.path.join(base_dir, "humidity")
temp_folder = os.path.join(output_folder, "temp_images")

# Fix if "humidity" exists as file
if os.path.exists(output_folder) and not os.path.isdir(output_folder):
    os.rename(output_folder, output_folder + "_old")

os.makedirs(output_folder, exist_ok=True)
os.makedirs(temp_folder, exist_ok=True)

main_pdf = os.path.join(output_folder, "humidity_overview.pdf")
district_pdf = os.path.join(output_folder, "humidity_by_district.pdf")

# =========================================================
# LOAD & CLEAN DATA
# =========================================================
df = pd.read_csv(csv_file, low_memory=False)

df.columns = df.columns.str.strip().str.lower()

# Your actual column names (from your data)
df['timestamp'] = pd.to_datetime(df['time'], errors='coerce')
df['humidity'] = pd.to_numeric(df['relative humidity'], errors='coerce')
df['neighbourhood'] = df['location']

df = df.dropna(subset=['timestamp', 'humidity'])
df['date'] = df['timestamp'].dt.date

# =========================================================
# COLOR SYSTEM (CONSISTENT EVERYWHERE)
# =========================================================
neighbourhoods = sorted(df['neighbourhood'].unique())

# Better palette for many lines
cmap = plt.get_cmap('nipy_spectral')

color_map = {
    name: cmap(i / len(neighbourhoods))
    for i, name in enumerate(neighbourhoods)
}

# =========================================================
# DAILY GLOBAL AVERAGE
# =========================================================
daily_avg = df.groupby('date')['humidity'].mean().reset_index()

# =========================================================
# 1️⃣ MAIN PLOT (COLORED + CONSISTENT)
# =========================================================
main_img = os.path.join(temp_folder, "main_plot.png")

plt.figure(figsize=(14, 7))

for name, group in df.groupby('neighbourhood'):
    group = group.sort_values('timestamp')
    plt.plot(
        group['timestamp'],
        group['humidity'],
        linewidth=0.4,
        color=color_map[name]
    )

# Thick black average line
plt.plot(
    daily_avg['date'],
    daily_avg['humidity'],
    color='black',
    linewidth=3,
    label='Daily Average'
)

plt.title("Humidity Across All Sofia Locations")
plt.xlabel("Time")
plt.ylabel("Humidity")
plt.grid(True)

# Optional legend (can be huge!)
# plt.legend()

plt.tight_layout()
plt.savefig(main_img, dpi=300)
plt.close()

doc = SimpleDocTemplate(main_pdf, pagesize=letter)
doc.build([Image(main_img, width=520, height=320)])

# =========================================================
# 2️⃣ DISTRICT PDF (MATCHING COLORS)
# =========================================================
doc2 = SimpleDocTemplate(district_pdf, pagesize=letter)
elements = []

for name, group in df.groupby('neighbourhood'):
    group = group.sort_values('timestamp')
    daily_local = group.groupby('date')['humidity'].mean().reset_index()

    img_path = os.path.join(temp_folder, f"{str(name)}.png")

    plt.figure(figsize=(12, 5))
    plt.plot(
        daily_local['date'],
        daily_local['humidity'],
        linewidth=2.2,
        color=color_map[name]   # SAME COLOR AS MAIN
    )

    plt.title(f"Annual Humidity - {name}")
    plt.xlabel("Date")
    plt.ylabel("Humidity")
    plt.grid(True)

    plt.tight_layout()
    plt.savefig(img_path, dpi=300)
    plt.close()

    elements.append(Image(img_path, width=520, height=300))
    elements.append(PageBreak())

doc2.build(elements)

# =========================================================
# CLEANUP
# =========================================================
for file in os.listdir(temp_folder):
    os.remove(os.path.join(temp_folder, file))

os.rmdir(temp_folder)

# =========================================================
# DONE
# =========================================================
print("✅ DONE!")
print("📁 Output folder:", output_folder)