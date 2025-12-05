# create_visuals.py
import matplotlib.pyplot as plt
from pathlib import Path

def save_plot(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()
