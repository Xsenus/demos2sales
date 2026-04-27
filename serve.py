import os
import runpy
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)
os.environ.setdefault("DEMO_CALC_BASE_DIR", str(BASE_DIR))

try:
    runpy.run_path(str(BASE_DIR / "irbistech_demo_sales_premiums_colab_v6_5_sql(1).py"), run_name="__main__")
except KeyboardInterrupt:
    raise SystemExit(0) from None
