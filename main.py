from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import List
import logging
import os

# Configurar conexión a base de datos
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# ****************************************************************************************
# Persistencia en SQLite
# ****************************************************************************************

# Configuración de la conexión a la base de datos y definir el modelo de la tabla de tareas
# (por ejemplo, con SQLAlchemy)
#engine = create_engine(DATABASE_URL,connect_args={"check_same_thread":False}) #Exclusivo de SQLite
# engine = create_engine(os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:@db:5432/postgres"))
engine = create_engine(os.getenv("DATABASE_URL"))
SessionLocal= sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)
Base = declarative_base()

# ****************************************************************************************
# Configuración de logging
# ****************************************************************************************
logging.basicConfig(level=logging.INFO, format="%(asctime)s-%(name)s-%(levelname)s-%(message)s")
logger= logging.getLogger(__name__)


class EstudianteDB(Base):
    __tablename__="estudiante"
    id= Column(Integer,primary_key=True,index=True)
    nombre= Column(String, nullable=False, index=True)
    email= Column(String, unique=True, index=True)
    edad= Column(Integer, nullable=False)

    def __repr__(self):
        return f"EstudianteDB(id={self.id}, nombre={self.nombre!r}, email={self.email!r}, edad={self.edad})"

Base.metadata.create_all(bind=engine)

class EstudianteRepository:
    def __init__(self, db:Session):
        self.db=db

    def db_buscar_por_email(self, email:str):
        return self.db.query(EstudianteDB).filter(EstudianteDB.email==email).first()

    def db_obtener_estudiantes(self)->List[EstudianteDB]:
        return self.db.query(EstudianteDB).all()

    def db_obtener_estudiante(self, estudiante_id:int)->EstudianteDB:
        return self.db.query(EstudianteDB).filter(EstudianteDB.id==estudiante_id).first()
    
    def db_crear_estudiante(self, estudiante:EstudianteDB)-> EstudianteDB:
        estudiante_db = EstudianteDB (nombre=estudiante.nombre, email=estudiante.email, edad=estudiante.edad)
        self.db.add(estudiante_db)
        self.db.commit()
        self.db.refresh(estudiante_db)
        return estudiante_db
    
    def db_eliminar_estudiante(self,estudiante_id:int)->bool:
        nroeliminadas= self.db.query(EstudianteDB).filter(EstudianteDB.id==estudiante_id).delete()
        self.db.commit()
        return nroeliminadas > 0

# ****************************************************************************************
# Clase Negocio
# ****************************************************************************************
class EstudianteManager:
    def __init__(self, repo:EstudianteRepository):
        self.repo= repo
    
    def obtener_estudiantes(self)-> List[EstudianteDB]:
        estudiantes_db=self.repo.db_obtener_estudiantes()
        logger.info(f"Lista de Estudiantes:{len(estudiantes_db)}")
        return estudiantes_db

    def obtener_estudiante(self, estudiante_id:int)-> EstudianteDB:
        estudiante_db=self.repo.db_obtener_estudiante(estudiante_id)
        if estudiante_db== None:
            logger.warning(f"No se ha encontrado el estudiante con ID:{estudiante_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Estudiante {estudiante_id} no encontrado")
        logger.info(f"Estudiante:{estudiante_db}")
        return estudiante_db
    
    def crear_estudiante(self, estudiante:EstudianteDB)-> EstudianteDB:
        if self.repo.db_buscar_por_email(estudiante.email):
            logger.warning(f"Intento de registro fallido_ el email {estudiante.email} ya está registrado.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Existe un estudiante registrado con el mismo email: {estudiante.email}")
        estudiante_db=self.repo.db_crear_estudiante(estudiante)
        logger.info(f"Estudiante registrado con ID:{estudiante_db.id}")
        return estudiante_db
    
    def eliminar_estudiante(self, estudiante_id:int):
        if not self.repo.db_eliminar_estudiante(estudiante_id):
            logger.error(f"No se ha encontrado el estudiante con ID:{estudiante_id} para eliminarlo.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Estudiante {estudiante_id} no encontrado")
        logger.info(f"Se ha eliminado el estudiante con ID:{estudiante_id}.")
    
# ****************************************************************************************
# Inyección de dependencias
# ****************************************************************************************
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_estudiante_repository(db:Session=Depends(get_db))->EstudianteRepository:
    return EstudianteRepository(db)

def get_estudiante_manager(repo:EstudianteRepository=Depends(get_estudiante_repository))->EstudianteManager:
    return EstudianteManager(repo)

# ****************************************************************************************
# Modelos Pydantic
# ****************************************************************************************
class EstudianteCreate(BaseModel):
    nombre: str = Field(..., min_length=2, description="Nombre del estudiante")
    email: EmailStr = Field(..., description="Email del estudiante")
    edad: int = Field(..., ge=3, le=99,description="Edad")

    @field_validator("nombre", mode="after")
    @classmethod
    def nombre_valido(cls, value:str)->str:
        if any(caracter.isdigit() for caracter in value):
            raise ValueError("El nombre no puede contener números.")
        return value

    @field_validator("edad", mode="after")
    @classmethod
    def edad_valida(cls,value:int)-> int:
        if not (0 < value < 99 ):
            raise ValueError("La edad debe ser un número entero mayor a cero y menor a 99")
        return value

class EstudianteResponse(BaseModel):
    id: int
    nombre: str
    email: str
    edad: int

app = FastAPI(title="CRUD API", version="1.0.0")    
# Implementación endpoints CRUD
@app.get("/estudiantes", response_model=List[EstudianteResponse])
def listar_estudiantes(mng:EstudianteManager=Depends(get_estudiante_manager)):
    """Lista todas las entidades"""
    return mng.obtener_estudiantes()

@app.get("/estudiantes/{estudiante_id}", response_model=EstudianteResponse)
def obtener_estudiante(estudiante_id: int, mng:EstudianteManager=Depends(get_estudiante_manager)):
    """Recupera una entidad específica"""
    return mng.obtener_estudiante(estudiante_id)

@app.post("/estudiantes", response_model=EstudianteResponse, status_code=status.HTTP_201_CREATED)
def crear_estudiante(estudiante: EstudianteCreate, mng:EstudianteManager=Depends(get_estudiante_manager)):
    """Crea una nueva entidad"""
    return mng.crear_estudiante(estudiante)  

@app.delete("/estudiantes/{estudiante_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_estudiante(estudiante_id: int, mng:EstudianteManager=Depends(get_estudiante_manager)):
    """Borra una entidad"""
    mng.eliminar_estudiante(estudiante_id)

@app.get("/")
def root():
    return {"message": "CRUD API"}