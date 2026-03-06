"""
Ocean Professional Recruitment System - Simplified API
No Docker required - Deploy to Render.com
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
import json

# Create app
app = FastAPI(
    title="Ocean Professional Recruitment API",
    version="1.0.0",
    description="Simple recruitment system - no Docker needed"
)

# Add CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (replace with database in production)
applicants_db = []
applications_db = []
users_db = [
    {
        "id": 1,
        "email": "admin@oceanprofessional.com",
        "password": "Admin@123456",
        "name": "Admin",
        "role": "admin"
    }
]

# Pydantic Models
class User(BaseModel):
    email: str
    password: str
    name: str

class Applicant(BaseModel):
    email: str
    first_name: str
    last_name: str
    phone_number: str
    nationality: str
    job_position: str

class Application(BaseModel):
    applicant_id: int
    job_position: str
    years_experience: int
    status: str = "submitted"

# Health Check
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

# Root
@app.get("/")
async def root():
    return {
        "message": "Ocean Professional Recruitment API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

# Authentication
@app.post("/auth/signup")
async def signup(user: User):
    """Create new user account"""
    # Check if user exists
    if any(u["email"] == user.email for u in users_db):
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create user
    new_user = {
        "id": len(users_db) + 1,
        "email": user.email,
        "password": user.password,
        "name": user.name,
        "role": "recruiter"
    }
    users_db.append(new_user)
    
    return {
        "status": "success",
        "message": "Account created",
        "user_id": new_user["id"],
        "email": new_user["email"]
    }

@app.post("/auth/login")
async def login(email: str, password: str):
    """Login user"""
    user = next((u for u in users_db if u["email"] == email and u["password"] == password), None)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {
        "status": "success",
        "message": "Login successful",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"]
        }
    }

# Applicants
@app.get("/api/v1/applicants")
async def get_applicants():
    """Get all applicants"""
    return {
        "status": "success",
        "total": len(applicants_db),
        "applicants": applicants_db
    }

@app.post("/api/v1/applicants")
async def create_applicant(applicant: Applicant):
    """Create new applicant"""
    # Check if email exists
    if any(a["email"] == applicant.email for a in applicants_db):
        raise HTTPException(status_code=400, detail="Email already exists")
    
    new_applicant = {
        "id": len(applicants_db) + 1,
        "email": applicant.email,
        "first_name": applicant.first_name,
        "last_name": applicant.last_name,
        "phone_number": applicant.phone_number,
        "nationality": applicant.nationality,
        "job_position": applicant.job_position,
        "status": "new",
        "created_at": datetime.now().isoformat(),
        "overall_score": 0,
        "documents": []
    }
    applicants_db.append(new_applicant)
    
    return {
        "status": "success",
        "message": "Application received",
        "applicant_id": new_applicant["id"],
        "email": new_applicant["email"]
    }

@app.get("/api/v1/applicants/{applicant_id}")
async def get_applicant(applicant_id: int):
    """Get specific applicant"""
    applicant = next((a for a in applicants_db if a["id"] == applicant_id), None)
    
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    
    return {
        "status": "success",
        "applicant": applicant
    }

@app.put("/api/v1/applicants/{applicant_id}")
async def update_applicant(applicant_id: int, data: dict):
    """Update applicant"""
    applicant = next((a for a in applicants_db if a["id"] == applicant_id), None)
    
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    
    # Update fields
    for key, value in data.items():
        if key in applicant:
            applicant[key] = value
    
    return {
        "status": "success",
        "message": "Applicant updated",
        "applicant": applicant
    }

# Applications
@app.get("/api/v1/applications")
async def get_applications():
    """Get all applications"""
    return {
        "status": "success",
        "total": len(applications_db),
        "applications": applications_db
    }

@app.post("/api/v1/applications")
async def create_application(app_data: Application):
    """Create new application"""
    new_application = {
        "id": len(applications_db) + 1,
        "applicant_id": app_data.applicant_id,
        "job_position": app_data.job_position,
        "years_experience": app_data.years_experience,
        "status": app_data.status,
        "screening_score": 0,
        "ai_recommendation": "pending",
        "created_at": datetime.now().isoformat()
    }
    applications_db.append(new_application)
    
    return {
        "status": "success",
        "message": "Application created",
        "application": new_application
    }

# Job Positions
job_positions = [
    {"id": 1, "title": "NDT Inspector", "description": "Experienced NDT Inspector"},
    {"id": 2, "title": "Offshore Technician", "description": "Skilled offshore technician"},
    {"id": 3, "title": "Rigger", "description": "Experienced rigger"},
    {"id": 4, "title": "Welder", "description": "Certified welder"},
    {"id": 5, "title": "Safety Officer", "description": "Safety officer"},
]

@app.get("/api/v1/job-positions")
async def get_job_positions():
    """Get all job positions"""
    return {
        "status": "success",
        "total": len(job_positions),
        "positions": job_positions
    }

# Dashboard Stats
@app.get("/api/v1/analytics/dashboard")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    total_apps = len(applicants_db)
    
    return {
        "status": "success",
        "total_applications": total_apps,
        "by_status": {
            "new": sum(1 for a in applicants_db if a["status"] == "new"),
            "screening": sum(1 for a in applicants_db if a["status"] == "screening"),
            "qualified": sum(1 for a in applicants_db if a["status"] == "qualified"),
            "rejected": sum(1 for a in applicants_db if a["status"] == "rejected")
        },
        "average_score": 0,
        "timestamp": datetime.now().isoformat()
    }

# Test endpoint
@app.get("/api/v1/test")
async def test():
    """Test endpoint"""
    return {
        "status": "success",
        "message": "API is working perfectly!",
        "system": "Ocean Professional Recruitment",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
