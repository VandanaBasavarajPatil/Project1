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
    """Create demo user if it doesn't exist"""
    
    # Check if demo user already exists
    existing_user = await db.users.find_one({"email": "demo@taskflow.com"})
    if existing_user:
        print("Demo user already exists!")
        return
    
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
    print("✅ Demo user created successfully!")
    print(f"   Email: demo@taskflow.com")
    print(f"   Password: demo123")
    print(f"   Role: scrum_master")
    print(f"   ID: {demo_user['id']}")

async def create_sample_data():
    """Create some sample projects and tasks"""
    
    # Get demo user
    demo_user = await db.users.find_one({"email": "demo@taskflow.com"})
    if not demo_user:
        print("Demo user not found!")
        return
    
    user_id = demo_user["id"]
    
    # Create sample projects
    projects = [
        {
            "id": str(uuid.uuid4()),
            "title": "Website Redesign",
            "description": "Complete redesign of company website with modern UI/UX",
            "status": "active",
            "deadline": datetime(2024, 12, 31, 23, 59, 59, tzinfo=timezone.utc),
            "created_by": user_id,
            "team_members": [user_id],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Mobile App Development",
            "description": "Develop cross-platform mobile application",
            "status": "planning",
            "deadline": datetime(2025, 3, 15, 23, 59, 59, tzinfo=timezone.utc),
            "created_by": user_id,
            "team_members": [user_id],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
    ]
    
    # Insert projects
    for project in projects:
        existing = await db.projects.find_one({"title": project["title"]})
        if not existing:
            await db.projects.insert_one(project)
            print(f"✅ Created project: {project['title']}")
    
    # Create sample tasks
    project_ids = [p["id"] for p in projects]
    tasks = [
        {
            "id": str(uuid.uuid4()),
            "title": "Design Homepage Mockup",
            "description": "Create wireframes and mockups for the new homepage",
            "status": "todo",
            "priority": "high",
            "project_id": project_ids[0],
            "assigned_to": user_id,
            "created_by": user_id,
            "due_date": datetime(2024, 11, 30, 17, 0, 0, tzinfo=timezone.utc),
            "estimated_hours": 8.0,
            "actual_hours": 0.0,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Setup Development Environment",
            "description": "Configure development tools and frameworks",
            "status": "in_progress",
            "priority": "medium",
            "project_id": project_ids[1],
            "assigned_to": user_id,
            "created_by": user_id,
            "due_date": datetime(2024, 11, 25, 17, 0, 0, tzinfo=timezone.utc),
            "estimated_hours": 4.0,
            "actual_hours": 2.0,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Write API Documentation",
            "description": "Document all API endpoints and usage examples",
            "status": "done",
            "priority": "medium",
            "project_id": project_ids[0],
            "assigned_to": user_id,
            "created_by": user_id,
            "due_date": datetime(2024, 11, 20, 17, 0, 0, tzinfo=timezone.utc),
            "estimated_hours": 6.0,
            "actual_hours": 5.5,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
    ]
    
    # Insert tasks
    for task in tasks:
        existing = await db.tasks.find_one({"title": task["title"]})
        if not existing:
            await db.tasks.insert_one(task)
            print(f"✅ Created task: {task['title']}")

async def main():
    print("🌱 Seeding database with demo data...")
    print("=" * 40)
    
    try:
        await create_demo_user()
        await create_sample_data()
        print("\n🎉 Database seeding completed successfully!")
    except Exception as e:
        print(f"❌ Error seeding database: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())