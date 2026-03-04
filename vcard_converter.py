import pandas as pd

INPUT_FILE  = "newcomers_final.xlsx"
PHONE_FILE  = "newcomers_phone.xlsx"
OUTPUT_VCF  = "newcomers.vcf"

def excel_to_vcf(excel_file, output_file):
    df = pd.read_excel(excel_file)
    with open(output_file, 'w') as f:
        for _, row in df.iterrows():
            f.write('BEGIN:VCARD\n')
            f.write(f'FN:{row["Name"]}\n')
            f.write(f'TEL:{row["Phone Number"]}\n')
            f.write('END:VCARD\n')
    print(f"✅ VCF created: {output_file} ({len(df)} contacts)")

def create_phone_xlsx_and_vcf():
    df = pd.read_excel(INPUT_FILE, usecols=["Name", "Phone Number"])
    df.to_excel(PHONE_FILE, index=False)
    print(f"✅ Phone list saved: {PHONE_FILE}")
    excel_to_vcf(PHONE_FILE, OUTPUT_VCF)

if __name__ == "__main__":
    create_phone_xlsx_and_vcf()
