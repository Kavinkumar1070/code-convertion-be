from fastapi import APIRouter, File, UploadFile, HTTPException
from sqlalchemy import Column, Integer, LargeBinary, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

# Define the database file
DATABASE_URL = "sqlite:///./test.db"

# Setup database
Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define the table structure
class FileModel(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(Integer, index=True)
    content = Column(LargeBinary)  # Store file data as binary

# Create the database and tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
router = APIRouter()

@router.post("/upload-file/")
async def upload_file(file: UploadFile = File(...)):
    db = SessionLocal()
    file_content = await file.read()  # Read file content
    new_file = FileModel(filename=file.filename, content=file_content)

    try:
        db.add(new_file)
        db.commit()
        db.refresh(new_file)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="File upload failed.")
    finally:
        db.close()

    return {"id": new_file.id, "filename": new_file.filename}

@router.get("/files/{file_id}")
async def get_file(file_id: int):
    db = SessionLocal()
    file_entry = db.query(FileModel).filter(FileModel.id == file_id).first()

    if file_entry is None:
        db.close()
        raise HTTPException(status_code=404, detail="File not found.")

    db.close()
    return {
        "id": file_entry.id,
        "filename": file_entry.filename,
        "content": file_entry.content.decode('latin1')  # Decode if needed, or you can send raw binary
    }


