# How to Fix 'ModuleNotFoundError: No module named data_pipeline' in Google Colab

The error `ModuleNotFoundError: No module named 'data_pipeline'` occurs because Google Colab's Python interpreter does not know where your Python project source files are located until you extract/link the code repository and set `sys.path`.

---

## ⚡ The 2-Step Fix

### Step 1: Upload your Project ZIP File into Colab
1. On your computer, zip your project folder into a `.zip` file (e.g. `CodeBlooded.zip`).
2. Open **Google Colab**.
3. Click the **Folder Icon (Files tab)** on the left sidebar.
4. Drag and drop `CodeBlooded.zip` into the file area.

---

### Step 2: Add & Run Cell 1 (Environment Setup & Path Resolution)

Create a new Code Cell at the **very top** of your notebook, paste this code, and click **Run** (`Shift + Enter`):

```python
# ==============================================================================
# CELL 1: SETUP PIPELINE & RESOLVE 'data_pipeline' PATH (RUN FIRST!)
# ==============================================================================
import os, sys, glob, shutil

print("🔧 Setting up Python environment...")

# 1. Navigate into project directory if already extracted
if not os.path.exists("data_pipeline"):
    possible_dirs = [d for d in os.listdir("/content") if os.path.isdir(os.path.join("/content", d)) and os.path.exists(os.path.join("/content", d, "data_pipeline"))]
    if possible_dirs:
        os.chdir(os.path.join("/content", possible_dirs[0]))
        print(f"📁 Navigated into project directory: {os.getcwd()}")
    else:
        # Check if a zip file was uploaded to /content
        zip_files = glob.glob("/content/*.zip") + glob.glob("*.zip")
        if zip_files:
            import zipfile
            print(f"📦 Extracting project zip: {zip_files[0]}...")
            with zipfile.ZipFile(zip_files[0], 'r') as zip_ref:
                zip_ref.extractall("/content")
            
            # Re-check directory after unzipping
            possible_dirs = [d for d in os.listdir("/content") if os.path.isdir(os.path.join("/content", d)) and os.path.exists(os.path.join("/content", d, "data_pipeline"))]
            if possible_dirs:
                os.chdir(os.path.join("/content", possible_dirs[0]))
            elif os.path.exists("/content/data_pipeline"):
                os.chdir("/content")
        else:
            print("🌐 Attempting to clone repository...")
            !git clone https://github.com/Zaid5671/CodeBlooded.git /content/CodeBlooded
            if os.path.exists("/content/CodeBlooded/data_pipeline"):
                os.chdir("/content/CodeBlooded")

# 2. Add current working directory to Python path
cwd = os.getcwd()
if cwd not in sys.path:
    sys.path.insert(0, cwd)
os.environ["PYTHONPATH"] = cwd

print("--------------------------------------------------------------------------------")
print("📍 Working Directory:", os.getcwd())
print("✅ 'data_pipeline' Available:", os.path.exists("data_pipeline"))
print("✅ 'unified_model_engine.py' Available:", os.path.exists("unified_model_engine.py"))
print("--------------------------------------------------------------------------------")

if not os.path.exists("data_pipeline"):
    print("⚠️ WARNING: 'data_pipeline' folder not found yet!")
    print("👉 Please upload your CodeBlooded.zip file to Colab's left sidebar, then run this cell again!")
else:
    print("🎉 SUCCESS! You can now run any model cell below without errors.")
```

---

### Step 3: Run Model M1 (Now Works Without Error!)

Now run your Model M1 code cell:

```python
import pandas as pd
from data_pipeline.data_loader import load_sanctioned_works
from feature_engineering.preprocessing import preprocess_sanctioned_works
from feature_engineering.category_classifier import apply_category_classification
from ml.model_1_cost_anomaly.overrun_rules import evaluate_cost_overrun
from ml.model_1_cost_anomaly.peer_analysis import evaluate_peer_iqr
from ml.model_1_cost_anomaly.isolation_forest import train_and_score_isolation_forest

print("=== TESTING MODEL M1 COST ANOMALY ENGINE ===")
df_raw = load_sanctioned_works()
df_prep = preprocess_sanctioned_works(df_raw)
df_cat = apply_category_classification(df_prep)
df_s1 = evaluate_cost_overrun(df_cat)
df_s2 = evaluate_peer_iqr(df_s1)
df_m1, imputer, iso_model = train_and_score_isolation_forest(df_s2)

print(f"Total Works Analyzed: {len(df_m1):,}")
print(f"Isolation Forest Cost Anomalies: {df_m1['isolation_forest_flag'].sum():,}")
```
