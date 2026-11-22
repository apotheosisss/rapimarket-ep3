"""Ejecuta la solución completa desde cero, en orden.

    python codigo_y_data/run_all.py        (desde la raíz del proyecto)

1. Pipeline de datos (Fase 1)          -> data/processed, resultados/calidad_*.csv
2. Auditoría A1-A6, Simpson y modelo   -> resultados/, figuras/
3. Informe ejecutivo y presentación    -> informes/, presentacion/ (PDF si hay Edge o Chrome)
4. PDF del guion y evidencias en papel -> guion_y_papel/
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src import pipeline, auditoria, documentos, guion_pdf  # noqa: E402

if __name__ == "__main__":
    for paso, mod in [("1/4 Pipeline", pipeline), ("2/4 Auditoría", auditoria),
                      ("3/4 Informe y presentación", documentos), ("4/4 Guion y evidencias", guion_pdf)]:
        print(f"\n=== {paso} ===")
        mod.main()
    print("\nListo. Abre el dashboard con:  streamlit run dashboard/app.py")
