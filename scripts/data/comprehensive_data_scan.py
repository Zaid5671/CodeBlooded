import os
import glob
import json
import numpy as np
import pandas as pd
from datetime import datetime

def analyze_dataset(file_path):
    print(f"Scanning: {file_path}")
    try:
        df = pd.read_csv(file_path, low_memory=False)
    except Exception as e:
        return {"error": str(e), "file_path": file_path}

    total_rows = len(df)
    total_cols = len(df.columns)

    exact_duplicates = int(df.duplicated().sum())
    exact_dup_pct = round((exact_duplicates / total_rows * 100.0), 2) if total_rows > 0 else 0.0

    norm_path = file_path.replace("\\", "/")
    filename = os.path.basename(file_path)

    if "LokSabha17" in norm_path or "LokSabha_17" in filename:
        chamber = "Lok Sabha"
        term = "17th Lok Sabha (2019-2024)"
    elif "LokSabha18" in norm_path or "LokSabha_18" in filename:
        chamber = "Lok Sabha"
        term = "18th Lok Sabha (2024-Present)"
    elif "RajyaSabha" in norm_path or "Rajya" in filename:
        chamber = "Rajya Sabha"
        term = "Sitting Members (Continuous House)"
    else:
        chamber = "Unknown"
        term = "Unknown"

    grain = "UNKNOWN"
    if "Allocated Limit" in filename or "Allocated_Limit" in filename:
        grain = "ONE ROW = ONE MP / CONSTITUENCY ALLOCATION RECORD"
    elif "Amount consented" in filename or "Amount_consented" in filename:
        grain = "ONE ROW = ONE CALAMITY RELIEF CONSENT EVENT"
    elif "Works Recommended" in filename or "Works_Recommended" in filename:
        grain = "ONE ROW = ONE WORK RECOMMENDATION PROPOSAL"
    elif "Works Sanctioned" in filename or "Works_Sanctioned" in filename:
        grain = "ONE ROW = ONE SANCTIONED WORK / PROJECT ENTITY"
    elif "Works Completed" in filename or "Works_Completed" in filename:
        grain = "ONE ROW = ONE COMPLETED WORK RECORD"
    elif "Expenditure on Completed" in filename or "Expenditure_on_Completed" in filename:
        grain = "ONE ROW = ONE EXPENDITURE / PAYMENT TRANSACTION RECORD"

    work_id_cols = [c for c in df.columns if any(k in c.lower() for k in ['work id', 'workid', 'work_id', 'work code'])]
    work_num_cols = [c for c in df.columns if any(k in c.lower() for k in ['work number', 'work no', 'work_no', 'work_number'])]
    mp_cols = [c for c in df.columns if any(k in c.lower() for k in ['mp name', 'honble mp', 'mp_name', 'member'])]
    constituency_cols = [c for c in df.columns if any(k in c.lower() for k in ['constituency', 'pc name', 'pc_name'])]
    state_cols = [c for c in df.columns if any(k in c.lower() for k in ['state'])]
    district_cols = [c for c in df.columns if any(k in c.lower() for k in ['district', 'ida'])]
    agency_cols = [c for c in df.columns if any(k in c.lower() for k in ['agency', 'implementing'])]
    vendor_cols = [c for c in df.columns if any(k in c.lower() for k in ['vendor', 'contractor', 'payee'])]
    amount_cols = [c for c in df.columns if any(k in c.lower() for k in ['amount', 'cost', 'limit', 'fund'])]
    date_cols = [c for c in df.columns if any(k in c.lower() for k in ['date', 'time', 'dt'])]
    status_cols = [c for c in df.columns if any(k in c.lower() for k in ['status'])]

    col_profiles = {}
    for col in df.columns:
        s = df[col]
        null_cnt = int(s.isnull().sum())
        null_pct = round((null_cnt / total_rows * 100.0), 2) if total_rows > 0 else 0.0
        unique_cnt = int(s.nunique(dropna=True))

        numeric_s = pd.to_numeric(s.astype(str).str.replace(',', '').str.strip(), errors='coerce')
        is_num = (numeric_s.notnull().sum() / max(1, (total_rows - null_cnt))) > 0.8 if (total_rows - null_cnt) > 0 else False

        is_dt = False
        date_min, date_max, date_unique = None, None, None
        if not is_num and any(k in col.lower() for k in ['date', 'dt', 'time']):
            try:
                dt_series = pd.to_datetime(s, format='%d/%m/%Y', errors='coerce')
                if dt_series.notnull().sum() == 0:
                    dt_series = pd.to_datetime(s, errors='coerce')
                if dt_series.notnull().sum() > 0:
                    is_dt = True
                    date_min = str(dt_series.min())
                    date_max = str(dt_series.max())
                    date_unique = int(dt_series.nunique(dropna=True))
            except Exception:
                pass

        stat_dict = {
            "name": col,
            "data_type": str(s.dtype),
            "null_count": null_cnt,
            "null_percentage": null_pct,
            "unique_count": unique_cnt
        }

        if is_dt and date_min is not None:
            stat_dict["type_category"] = "DATE"
            stat_dict["min_date"] = date_min
            stat_dict["max_date"] = date_max
            stat_dict["unique_dates"] = date_unique
        elif is_num and numeric_s.notnull().sum() > 0:
            num_clean = numeric_s.dropna()
            stat_dict["type_category"] = "NUMERIC"
            stat_dict["numeric_count"] = int(len(num_clean))
            stat_dict["min"] = float(num_clean.min())
            stat_dict["max"] = float(num_clean.max())
            stat_dict["mean"] = float(round(num_clean.mean(), 2))
            stat_dict["median"] = float(round(num_clean.median(), 2))
            stat_dict["std"] = float(round(num_clean.std(), 2)) if len(num_clean) > 1 else 0.0
            q1 = float(round(num_clean.quantile(0.25), 2))
            q3 = float(round(num_clean.quantile(0.75), 2))
            stat_dict["q1"] = q1
            stat_dict["q3"] = q3
            stat_dict["iqr"] = float(round(q3 - q1, 2))
        else:
            stat_dict["type_category"] = "CATEGORICAL"
            top_vals = s.value_counts(dropna=True).head(5)
            stat_dict["top_values"] = [
                {"value": str(k), "count": int(v), "percentage": round(v / total_rows * 100.0, 2)}
                for k, v in top_vals.items()
            ]

        col_profiles[col] = stat_dict

    id_analyses = {}
    for id_col in work_id_cols + work_num_cols:
        s_id = df[id_col].dropna()
        tot_id = len(s_id)
        uniq_id = s_id.nunique()
        dup_id = tot_id - uniq_id
        dup_pct = round(dup_id / tot_id * 100.0, 2) if tot_id > 0 else 0.0
        id_analyses[id_col] = {
            "total_present": tot_id,
            "unique_count": uniq_id,
            "duplicate_count": dup_id,
            "duplicate_percentage": dup_pct
        }

    return {
        "file_path": file_path,
        "filename": filename,
        "file_size_bytes": os.path.getsize(file_path),
        "chamber": chamber,
        "term": term,
        "record_grain": grain,
        "row_count": total_rows,
        "column_count": total_cols,
        "exact_duplicate_rows": exact_duplicates,
        "exact_duplicate_percentage": exact_dup_pct,
        "column_names": list(df.columns),
        "semantic_fields": {
            "work_id_fields": work_id_cols,
            "work_number_fields": work_num_cols,
            "mp_fields": mp_cols,
            "constituency_fields": constituency_cols,
            "state_fields": state_cols,
            "district_fields": district_cols,
            "agency_fields": agency_cols,
            "vendor_fields": vendor_cols,
            "amount_fields": amount_cols,
            "date_fields": date_cols,
            "status_fields": status_cols
        },
        "identifier_analyses": id_analyses,
        "columns": col_profiles
    }

