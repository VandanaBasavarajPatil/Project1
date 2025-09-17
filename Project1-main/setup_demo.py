import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime, timezone
import uuid
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_demo_user():
    try:
        # Check if demo user already exists
        existing_user = await db.users.find_one({"email": "demo@taskflow.com"})
        if existing_user:
            print("✅ Demo user already exists")
            return existing_user['id']
        
        # Create demo user
        demo_user = {
            "id": str(uuid.uuid4()),
            "email": "demo@taskflow.com",
            "name": "Demo User",
            "role": "scrum_master",
            "avatar": None,
            "created_at": datetime.now(timezone.utc),
            "is_active": True,
            "hashed_password": pwd_context.hash("demo123")
        }
        
        await db.users.insert_one(demo_user)
        print("✅ Demo user created successfully")
        return demo_user['id']
        
    except Exception as e:
        print(f"❌ Error creating demo user: {e}")
        return None

async def create_sample_data(user_id):
    try:
        # Create sample project
        project = {
            "id": str(uuid.uuid4()),
            "title": "TaskFlow Development",
            "description": "Building the ultimate task management platform",
            "status": "active",
            "deadline": datetime(2024, 12, 31, tzinfo=timezone.utc),
            "created_by": user_id,
            "team_members": [user_id],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        await db.projects.insert_one(project)
        
        # Create sample tasks
        tasks = [
            {
                "id": str(uuid.uuid4()),
                "title": "Design User Dashboard",
                "description": "Create a comprehensive dashboard with KPIs and analytics",
                "status": "done",
                "priority": "high",
                "project_id": project['id'],
                "assigned_to": user_id,
                "created_by": user_id,
                "due_date": datetime(2024, 1, 20, tzinfo=timezone.utc),
                "estimated_hours": 8.0,
                "actual_hours": 7.5,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Implement Kanban Board",
                "description": "Build drag-and-drop Kanban board functionality",
                "status": "in_progress", 
                "priority": "urgent",
                "project_id": project['id'],
                "assigned_to": user_id,
                "created_by": user_id,
                "due_date": datetime(2024, 1, 25, tzinfo=timezone.utc),
                "estimated_hours": 12.0,
                "actual_hours": 0.0,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Add Time Tracking",
                "description": "Implement timer functionality for tracking work hours",
                "status": "review",
                "priority": "medium",
                "project_id": project['id'],
                "assigned_to": user_id,
                "created_by": user_id,
                "due_date": datetime(2024, 1, 30, tzinfo=timezone.utc),
                "estimated_hours": 6.0,
                "actual_hours": 0.0,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Setup Team Management",
                "description": "Create team member management and role assignment",
                "status": "todo",
                "priority": "low",
                "project_id": project['id'],
                "created_by": user_id,
                "due_date": datetime(2024, 2, 5, tzinfo=timezone.utc),
                "estimated_hours": 4.0,
                "actual_hours": 0.0,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
        ]
        
        await db.tasks.insert_many(tasks)
        print("✅ Sample tasks created successfully")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")

async def main():
    print("🚀 Setting up demo data for TaskFlow...")
    user_id = await create_demo_user()
    if user_id:
        await create_sample_data(user_id)
        print("✅ Demo data setup complete!")
    else:
        print("❌ Failed to setup demo data")
    
    client.close()

# Run the setup
if __name__ == "__main__":
    asyncio.run(main())