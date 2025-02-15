import nest_asyncio
import subprocess
import os
import requests
import json

from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Load API key from environment variable
token = os.environ.get("AIPROXY_TOKEN")
if not token:
    raise ValueError("Missing API key! Please set AIPROXY_TOKEN in your environment.")



app = FastAPI() 

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Task descriptions mapped to execution functions
TASK_MAP = {
    "A1": "Install uv and run datagen.py with user email",
    "A2": "Format /data/format.md using prettier@3.4.2",
    "A3": "Count the number of Wednesdays in /data/dates.txt and write to /data/dates-wednesdays.txt",
    "A4": "Sort contacts in /data/contacts.json by last_name, then first_name, and save to /data/contacts-sorted.json",
    "A5": "Extract first lines of the 10 most recent log files in /data/logs/ and write to /data/logs-recent.txt",
    "A6": "Extract H1 headings from Markdown files in /data/docs/ and create /data/docs/index.json",
    "A7": "Extract the sender’s email from /data/email.txt and write to /data/email-sender.txt",
    "A8": "Extract the credit card number from /data/credit-card.png using an LLM",
    "A9": "Find the most similar pair of comments in /data/comments.txt using embeddings",
    "A10": "Calculate total sales for 'Gold' tickets from /data/ticket-sales.db and write to /data/ticket-sales-gold.txt",
}

def interpret_task(task_description: str):
    """
    Use OpenAI's GPT to map the given task description to a predefined task.
    """
    if not token:
        raise HTTPException(status_code=500, detail="Missing API key for OpenAI")

    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {
        "model": "gpt-4",
        "messages": [{"role": "system", "content": f"Given the task: '{task_description}', match it to one of {TASK_MAP.keys()} and return the task ID only."}],
        "temperature": 0.2
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {response.text}")

    task_id = response.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
    return task_id if task_id in TASK_MAP else None

def execute_task(task_id: str):
    """
    Execute the appropriate command based on the identified task.
    """
    try:
        if task_id == "A1":
            email = "21f3000031@ds.study.iitm.ac.in"
            script_url = "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py"
            script_path = "datagen.py"

            commands = [
                "pip install --upgrade pip",
                "pip install Pillow",
                f"curl -s -o {script_path} {script_url}",
                f"chmod +x {script_path}",
                f"python3 {script_path} {email}"
            ]
        
        elif task_id == "A2":
            commands = ["npx prettier@3.4.2 --write /data/format.md"]
        
        elif task_id == "A3":
            commands = ["grep -i 'Wed' /data/dates.txt | wc -l > /data/dates-wednesdays.txt"]

        elif task_id == "A4":
            commands = ["jq 'sort_by(.last_name, .first_name)' /data/contacts.json > /data/contacts-sorted.json"]
        
        elif task_id == "A5":
            commands = ["ls -t /data/logs/*.log | head -10 | xargs -I {} head -n 1 {} > /data/logs-recent.txt"]
        
        elif task_id == "A6":
            commands = ["grep -h '^# ' /data/docs/*.md | awk '{print $0}' > /data/docs/index.json"]
        
        elif task_id == "A7":
            commands = ["grep -E -o '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}' /data/email.txt > /data/email-sender.txt"]
        
        elif task_id == "A8":
            return {"error": "LLM-based OCR for credit card extraction not implemented"}
        
        elif task_id == "A9":
            return {"error": "LLM-based comment similarity not implemented"}
        
        elif task_id == "A10":
            commands = ["sqlite3 /data/ticket-sales.db 'SELECT SUM(units * price) FROM tickets WHERE type=\"Gold\";' > /data/ticket-sales-gold.txt"]
        
        else:
            return {"error": "Task not implemented"}

        output = ""
        for cmd in commands:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            output += f"\nCommand: {cmd}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}\n"

            if result.returncode != 0:
                return {"error": output}

        return {"output": output}
    
    except Exception as e:
        return {"error": str(e)}

@app.post("/run")
def run(task: str = Query(..., description="Task description")):
    """
    Receives a task in plain English, maps it to an operation, and executes it.
    """
    task_id = interpret_task(task)
    if not task_id:
        raise HTTPException(status_code=400, detail="Unable to interpret task")

    return execute_task(task_id)

@app.get("/read")
def read_file(path: str = Query(..., description="Path to file")):
    """
    Reads a file and returns its contents.
    """
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    
    with open(path, "r") as file:
        return file.read()

if __name__ == "__main__":
    import uvicorn
    nest_asyncio.apply()  # Apply nest_asyncio to allow nested event loops
    uvicorn.run(app, host="0.0.0.0", port=8000)
