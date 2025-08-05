import os
import shutil

# Get the absolute path of the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define your source root directory
source_dirs = [
    os.path.join(script_dir, "full_contract_pdf/Part_I"),
    os.path.join(script_dir, "full_contract_pdf/Part_II"),
    os.path.join(script_dir, "full_contract_pdf/Part_III")
]

# Define your target folder where all PDFs will be moved
target_dir = os.path.join(script_dir, "..", "pdfs")



# Create target folder if it doesn't exist
os.makedirs(target_dir, exist_ok=True)

# Counter to prevent filename clashes
pdf_count = 1

for source_dir in source_dirs:
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith(".pdf"):
                src_path = os.path.normpath(os.path.join(root, file))
                # Rename to prevent duplicates (optional)
                new_filename = f"contract_{pdf_count}.pdf"
                dest_path = os.path.normpath(os.path.join(target_dir, new_filename))
                shutil.copy2(src_path, dest_path)
                pdf_count += 1

print(f"✅ Moved {pdf_count - 1} PDF files to: {target_dir}")
