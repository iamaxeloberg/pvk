"""Generate test financial documents for the ingestion pipeline."""
import csv
import struct
import textwrap
from pathlib import Path

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

OUT = Path("data/input")
OUT.mkdir(parents=True, exist_ok=True)


# ── 1. CSV – quarterly income statement ──────────────────────────────────────
csv_rows = [
    ["Acme Corp – Quarterly Income Statement"],
    [],
    ["", "Q1 2023", "Q2 2023", "Q3 2023", "Q4 2023", "FY 2023"],
    ["Revenue", 12_400_000, 13_100_000, 14_200_000, 16_800_000, 56_500_000],
    ["Cost of Revenue", 5_580_000, 5_895_000, 6_390_000, 7_560_000, 25_425_000],
    ["Gross Profit", 6_820_000, 7_205_000, 7_810_000, 9_240_000, 31_075_000],
    ["Gross Margin %", "55.0%", "55.0%", "55.0%", "55.0%", "55.0%"],
    [],
    ["Operating Expenses"],
    ["  R&D", 1_860_000, 1_965_000, 2_130_000, 2_520_000, 8_475_000],
    ["  Sales & Marketing", 2_480_000, 2_620_000, 2_840_000, 3_360_000, 11_300_000],
    ["  General & Administrative", 620_000, 655_000, 710_000, 840_000, 2_825_000],
    ["Total OpEx", 4_960_000, 5_240_000, 5_680_000, 6_720_000, 22_600_000],
    [],
    ["EBIT", 1_860_000, 1_965_000, 2_130_000, 2_520_000, 8_475_000],
    ["EBIT Margin %", "15.0%", "15.0%", "15.0%", "15.0%", "15.0%"],
    ["Net Interest Expense", -124_000, -131_000, -142_000, -168_000, -565_000],
    ["Pre-tax Income", 1_736_000, 1_834_000, 1_988_000, 2_352_000, 7_910_000],
    ["Income Tax (25%)", -434_000, -458_500, -497_000, -588_000, -1_977_500],
    ["Net Income", 1_302_000, 1_375_500, 1_491_000, 1_764_000, 5_932_500],
    ["EPS (diluted)", 0.43, 0.46, 0.50, 0.59, 1.98],
]

