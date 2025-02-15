import subprocess
import os
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

def run_task(task: str):
    if task == "A1":
        email = "21f3000031@ds.study.iitm.ac.in"
        script_url = "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py"
        script_path = "datagen.py"

        commands = [
            "pip install --upgrade pip",  # Upgrade pip
            "pip install Pillow",  # Install dependencies
            f"curl -s -o {script_path} {script_url}",  # Download script
            f"chmod +x {script_path}",  # Make it executable
            f"python3 {script_path} {email}"  # Run script with email
        ]

        output = ""
        try:
            for cmd in commands:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                output += f"\nCommand: {cmd}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}\n"

                if result.returncode != 0:  # Stop if an error occurs
                    return {"error": output}

            return {"output": output}

        except Exception as e:
            return {"error": str(e)}

    else:
        return {"error": "Task not recognized"}

@app.get("/run")
def run(task: str = Query(..., description="Task to execute")):
    return run_task(task)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


