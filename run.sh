# --- Face Detection Microservice (4000)---
cd face-detection-mcsv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python3 run.py


# --- Camera Microservice (6000) ---
python3 client-server.py


# --- Attendance Microservice (5000) ---
cd attendance-mcsv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

flask insert-db
flask run 


# --- Frontend Microservice (5173) ---
cd frontend
pnpm install
pnpm run dev