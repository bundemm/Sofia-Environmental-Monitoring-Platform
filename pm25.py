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

output_folder = os.path.join(base_dir, "pm25")
temp_folder = os.path.join(output_folder, "temp_images")

# Fix if folder exists as file
if os.path.exists(output_folder) and not os.path.isdir(output_folder):
    os.rename(output_folder, output_folder + "_old")

os.makedirs(output_folder, exist_ok=True)
os.makedirs(temp_folder, exist_ok=True)

main_pdf = os.path.join(output_folder, "pm25_overview.pdf")
district_pdf = os.path.join(output_folder, "pm25_by_district.pdf")

# =========================================================
# LOAD DATA
# =========================================================
df = pd.read_csv(csv_file, low_memory=False)

df.columns = df.columns.str.strip().str.lower()

# Extract relevant columns
df['timestamp'] = pd.to_datetime(df['time'], errors='coerce')
df['value'] = pd.to_numeric(df['pm2.5'], errors='coerce')
df['neighbourhood'] = df['location']

df = df.dropna(subset=['timestamp', 'value'])
df['date'] = df['timestamp'].dt.date

# =========================================================
# COLOR SYSTEM (CONSISTENT)
# =========================================================
neighbourhoods = sorted(df['neighbourhood'].unique())

cmap = plt.get_cmap('nipy_spectral')

color_map = {
    name: cmap(i / len(neighbourhoods))
    for i, name in enumerate(neighbourhoods)
}

# =========================================================
# DAILY GLOBAL AVERAGE
# =========================================================
daily_avg = df.groupby('date')['value'].mean().reset_index()

# =========================================================
# 1️⃣ MAIN PLOT
# =========================================================
main_img = os.path.join(temp_folder, "main_plot.png")

plt.figure(figsize=(14, 7))

for name, group in df.groupby('neighbourhood'):
    group = group.sort_values('timestamp')
    plt.plot(
        group['timestamp'],
        group['value'],
        linewidth=0.4,
        color=color_map[name]
    )

# Thick black daily average
plt.plot(
    daily_avg['date'],
    daily_avg['value'],
    color='black',
    linewidth=3
)

plt.title("PM2.5 Across All Sofia Locations")
plt.xlabel("Time")
plt.ylabel("PM2.5")
plt.grid(True)

plt.tight_layout()
plt.savefig(main_img, dpi=300)
plt.close()

doc = SimpleDocTemplate(main_pdf, pagesize=letter)
doc.build([Image(main_img, width=520, height=320)])

# =========================================================
# 2️⃣ DISTRICT PDF
# =========================================================
doc2 = SimpleDocTemplate(district_pdf, pagesize=letter)
elements = []

for name, group in df.groupby('neighbourhood'):
    group = group.sort_values('timestamp')

    daily_local = group.groupby('date')['value'].mean().reset_index()

    img_path = os.path.join(temp_folder, f"{str(name)}.png")

    plt.figure(figsize=(12, 5))
    plt.plot(
        daily_local['date'],
        daily_local['value'],
        linewidth=2.2,
        color=color_map[name]
    )

    plt.title(f"Annual PM2.5 - {name}")
    plt.xlabel("Date")
    plt.ylabel("PM2.5")
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
print("✅ PM2.5 DONE!")
print("📁 Output folder:", output_folder)