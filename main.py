import os
from uuid import uuid4
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from concurrent.futures import ThreadPoolExecutor
from image_processing import generate_image
from ad_template import create_ad_template

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Welcome to the API. Use the appropriate endpoints for specific functionalities."}

executor = ThreadPoolExecutor(max_workers=3)  # Adjust the number of workers as needed
tasks = {}  # Dictionary to keep track of tasks

def process_image(image_path, logo_path, text_prompt, hex_color, punchline_and_button_color_hex, punchline_text, button_text):
    # Generate the enhanced or modified image
    result_image = generate_image(image_path, text_prompt, hex_color)
    result_image_path = "output/generated_image.png"
    result_image.save(result_image_path)

    # Create the advertisement template
    ad_image = create_ad_template(result_image_path, logo_path, punchline_and_button_color_hex, punchline_text, button_text)
    ad_image_path = "output/ad_template.png"
    ad_image.save(ad_image_path)

    return ad_image_path  # Return the path of the ad image

@app.post("/generate-ad/")
async def generate_ad(image: UploadFile = File(...), 
                      logo: UploadFile = File(...), 
                      text_prompt: str = Form(...), 
                      hex_color: str = Form(...), 
                      punchline_and_button_color_hex: str = Form(...), 
                      punchline_text: str = Form(...), 
                      button_text: str = Form(...)):
    image_path = f"temp/{image.filename}"
    logo_path = f"temp/{logo.filename}"
    
    with open(image_path, "wb") as buffer:
        buffer.write(await image.read())
    with open(logo_path, "wb") as buffer:
        buffer.write(await logo.read())

    # Generate a unique task ID and submit the task to the executor
    task_id = str(uuid4())
    future = executor.submit(process_image, image_path, logo_path, text_prompt, hex_color, punchline_and_button_color_hex, punchline_text, button_text)
    tasks[task_id] = future

    return {"task_id": task_id}

@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    if task_id in tasks:
        if tasks[task_id].done():
            return {"status": "completed"}
        return {"status": "processing"}
    return {"status": "invalid task id"}

@app.get("/download/{task_id}")
async def download_image(task_id: str):
    if task_id in tasks and tasks[task_id].done():
        ad_image_path = tasks[task_id].result()
        return FileResponse(ad_image_path)
    return {"status": "processing or invalid task id"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
