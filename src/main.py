"""
Ponto de entrada principal do projeto Deadlock Analytics.
Executa o pipeline orquestrado em src/pipelines/run_pipeline.py.
"""
import sys
from pathlib import Path

# Garante que a pasta src esteja no sys.path
SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from pipelines.run_pipeline import run_full_pipeline

if __name__ == "__main__":
    run_full_pipeline()

