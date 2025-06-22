from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
import base64

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "your-secret-key-change-in-production"

# Create the main app without a prefix
app = FastAPI(title="ABOU GENI API", description="Gestionnaire de Documents de Véhicules")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    role: str = "user"  # admin, user
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "user"

class UserLogin(BaseModel):
    username: str
    password: str

class Vehicle(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    marque: str
    modele: str
    immatriculation: str
    type_vehicule: str  # camion, bus, mini_bus, camionnette
    proprietaire: str
    annee: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: str

class VehicleCreate(BaseModel):
    marque: str
    modele: str
    immatriculation: str
    type_vehicule: str
    proprietaire: str
    annee: Optional[int] = None

class Document(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    vehicle_id: str
    type_document: str  # carte_grise, assurance, controle_technique, permis_conduire
    numero_document: str
    date_emission: datetime
    date_expiration: datetime
    fichier_base64: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: str

class DocumentCreate(BaseModel):
    vehicle_id: str
    type_document: str
    numero_document: str
    date_emission: datetime
    date_expiration: datetime
    fichier_base64: Optional[str] = None

class Alert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str
    vehicle_id: str
    type_alert: str  # 30_jours, 15_jours, 7_jours, expire
    message: str
    date_alert: datetime
    status: str = "active"  # active, dismissed
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Utility functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token invalide")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token invalide")
    
    user = await db.users.find_one({"username": username})
    if user is None:
        raise HTTPException(status_code=401, detail="Utilisateur non trouvé")
    return User(**user)

# Authentication routes
@api_router.post("/auth/register", response_model=User)
async def register(user_data: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"username": user_data.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà utilisé")
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    user_dict = user_data.dict()
    del user_dict["password"]
    user_obj = User(**user_dict)
    
    user_doc = user_obj.dict()
    user_doc["password"] = hashed_password
    
    await db.users.insert_one(user_doc)
    return user_obj

@api_router.post("/auth/login")
async def login(user_data: UserLogin):
    user = await db.users.find_one({"username": user_data.username})
    if not user or not verify_password(user_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Identifiants incorrects")
    
    access_token = create_access_token(data={"sub": user["username"]})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": User(**user)
    }

# Vehicle routes
@api_router.post("/vehicles", response_model=Vehicle)
async def create_vehicle(vehicle_data: VehicleCreate, current_user: User = Depends(get_current_user)):
    vehicle_dict = vehicle_data.dict()
    vehicle_dict["user_id"] = current_user.id
    vehicle_obj = Vehicle(**vehicle_dict)
    
    await db.vehicles.insert_one(vehicle_obj.dict())
    return vehicle_obj

@api_router.get("/vehicles", response_model=List[Vehicle])
async def get_vehicles(current_user: User = Depends(get_current_user)):
    vehicles = await db.vehicles.find({"user_id": current_user.id}).to_list(1000)
    return [Vehicle(**vehicle) for vehicle in vehicles]

@api_router.get("/vehicles/{vehicle_id}", response_model=Vehicle)
async def get_vehicle(vehicle_id: str, current_user: User = Depends(get_current_user)):
    vehicle = await db.vehicles.find_one({"id": vehicle_id, "user_id": current_user.id})
    if not vehicle:
        raise HTTPException(status_code=404, detail="Véhicule non trouvé")
    return Vehicle(**vehicle)

@api_router.put("/vehicles/{vehicle_id}", response_model=Vehicle)
async def update_vehicle(vehicle_id: str, vehicle_data: VehicleCreate, current_user: User = Depends(get_current_user)):
    vehicle = await db.vehicles.find_one({"id": vehicle_id, "user_id": current_user.id})
    if not vehicle:
        raise HTTPException(status_code=404, detail="Véhicule non trouvé")
    
    await db.vehicles.update_one(
        {"id": vehicle_id, "user_id": current_user.id},
        {"$set": vehicle_data.dict()}
    )
    
    updated_vehicle = await db.vehicles.find_one({"id": vehicle_id, "user_id": current_user.id})
    return Vehicle(**updated_vehicle)

@api_router.delete("/vehicles/{vehicle_id}")
async def delete_vehicle(vehicle_id: str, current_user: User = Depends(get_current_user)):
    result = await db.vehicles.delete_one({"id": vehicle_id, "user_id": current_user.id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Véhicule non trouvé")
    
    # Delete associated documents
    await db.documents.delete_many({"vehicle_id": vehicle_id, "user_id": current_user.id})
    return {"message": "Véhicule supprimé avec succès"}

# Document routes
@api_router.post("/documents", response_model=Document)
async def create_document(document_data: DocumentCreate, current_user: User = Depends(get_current_user)):
    # Verify vehicle exists and belongs to user
    vehicle = await db.vehicles.find_one({"id": document_data.vehicle_id, "user_id": current_user.id})
    if not vehicle:
        raise HTTPException(status_code=404, detail="Véhicule non trouvé")
    
    document_dict = document_data.dict()
    document_dict["user_id"] = current_user.id
    document_obj = Document(**document_dict)
    
    await db.documents.insert_one(document_obj.dict())
    
    # Create alerts for this document
    await create_alerts_for_document(document_obj)
    
    return document_obj

@api_router.get("/documents", response_model=List[Document])
async def get_documents(vehicle_id: Optional[str] = None, current_user: User = Depends(get_current_user)):
    query = {"user_id": current_user.id}
    if vehicle_id:
        query["vehicle_id"] = vehicle_id
    
    documents = await db.documents.find(query).to_list(1000)
    return [Document(**document) for document in documents]

@api_router.get("/documents/{document_id}", response_model=Document)
async def get_document(document_id: str, current_user: User = Depends(get_current_user)):
    document = await db.documents.find_one({"id": document_id, "user_id": current_user.id})
    if not document:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    return Document(**document)

@api_router.put("/documents/{document_id}", response_model=Document)
async def update_document(document_id: str, document_data: DocumentCreate, current_user: User = Depends(get_current_user)):
    document = await db.documents.find_one({"id": document_id, "user_id": current_user.id})
    if not document:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    
    await db.documents.update_one(
        {"id": document_id, "user_id": current_user.id},
        {"$set": document_data.dict()}
    )
    
    updated_document = await db.documents.find_one({"id": document_id, "user_id": current_user.id})
    document_obj = Document(**updated_document)
    
    # Update alerts
    await db.alerts.delete_many({"document_id": document_id})
    await create_alerts_for_document(document_obj)
    
    return document_obj

@api_router.delete("/documents/{document_id}")
async def delete_document(document_id: str, current_user: User = Depends(get_current_user)):
    result = await db.documents.delete_one({"id": document_id, "user_id": current_user.id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    
    # Delete associated alerts
    await db.alerts.delete_many({"document_id": document_id})
    return {"message": "Document supprimé avec succès"}

# Alert functions
async def create_alerts_for_document(document: Document):
    now = datetime.utcnow()
    alerts = []
    
    # 30 days alert
    alert_30 = Alert(
        document_id=document.id,
        vehicle_id=document.vehicle_id,
        type_alert="30_jours",
        message=f"Le document {document.type_document} expire dans 30 jours",
        date_alert=document.date_expiration - timedelta(days=30)
    )
    
    # 15 days alert
    alert_15 = Alert(
        document_id=document.id,
        vehicle_id=document.vehicle_id,
        type_alert="15_jours",
        message=f"Le document {document.type_document} expire dans 15 jours",
        date_alert=document.date_expiration - timedelta(days=15)
    )
    
    # 7 days alert
    alert_7 = Alert(
        document_id=document.id,
        vehicle_id=document.vehicle_id,
        type_alert="7_jours",
        message=f"Le document {document.type_document} expire dans 7 jours",
        date_alert=document.date_expiration - timedelta(days=7)
    )
    
    alerts = [alert_30, alert_15, alert_7]
    alert_dicts = [alert.dict() for alert in alerts]
    
    await db.alerts.insert_many(alert_dicts)

# Alerts routes
@api_router.get("/alerts", response_model=List[Alert])
async def get_alerts(current_user: User = Depends(get_current_user)):
    # Get user's vehicles
    user_vehicles = await db.vehicles.find({"user_id": current_user.id}).to_list(1000)
    vehicle_ids = [v["id"] for v in user_vehicles]
    
    now = datetime.utcnow()
    alerts = await db.alerts.find({
        "vehicle_id": {"$in": vehicle_ids},
        "date_alert": {"$lte": now},
        "status": "active"
    }).to_list(1000)
    
    return [Alert(**alert) for alert in alerts]

@api_router.put("/alerts/{alert_id}/dismiss")
async def dismiss_alert(alert_id: str, current_user: User = Depends(get_current_user)):
    result = await db.alerts.update_one(
        {"id": alert_id},
        {"$set": {"status": "dismissed"}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Alerte non trouvée")
    
    return {"message": "Alerte masquée"}

# Statistics routes
@api_router.get("/statistics")
async def get_statistics(current_user: User = Depends(get_current_user)):
    # Get user's vehicles and documents
    vehicles_count = await db.vehicles.count_documents({"user_id": current_user.id})
    documents_count = await db.documents.count_documents({"user_id": current_user.id})
    
    # Get active alerts
    user_vehicles = await db.vehicles.find({"user_id": current_user.id}).to_list(1000)
    vehicle_ids = [v["id"] for v in user_vehicles]
    alerts_count = await db.alerts.count_documents({
        "vehicle_id": {"$in": vehicle_ids},
        "status": "active",
        "date_alert": {"$lte": datetime.utcnow()}
    })
    
    # Get expiring documents (next 30 days)
    future_date = datetime.utcnow() + timedelta(days=30)
    expiring_documents = await db.documents.count_documents({
        "user_id": current_user.id,
        "date_expiration": {"$lte": future_date, "$gte": datetime.utcnow()}
    })
    
    return {
        "vehicles_count": vehicles_count,
        "documents_count": documents_count,
        "alerts_count": alerts_count,
        "expiring_documents": expiring_documents
    }

# Search route
@api_router.get("/search")
async def search(q: str, current_user: User = Depends(get_current_user)):
    vehicles = await db.vehicles.find({
        "user_id": current_user.id,
        "$or": [
            {"marque": {"$regex": q, "$options": "i"}},
            {"modele": {"$regex": q, "$options": "i"}},
            {"immatriculation": {"$regex": q, "$options": "i"}},
            {"proprietaire": {"$regex": q, "$options": "i"}}
        ]
    }).to_list(100)
    
    documents = await db.documents.find({
        "user_id": current_user.id,
        "$or": [
            {"type_document": {"$regex": q, "$options": "i"}},
            {"numero_document": {"$regex": q, "$options": "i"}}
        ]
    }).to_list(100)
    
    return {
        "vehicles": [Vehicle(**v) for v in vehicles],
        "documents": [Document(**d) for d in documents]
    }

# Create default admin user
@api_router.post("/setup")
async def setup_default_user():
    # Check if admin already exists
    admin = await db.users.find_one({"username": "admin"})
    if admin:
        return {"message": "Admin user already exists"}
    
    # Create admin user
    admin_user = UserCreate(
        username="admin",
        email="admin@abougeni.org",
        password="admin123",
        role="admin"
    )
    
    hashed_password = get_password_hash(admin_user.password)
    user_dict = admin_user.dict()
    del user_dict["password"]
    user_obj = User(**user_dict)
    
    user_doc = user_obj.dict()
    user_doc["password"] = hashed_password
    
    await db.users.insert_one(user_doc)
    return {"message": "Admin user created successfully"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()