def main():
    os.makedirs("output", exist_ok=True)
    all_files = sorted(glob.glob("data/original/**/*.csv", recursive=True))
    print(f"Discovered {len(all_files)} CSV files.")

    results = []
    for f in all_files:
        res = analyze_dataset(f)
        results.append(res)

    with open("output/FULL_DATASET_SCAN.json", "w", encoding="utf-8") as f_out:
        json.dump(results, f_out, indent=2)
    print("Wrote output/FULL_DATASET_SCAN.json")

    md = []
    md.append("# FULL REAL-DATA INVENTORY & STATISTICAL SCAN REPORT")
    md.append(f"**Generated At**: {datetime.now().isoformat()} | **Total Structured Files Scanned**: {len(results)}\n")
    md.append("## Executive Summary of Scanned Datasets\n")
    md.append("| # | Dataset File | Chamber / Term | Record Grain | Rows | Cols | Dupl Rows (%) | Work ID / Key Fields |")
    md.append("|---|---|---|---|---:|---:|---:|---|")

    total_all_rows = 0
    chamber_rows = {"Lok Sabha": 0, "Rajya Sabha": 0}

    for idx, r in enumerate(results, 1):
        if "error" in r:
            md.append(f"| {idx} | `{r['filename']}` | ERROR | ERROR | - | - | - | {r['error']} |")
            continue
        total_all_rows += r["row_count"]
        chamber_rows[r["chamber"]] = chamber_rows.get(r["chamber"], 0) + r["row_count"]
        key_fields = ", ".join(r["semantic_fields"]["work_id_fields"] + r["semantic_fields"]["work_number_fields"] + r["semantic_fields"]["mp_fields"][:1])
        md.append(f"| {idx} | `{r['filename']}` | {r['term']} | {r['record_grain']} | {r['row_count']:,} | {r['column_count']} | {r['exact_duplicate_rows']:,} ({r['exact_duplicate_percentage']}%) | {key_fields} |")

    md.append(f"\n**Total Real Data Records Scanned Across All Files**: **{total_all_rows:,} rows**\n")
    md.append(f"- **Lok Sabha Total Rows**: {chamber_rows.get('Lok Sabha', 0):,}")
    md.append(f"- **Rajya Sabha Total Rows**: {chamber_rows.get('Rajya Sabha', 0):,}\n")

    md.append("## Detailed File-by-File Statistical Profile\n")
    for idx, r in enumerate(results, 1):
        if "error" in r:
            continue
        md.append(f"### {idx}. `{r['filename']}`")
        md.append(f"- **File Path**: `{r['file_path']}`")
        md.append(f"- **Chamber**: {r['chamber']} | **Term**: {r['term']}")
        md.append(f"- **Record Grain**: `{r['record_grain']}`")
        md.append(f"- **Dimensions**: {r['row_count']:,} rows × {r['column_count']} columns | Size: {r['file_size_bytes']:,} bytes")
        md.append(f"- **Exact Duplicate Rows**: {r['exact_duplicate_rows']:,} ({r['exact_duplicate_percentage']}%)")

        if r["identifier_analyses"]:
            md.append("- **Identifier Uniqueness**:")
            for id_col, id_info in r["identifier_analyses"].items():
                md.append(f"  - `{id_col}`: {id_info['unique_count']:,} unique out of {id_info['total_present']:,} records ({id_info['duplicate_count']:,} duplicates, {id_info['duplicate_percentage']}%)")

        md.append("\n#### Column Schema & Statistics\n")
        md.append("| Column Name | Type | Category | Null Count (%) | Summary Statistics / Distribution |")
        md.append("|---|---|---|---:|---|")

        for col_name, c in r["columns"].items():
            cat = c.get("type_category", "UNKNOWN")
            null_str = f"{c['null_count']:,} ({c['null_percentage']}%)"
            if cat == "NUMERIC":
                detail = f"Min: {c['min']}, Max: {c['max']}, Mean: {c['mean']}, Median: {c['median']}, IQR: {c['iqr']} (Q1: {c['q1']}, Q3: {c['q3']})"
            elif cat == "DATE":
                detail = f"Min Date: {c['min_date']}, Max Date: {c['max_date']}, Unique Dates: {c['unique_dates']:,}"
            else:
                top_items = [f"{t['value']} ({t['count']:,})" for t in c.get("top_values", [])[:3]]
                detail = f"{c['unique_count']:,} unique. Top: " + "; ".join(top_items)
            md.append(f"| `{col_name}` | `{c['data_type']}` | `{cat}` | {null_str} | {detail} |")
        md.append("\n---\n")

    with open("output/FULL_DATASET_SCAN.md", "w", encoding="utf-8") as f_md:
        f_md.write("\n".join(md))
    print("Wrote output/FULL_DATASET_SCAN.md")

if __name__ == '__main__':
    main()
