from tensorflow.keras.models import load_model
import cv2
import numpy as np
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# Load model
model = load_model("xray_model.keras", compile=False)

IMG_SIZE = 224


def upload_xray():
    # Hide main tkinter window
    root = Tk()
    root.withdraw()

    file_path = askopenfilename(
        title="Select X-ray Image",
        filetypes=[("Image Files", "*.jpg *.jpeg *.png")]
    )

    return file_path


def predict_xray(image_path):

    img = cv2.imread(image_path)

    if img is None:
        return "IMAGE NOT FOUND"

    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
    img = img / 255.0
    img = np.expand_dims(img, axis=0)

    prediction = model.predict(img)
    print("Raw Prediction",prediction)

    confidence = float(prediction[0][0])

    if confidence > 0.5:
        result = "PNEUMONIA DETECTED"
        conf = confidence * 100
    else:
        result = "NORMAL"
        conf = (1 - confidence) * 100

    return f"{result} ({conf:.2f}% confidence)"