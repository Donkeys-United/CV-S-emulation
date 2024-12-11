from ultralytics import YOLO
from pathlib import Path

current_dir = Path(__file__).parent.resolve()
pt_model_path = current_dir / "models" / "yolov8m_best.pt"

model = YOLO(pt_model_path)
model.export(format="engine")
