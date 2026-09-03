from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Voice AI API is running"}