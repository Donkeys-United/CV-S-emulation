from ultralytics import YOLO
from pathlib import Path, PurePath

current_dir = Path(__file__).parent.resolve()
cv_model_path = current_dir / "models" / "yolov8m_best.engine"
validation_data = current_dir / "kaggle-ships-in-google-earth-3" / "data.yaml"

model = YOLO(cv_model_path)

validation_results = model.val(data=validation_data, imgsz=640, device="0", plots=True)
print(validation_results.box.map)
print(validation_results.box.map50)
print(validation_results.box.map75)
print(validation_results.box.maps)