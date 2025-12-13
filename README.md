# 🚧 Vision-Based Intelligent Transportation System  
## Deep Learning Based- Automated Pothole Detection and Alert System

A full-stack AI-powered system for **real-time pothole detection**, **road condition monitoring**, and **visual analytics**, built using **YOLO deep learning**, **FastAPI**, **React**, and **Supabase**.

This project detects potholes from video streams, stores geo-tagged detections, and visualizes them on an interactive dashboard.

---

## 📌 Features

### 🔍 AI-Based Detection
- YOLO-based pothole detection model
- Processes videos or live camera feeds
- Saves **combined annotated frames** (not cropped snippets)
- Intelligent storage with **15-second time-gap filtering**

### 🌐 Backend (FastAPI)
- REST APIs for:
  - Authentication
  - Recent detections
  - Dashboard analytics
  - Image uploads
- YOLO inference engine
- Supabase integration for:
  - Database
  - Image storage
- Background video processing thread

### 🎨 Frontend (React + TypeScript)
- Secure Login & Register (real users)
- Dashboard with:
  - Detection statistics
  - Confidence scores
- Recent detections (real-time Supabase data)
- Map visualization (Mapbox)
- Image preview from Supabase Storage

### ☁️ Cloud & Storage
- Supabase PostgreSQL database
- Supabase Storage bucket for detection images
- Public image URLs generation

---

## 🏗️ Tech Stack

### 🧠 AI / ML
- YOLO (PyTorch)
- OpenCV
- NumPy

### ⚙️ Backend
- FastAPI
- Python 3.10+
- Uvicorn
- Supabase (supabase-py)

### 🖥️ Frontend
- React
- TypeScript
- Vite
- Axios
- Mapbox GL JS

### 🗄️ Database & Storage
- Supabase PostgreSQL
- Supabase Storage Buckets

---

## 📁 Project Structure

pothole-system/
│
├── backend/
│ ├── app/
│ │ ├── main.py
│ │ ├── model_infer.py
│ │ ├── detection_worker.py
│ │ ├── supabase_client.py
│ │ └── auth.py
│ ├── pothole.pt
│ ├── requirements.txt
│ └── .env
│
├── frontend/
│ ├── src/
│ │ ├── pages/
│ │ ├── components/
│ │ ├── services/
│ │ └── App.tsx
│ ├── .env
│ └── package.json
│
└── README.md



---

## ⚙️ Environment Variables

### Backend `.env`
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_service_key
SUPABASE_BUCKET=detections
MODEL_PATH=pothole.pt

### Fronend '.env'
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_anon_key
VITE_MAPBOX_TOKEN=your_mapbox_token

🚀 Installation & Setup
1️⃣ Backend Setup
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload


Backend will run at:

http://127.0.0.1:8000

2️⃣ Frontend Setup
cd frontend
npm install
npm run dev


Frontend will run at:

http://localhost:5173

📡 API Endpoints
| Method | Endpoint                 | Description               |
| ------ | ------------------------ | ------------------------- |
| POST   | `/auth/login`            | User login                |
| POST   | `/auth/register`         | User registration         |
| GET    | `/api/recent-detections` | Latest pothole detections |
| GET    | `/api/dashboard`         | Analytics data            |
| POST   | `/api/report`            | Upload detection image    |


🧪 Detection Logic Highlights

Multiple potholes detected → single annotated image
Detection saved only if:
Confidence threshold met
Time gap > 15 seconds
GPS metadata stored with every detection

📊 Dashboard Metrics

Total potholes detected
High-risk potholes
Average confidence score
Location-based visualization

🔒 Authentication

Supabase Auth
JWT-based session handling
Secure API access

📸 Sample Output

Annotated detection images
Bounding boxes with confidence
Stored and served via Supabase Storage

🧠 Future Enhancements

Live camera feed support
Severity classification
Government/municipality dashboard
Mobile application
Road quality heatmaps

📜 License

This project is intended for academic and research purposes.
For commercial use, please contact the authors.

⭐ Acknowledgements

YOLO Community
Supabase
FastAPI
Mapbox
OpenCV
