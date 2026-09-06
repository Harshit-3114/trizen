### Task 1: Project Setup and Backend Scaffolding

**Files:**
- Create: ackend/app/main.py
- Create: ackend/app/core/config.py
- Create: ackend/app/core/database.py
- Create: equirements.txt
- Create: lembic.ini
- Create: lembic/env.py

**Interfaces:**
- Consumes: None
- Produces: FastAPI app instance, database connection factory, basic configuration

- [ ] **Step 1: Initialize project structure and dependencies**

`ash
mkdir -p backend/app/{core,api/v1/endpoints,models,schemas,crud,utils}
touch backend/app/__init__.py
touch backend/app/core/__init__.py
touch backend/app/api/v1/__init__.py
touch backend/app/api/v1/endpoints/__init__.py
touch backend/app/models/__init__.py
touch backend/app/schemas/__init__.py
touch backend/app/crud/__init__.py
touch backend/app/utils/__init__.py
`

- [ ] **Step 2: Create requirements.txt with FastAPI, SQLAlchemy, etc.**

`
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pydantic==2.5.0
alembic==1.13.1
python-dotenv==1.0.0
`

- [ ] **Step 3: Initialize git repository and commit**

`ash
git init
git add .
git commit -m "feat: initialize project structure"
`

- [ ] **Step 4: Create basic FastAPI app in main.py**

`python
from fastapi import FastAPI

app = FastAPI(
    title="Photo Sharing Platform API",
    description="API for event photo sharing platform",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Photo Sharing Platform API"}
`

- [ ] **Step 5: Run and verify server starts**

`ash
uvicorn backend.app.main:app --reload
`
Expected: Server starts successfully on http://localhost:8000

- [ ] **Step 6: Commit**

`ash
git add backend/app/main.py requirements.txt
git commit -m "feat: create basic FastAPI app"
"
