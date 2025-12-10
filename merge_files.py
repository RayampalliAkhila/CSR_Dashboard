import os
import pandas as pd

DATA_DIR = "data"
OUTPUT_FILE = "merged_csr_data.csv"

def clean_and_merge_excel(file_path):
    """Reads all sheets in an Excel file and standardizes them."""
    company_name = os.path.basename(file_path).split("_CSR_Report")[0]
    xls = pd.ExcelFile(file_path)
    merged = []

    for sheet in xls.sheet_names:
        try:
            df = pd.read_excel(xls, sheet_name=sheet, skiprows=1)
            df.columns = [
                "S.No", "Project", "Sector", "State", "District",
                "Budget_Outlay_Cr", "Amount_Spent_Cr", "Implementation_Mode"
            ]
            df["Year"] = sheet
            df["Company"] = company_name
            merged.append(df)
        except Exception as e:
            print(f"⚠️ Skipping sheet {sheet} in {company_name} — {e}")

    return pd.concat(merged, ignore_index=True)


def main():
    all_data = []

    for file in os.listdir(DATA_DIR):
        if file.endswith(".xlsx"):
            print(f"📄 Processing {file}...")
            df = clean_and_merge_excel(os.path.join(DATA_DIR, file))
            all_data.append(df)

    master_df = pd.concat(all_data, ignore_index=True)
    master_df.to_csv(OUTPUT_FILE, index=False)
    print(f"\n✅ All data merged successfully into '{OUTPUT_FILE}'")


if __name__ == "__main__":
    main()
