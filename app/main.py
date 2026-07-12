from fastapi import FastAPI

app = FastAPI()


@app.get("/projects")
def get_projects():
    return {"projects": "None"}