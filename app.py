import streamlit as st
from xray_predictor import predict_xray
from PIL import Image
import tempfile

st.title("AI X-ray Detection System")

user_name = st.text_input("Enter Patient Name")

uploaded_file = st.file_uploader("Upload X-ray Image", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:

    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded X-ray", use_container_width=True)

    temp_file = tempfile.NamedTemporaryFile(delete=False,suffix=".jpg")
    image.save(temp_file.name)

    if st.button("Predict"):

        result = predict_xray(temp_file.name)

        st.success(f"Patient: {user_name}")
        st.warning(f"Result: {result}")