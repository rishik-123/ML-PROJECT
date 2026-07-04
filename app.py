import streamlit as st
from xray_predictor import predict_xray
from PIL import Image
import tempfile
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

LOGO_PATH = r"C:\Users\Abcom\OneDrive\Desktop\PYTHON AND ML\VIRTUAL KEYBOARD\logo img.jpeg"

st.set_page_config(page_title="MediScan X", page_icon="🩻", layout="wide")

# ---------- CSS ----------
st.markdown("""
<style>
.main-title{
    text-align:center;
    font-size:55px;
    font-weight:800;
    font-style:italic;
    color:#0B3C5D;
}
.card{
    background:white;
    padding:30px;
    border-radius:15px;
    box-shadow:0 0 20px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# ---------- SESSION ----------
if "page" not in st.session_state:
    st.session_state.page = "home"
if "users" not in st.session_state:
    st.session_state.users = {}

def go(page):
    st.session_state.page = page
    st.rerun()

# ---------- REPORT ----------
def generate_report(user, patient, result, photo_path):
    pdf_path = "MediScanX_Report.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()
    flow = []

    flow.append(RLImage(LOGO_PATH, width=200, height=120))
    flow.append(Paragraph("<b><font size=22>MediScan X - Xray Diagnosis Report</font></b>", styles['Title']))
    flow.append(Spacer(1, 20))

    flow.append(RLImage(photo_path, width=100, height=100))
    flow.append(Paragraph(f"<b>User:</b> {user['name']} | {user['email']}", styles['Normal']))
    flow.append(Spacer(1, 20))

    flow.append(Paragraph(f"<b><font size=16>Patient Name: {patient}</font></b>", styles['Normal']))
    flow.append(Spacer(1, 10))

    flow.append(Paragraph(f"<b>Model Result:</b> {result}", styles['Normal']))
    flow.append(Spacer(1, 10))

    flow.append(Paragraph("<b>Remedial Measures:</b> Consult physician, take medication, rest and hygiene.", styles['Normal']))
    flow.append(Spacer(1, 30))

    flow.append(Paragraph("<b>Tested by:</b>Rishik Jariwala", styles['Normal']))
    doc.build(flow)
    return pdf_path

# ---------- HOME ----------
def home():
    st.image(LOGO_PATH, width=300)
    st.markdown('<div class="main-title">MediScan X</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Login", use_container_width=True):
            go("login")
    with c2:
        if st.button("Sign Up", use_container_width=True):
            go("signup")

# ---------- SIGNUP ----------
def signup():
    st.markdown("### Create Account")

    name = st.text_input("Full Name")
    email = st.text_input("Email")
    pwd = st.text_input("Password", type="password")
    photo = st.file_uploader("Upload Profile Photo", type=["jpg","png"])

    if st.button("Create Account"):
        if email and pwd and photo:
            photo_path = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
            Image.open(photo).save(photo_path)

            st.session_state.users[email] = {
                "name": name,
                "email": email,
                "pwd": pwd,
                "photo": photo_path
            }
            st.success("Account created successfully!")

    st.markdown("---")
    if st.button("Go to Login", use_container_width=True):
        go("login")

# ---------- LOGIN ----------
def login():
    st.markdown("### Login")
    email = st.text_input("Email")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        user = st.session_state.users.get(email)
        if user and user["pwd"] == pwd:
            st.session_state.user = user
            go("instructions")
        else:
            st.error("Invalid credentials")

# ---------- INSTRUCTIONS ----------
def instructions():
    st.info("""
    📌 Upload X-ray image in JPG/PNG format.
    📌 Click Predict to analyze disease.
    📌 Result will appear in table below.
    """)
    if st.button("Proceed"):
        go("upload")

# ---------- UPLOAD ----------
def upload():
    st.markdown("### Upload X-ray")
    patient = st.text_input("Patient Name")
    file = st.file_uploader("Upload X-ray", type=["jpg","png","jpeg"])

    if file:
        img = Image.open(file)
        st.image(img, use_container_width=True)

        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        img.save(temp.name)

        # ---------- PREDICT ----------
        if st.button("Predict"):
            result = predict_xray(temp.name)

            # store in session
            st.session_state.result = result
            st.session_state.patient = patient
            st.session_state.xray_path = temp.name

        # ---------- SHOW RESULT IF AVAILABLE ----------
        if "result" in st.session_state:
            df = pd.DataFrame({
                "Patient Name": [st.session_state.patient],
                "Prediction Result": [st.session_state.result]
            })
            st.table(df)

            # ---------- REPORT BUTTON (separate) ----------
            if st.button("Generate Report"):
                pdf = generate_report(
                    st.session_state.user,
                    st.session_state.patient,
                    st.session_state.result,
                    st.session_state.user["photo"]
                )

                with open(pdf, "rb") as f:
                    st.download_button(
                        "Download Report",
                        f,
                        file_name="MediScanX_Report.pdf"
                    )
# ---------- ROUTING ----------
if st.session_state.page == "home":
    home()
elif st.session_state.page == "signup":
    signup()
elif st.session_state.page == "login":
    login()
elif st.session_state.page == "instructions":
    instructions()
elif st.session_state.page == "upload":
    upload()