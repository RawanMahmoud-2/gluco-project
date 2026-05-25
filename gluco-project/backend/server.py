from fastapi import FastAPI, Request

app = FastAPI()

latest_ppg = None


@app.post("/upload")
async def upload(request: Request):

    global latest_ppg

    data = await request.json()
    latest_ppg = data.get("ppg", [])

    print("Received:", len(latest_ppg))

    return {"status": "ACK"}


@app.get("/data")
def get_data():
    return {"ppg": latest_ppg}