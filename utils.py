import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set global matplotlib style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8

# Corporate Color Palette (McKinsey/Deloitte aesthetic)
COLOR_PALETTE = {
    'primary': '#003366',       # Deep Navy
    'secondary': '#008080',     # Teal
    'accent': '#FF6F61',        # Coral Accent
    'dark': '#1F2937',          # Charcoal
    'light': '#F3F4F6',         # Light Gray
    'gradient': ['#003366', '#005580', '#008080', '#2E8B57', '#20B2AA'],
    'diverging': ['#003366', '#4A90E2', '#E5E7EB', '#FF6F61', '#D0021B']
}


def auto_load_dataset(filepath: str) -> pd.DataFrame:
    """Automatically detects and loads dataset based on file extension."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext in ['.csv']:
        return pd.read_csv(filepath)
    elif ext in ['.xlsx', '.xls']:
        return pd.read_excel(filepath)
    elif ext in ['.json']:
        return pd.read_json(filepath)
    else:
        # Fallback try CSV
        try:
            return pd.read_csv(filepath)
        except Exception as e:
            raise ValueError(f"Unsupported file format: {ext}. Error: {e}")


def generate_overview_report(df: pd.DataFrame, filepath: str) -> dict:
    """Generates Phase 1 Dataset Overview metrics."""
    memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
    overview = {
        'filepath': filepath,
        'format': os.path.splitext(filepath)[1].upper().replace('.', ''),
        'shape': df.shape,
        'num_rows': df.shape[0],
        'num_cols': df.shape[1],
        'memory_usage_mb': round(memory_mb, 4),
        'columns': list(df.columns),
        'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
        'head_10': df.head(10).to_dict(orient='records'),
        'tail_10': df.tail(10).to_dict(orient='records')
    }
    return overview


def save_figure(fig, filename: str, output_dir: str = 'visuals', dpi: int = 300):
    """Saves a matplotlib/seaborn figure at publication quality (300 DPI)."""
    os.makedirs(output_dir, exist_ok=True)
    full_path = os.path.join(output_dir, filename)
    fig.tight_layout()
    fig.savefig(full_path, dpi=dpi, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return full_path
