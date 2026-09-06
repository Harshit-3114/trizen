from fastapi import FastAPI

app = FastAPI(
    title="Photo Sharing Platform API",
    description="API for event photo sharing platform",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Photo Sharing Platform API"}