with open(OUT / "acme_income_statement_2023.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(csv_rows)

print("Created acme_income_statement_2023.csv")


# ── 2. Excel – balance sheet + KPI summary ───────────────────────────────────
wb = openpyxl.Workbook()

# Sheet 1: Balance Sheet
ws1 = wb.active
ws1.title = "Balance Sheet"

header_font = Font(bold=True, color="FFFFFF")
header_fill = PatternFill("solid", fgColor="1F4E79")
subheader_fill = PatternFill("solid", fgColor="BDD7EE")

def header(ws, row, col, text):
    c = ws.cell(row=row, column=col, value=text)
    c.font = header_font
    c.fill = header_fill
    c.alignment = Alignment(horizontal="center")

header(ws1, 1, 1, "Acme Corp – Balance Sheet (USD)")
header(ws1, 1, 2, "FY 2022")
header(ws1, 1, 3, "FY 2023")

bs_data = [
    ("ASSETS", None, None),
    ("Current Assets", None, None),
    ("  Cash & Equivalents", 8_200_000, 11_500_000),
    ("  Accounts Receivable", 4_100_000, 5_650_000),
    ("  Inventory", 2_300_000, 2_800_000),
    ("  Other Current Assets", 900_000, 1_050_000),
    ("Total Current Assets", 15_500_000, 21_000_000),
    ("Non-Current Assets", None, None),
    ("  PP&E (net)", 18_000_000, 19_500_000),
    ("  Intangibles & Goodwill", 6_500_000, 6_100_000),
    ("  Right-of-Use Assets", 2_200_000, 2_050_000),
    ("Total Non-Current Assets", 26_700_000, 27_650_000),
    ("TOTAL ASSETS", 42_200_000, 48_650_000),
    ("", None, None),
    ("LIABILITIES & EQUITY", None, None),
    ("Current Liabilities", None, None),
    ("  Accounts Payable", 3_100_000, 3_800_000),
    ("  Short-term Debt", 1_500_000, 1_200_000),
    ("  Accrued Liabilities", 2_400_000, 2_900_000),
    ("Total Current Liabilities", 7_000_000, 7_900_000),
    ("Non-Current Liabilities", None, None),
    ("  Long-term Debt", 10_000_000, 9_000_000),
    ("  Deferred Tax Liabilities", 1_200_000, 1_350_000),
    ("Total Non-Current Liabilities", 11_200_000, 10_350_000),
    ("TOTAL LIABILITIES", 18_200_000, 18_250_000),
    ("Shareholders' Equity", None, None),
    ("  Common Stock & APIC", 12_000_000, 12_000_000),
    ("  Retained Earnings", 12_000_000, 18_400_000),
    ("TOTAL EQUITY", 24_000_000, 30_400_000),
    ("TOTAL LIABILITIES & EQUITY", 42_200_000, 48_650_000),
]

for i, (label, fy22, fy23) in enumerate(bs_data, start=2):
    ws1.cell(row=i, column=1, value=label)
    if fy22 is not None:
        ws1.cell(row=i, column=2, value=fy22).number_format = '#,##0'
    if fy23 is not None:
        ws1.cell(row=i, column=3, value=fy23).number_format = '#,##0'

ws1.column_dimensions["A"].width = 36
ws1.column_dimensions["B"].width = 18
ws1.column_dimensions["C"].width = 18

# Sheet 2: KPI Summary
ws2 = wb.create_sheet("KPI Summary")
header(ws2, 1, 1, "KPI")
header(ws2, 1, 2, "FY 2021")
header(ws2, 1, 3, "FY 2022")
header(ws2, 1, 4, "FY 2023")
header(ws2, 1, 5, "YoY Change")

kpis = [
    ("Revenue (USD)", 44_800_000, 50_200_000, 56_500_000, "12.5%"),
    ("Revenue Growth", "—", "12.1%", "12.5%", "+0.4pp"),
    ("Gross Margin", "54.2%", "54.8%", "55.0%", "+0.2pp"),
    ("EBIT Margin", "13.5%", "14.2%", "15.0%", "+0.8pp"),
    ("Net Margin", "9.8%", "10.5%", "10.5%", "0.0pp"),
    ("EPS (diluted)", 1.46, 1.68, 1.98, "+$0.30"),
    ("Return on Equity", "18.2%", "20.1%", "21.8%", "+1.7pp"),
    ("Return on Assets", "9.8%", "11.2%", "13.0%", "+1.8pp"),
    ("Debt / Equity", 0.76, 0.64, 0.53, "-0.11"),
    ("Current Ratio", 2.05, 2.21, 2.66, "+0.45"),
    ("Free Cash Flow (USD)", 6_100_000, 7_400_000, 9_200_000, "+24.3%"),
    ("Employees (FTE)", 1_820, 2_045, 2_310, "+265"),
    ("Revenue per Employee (USD)", 24_615, 24_548, 24_458, "-$90"),
]

for i, row in enumerate(kpis, start=2):
    for j, val in enumerate(row, start=1):
        ws2.cell(row=i, column=j, value=val)

for col in ["A", "B", "C", "D", "E"]:
    ws2.column_dimensions[col].width = 26

wb.save(OUT / "acme_financials_2023.xlsx")
print("Created acme_financials_2023.xlsx")


# ── 3. Minimal valid PDF – Annual Report narrative ────────────────────────────
narrative = textwrap.dedent("""\
    Acme Corp Annual Report 2023

    Dear Shareholders,

    We are pleased to report a strong fiscal year 2023. Total revenue reached USD 56.5 million,
    representing 12.5% year-over-year growth. Our gross margin expanded 20 basis points to 55.0%,
    reflecting disciplined pricing and supply-chain optimisation.

    EBIT grew to USD 8.5 million (15.0% margin), up from 14.2% in FY 2022. Net income of
    USD 5.9 million translated to diluted EPS of USD 1.98, a 17.9% increase. Free cash flow
    of USD 9.2 million allowed us to reduce long-term debt by USD 1 million while growing
    the cash balance to USD 11.5 million.

    Key Operational Highlights
    - Launched next-generation product line in Q2, contributing 18% of H2 revenue.
    - Expanded into three new geographies, adding 215 enterprise customers.
    - Headcount grew to 2,310 FTEs; R&D investment increased 14% YoY.
    - Net Promoter Score improved from 42 to 51.

    Outlook for FY 2024
    Management guides for revenue of USD 63-66 million (11-17% growth) and EBIT margin of
    15.5-16.5%. Capital expenditure is expected at USD 3.5 million, focused on automation
    and cloud infrastructure.

    We remain committed to sustainable, profitable growth and creating long-term value for
    all stakeholders.

    Board of Directors, Acme Corp
""")

# Build a minimal but valid PDF without external libraries
lines = narrative.split("\n")

# Encode text drawing commands
stream_lines = ["BT", "/F1 11 Tf", "50 750 Td", "14 TL"]
for line in lines:
    safe = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    stream_lines.append(f"({safe}) Tj T*")
stream_lines.append("ET")
stream_body = "\n".join(stream_lines).encode("latin-1")

font_obj = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>"
catalog   = b"<< /Type /Catalog /Pages 2 0 R >>"
pages     = b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>"
page      = (
    b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
    b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>"
)
content   = b"<< /Length " + str(len(stream_body)).encode() + b" >>\nstream\n" + stream_body + b"\nendstream"

objects = [catalog, pages, page, content, font_obj]
pdf = bytearray(b"%PDF-1.4\n")
offsets = []
for i, obj in enumerate(objects, start=1):
    offsets.append(len(pdf))
    pdf += f"{i} 0 obj\n".encode()
    pdf += obj + b"\nendobj\n"

xref_offset = len(pdf)
pdf += b"xref\n"
pdf += f"0 {len(objects)+1}\n".encode()
pdf += b"0000000000 65535 f \n"
for off in offsets:
    pdf += f"{off:010d} 00000 n \n".encode()

pdf += b"trailer\n"
pdf += f"<< /Size {len(objects)+1} /Root 1 0 R >>\n".encode()
pdf += b"startxref\n"
pdf += f"{xref_offset}\n".encode()
pdf += b"%%EOF\n"

(OUT / "acme_annual_report_2023.pdf").write_bytes(bytes(pdf))
print("Created acme_annual_report_2023.pdf")
print("\nAll test files written to data/input/")
