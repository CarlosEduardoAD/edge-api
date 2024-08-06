import io

import aiohttp
import requests
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from replit import db
import uuid

URL = "https://api.limewire.com/api/image/generation"

class Prompt(BaseModel):
  prompt: str

app = FastAPI()

async def generate_image_task(prompt: str, task_id: str):
    api_payload = {"prompt": prompt, "aspect_ratio": "1:1"}
    headers = {
        "Content-Type": "application/json",
        "X-Api-Version": "v1",
        "Accept": "application/json",
        "Authorization": "Bearer lmwr_sk_pCeG6aGUyi_s5IYfYHnP6fSOwiIG593xfTFXt4dnPYtkl5wL"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(URL, json=api_payload, headers=headers) as response:
            if response.status != 200:
                db[task_id] = {"status": "failed", "result": None}
                return
                
            image_data = await response.json()
            db[task_id] = {"status": "completed", "result": image_data}

@app.post("/generate", response_model=dict)
async def generate(payload: Prompt, background_tasks: BackgroundTasks):
    if payload.prompt == "" or payload.prompt is None:
        raise HTTPException(status_code=400, detail="Prompt not informed")

    task_id = str(uuid.uuid4())
    db[task_id] = {"status": "processing", "result": None}
    background_tasks.add_task(generate_image_task, payload.prompt, task_id)
    return {"task_id": task_id, "status": "processing"}

@app.get("/generate/{task_id}", response_class=StreamingResponse)
async def get_generated_image(task_id: str):
    if db[task_id] is None:
        raise HTTPException(status_code=404, detail="Task ID not found")
    task_info = db[task_id]
    if task_info["status"] == "processing":
        return JSONResponse(content={"status": "processing"})
    elif task_info["status"] == "completed":
        return JSONResponse(content=task_info["result"])
    else:
        raise HTTPException(status_code=500, detail="Image generation failed")


@app.get("/")
async def main():
  test_response = requests.get("https://api.github.com")

  if test_response.status_code != 200:
    raise HTTPException(status_code=503, detail="Service Unavailable")

  return {"Status": "OK!"}


if __name__ == "__main__":
  import uvicorn
  uvicorn.run(app, host="0.0.0.0", port=8000)

