"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
from pymongo import MongoClient

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['mergington_high']
activities_collection = db['activities']

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# Initial activities data
initial_activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in local leagues",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
    },
    "Basketball Club": {
        "description": "Practice basketball skills and play friendly matches",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["liam@mergington.edu", "ava@mergington.edu"]
    },
    "Drama Club": {
        "description": "Participate in theater productions and acting workshops",
        "schedule": "Mondays, 4:00 PM - 5:30 PM",
        "max_participants": 25,
        "participants": ["noah@mergington.edu", "isabella@mergington.edu"]
    },
    "Art Workshop": {
        "description": "Explore painting, drawing, and other visual arts",
        "schedule": "Fridays, 2:00 PM - 3:30 PM",
        "max_participants": 20,
        "participants": ["amelia@mergington.edu", "benjamin@mergington.edu"]
    },
    "Math Olympiad": {
        "description": "Prepare for math competitions and solve challenging problems",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["elijah@mergington.edu", "charlotte@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 14,
        "participants": ["james@mergington.edu", "harper@mergington.edu"]
    }
}


@app.on_event("startup")
async def startup_event():
    # Clear existing data
    activities_collection.drop()
    
    # Insert initial activities
    for name, details in initial_activities.items():
        activities_collection.insert_one({"name": name, **details})


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    # Convert MongoDB cursor to dictionary with activity names as keys
    activities = {}
    for activity in activities_collection.find({}, {'_id': 0}):
        name = activity.pop('name')
        activities[name] = activity
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Find the activity
    activity = activities_collection.find_one({"name": activity_name})
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student already signed up")
    
    # Add student to participants
    result = activities_collection.update_one(
        {"name": activity_name},
        {"$push": {"participants": email}}
    )
    
    if result.modified_count == 1:
        return {"message": f"Signed up {email} for {activity_name}"}
    else:
        raise HTTPException(status_code=500, detail="Failed to update activity")


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Find the activity
    activity = activities_collection.find_one({"name": activity_name})
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    if email not in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student not registered")
    
    # Remove student from participants
    result = activities_collection.update_one(
        {"name": activity_name},
        {"$pull": {"participants": email}}
    )
    
    if result.modified_count == 1:
        return {"message": f"Unregistered {email} from {activity_name}"}
    else:
        raise HTTPException(status_code=500, detail="Failed to update activity")
