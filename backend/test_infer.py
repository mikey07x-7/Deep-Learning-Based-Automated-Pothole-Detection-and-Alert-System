# test_infer.py
from app.model_infer import PotholeModel
import cv2
import sys

TEST_IMAGE = "test.jpg"   # put any jpg in backend folder and rename to test.jpg

m = PotholeModel()
print("Model loaded:", type(m.model))

img = cv2.imread(TEST_IMAGE)
if img is None:
    print(f"ERROR: test image {TEST_IMAGE} not found.")
    sys.exit(1)

detections = m.infer_frame(img)
print("Detections:", detections)
