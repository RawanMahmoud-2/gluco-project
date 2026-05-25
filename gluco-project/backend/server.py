from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

latest_ppg = []

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Backend running"}

@app.post("/upload")
async def upload(request: Request):

    global latest_ppg

    data = await request.json()

    latest_ppg = data.get("ppg", [])

    print("Received samples:", len(latest_ppg))

    return {"status": "ACK"}

@app.get("/data")
def get_data():
    return {"ppg": latest_ppg}
