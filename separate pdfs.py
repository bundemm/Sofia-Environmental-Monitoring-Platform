from PyPDF2 import PdfReader, PdfWriter
import os

# =========================================================
# BASE DIRECTORY
# =========================================================
base_dir = os.path.dirname(os.path.abspath(__file__))

# Correct folders
folders = ["pm25", "pm10", "humidity"]

# =========================================================
# SPLIT FUNCTION
# =========================================================
def split_pdf(folder_name):
    folder_path = os.path.join(base_dir, folder_name)

    if not os.path.exists(folder_path):
        print(f"❌ Folder not found: {folder_path}")
        return

    # Find *_by_district.pdf
    pdf_files = [f for f in os.listdir(folder_path) if f.endswith("_by_district.pdf")]

    if not pdf_files:
        print(f"⚠️ No *_by_district.pdf found in {folder_name}")
        return

    pdf_file = pdf_files[0]
    pdf_path = os.path.join(folder_path, pdf_file)

    print(f"📄 Processing: {pdf_path}")

    reader = PdfReader(pdf_path)
    base_name = os.path.splitext(pdf_file)[0]

    # Split pages
    for i, page in enumerate(reader.pages):
        writer = PdfWriter()
        writer.add_page(page)

        output_filename = f"{base_name}_page_{i+1:03d}.pdf"
        output_path = os.path.join(folder_path, output_filename)

        with open(output_path, "wb") as f:
            writer.write(f)

    print(f"✅ {folder_name}: {len(reader.pages)} pages created\n")


# =========================================================
# RUN
# =========================================================
for folder in folders:
    split_pdf(folder)

print("🎯 DONE splitting all PDFs!")