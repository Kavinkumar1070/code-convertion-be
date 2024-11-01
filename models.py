from fastapi import APIRouter, File, UploadFile, HTTPException
from sqlalchemy import Column, Integer, LargeBinary, create_engine,String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from json_func import role_based_function
from pydantic import BaseModel
from typing import Any
import os 
import json

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
    filename = Column(String, index=True)
    content = Column(LargeBinary)  # Store file data as binary
class RoleFunction(Base):
    __tablename__ = "role_functions"

    id = Column(Integer, primary_key=True, index=True)
    Role = Column(Integer, index=True)
    Function = Column(String(300))  # Store file data as binary

# Create the database and tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
router = APIRouter()

def upload_json_folder(folder_path: str):
    db = SessionLocal()
    try:
        # Clear all existing records in the table
        db.query(FileModel).delete()
        db.commit()  # Commit after deletion

        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)

            # Process only JSON files
            if filename.endswith(".json") and os.path.isfile(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    file_content = f.read()  # Read file content as string

                    # Create a new database entry
                    new_file = FileModel(filename=filename, content=file_content.encode("utf-8"))

                    # Add and commit the new file to the database
                    db.add(new_file)
                    db.commit()
                    db.refresh(new_file)

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Failed to upload files from folder.")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Folder not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

    return {"detail": "Files successfully uploaded"}


# @router.get("/files/{file_id}")
# async def get_file(file_id: int):
#     db = SessionLocal()
#     file_entry = db.query(FileModel).filter(FileModel.id == file_id).first()

#     if file_entry is None:
#         db.close()
#         raise HTTPException(status_code=404, detail="File not found.")

#     db.close()
#     return {
#         "id": file_entry.id,
#         "filename": file_entry.filename,
#         "content": file_entry.content.decode('latin1')  # Decode if needed, or you can send raw binary
#     }


# @router.post("/test")
# async def get_functionality(folder_path: str):
#     a=role_based_function(folder_path)
#     return a 


@router.get("/get-json-filename")
def get_json_file():
    db=SessionLocal()
    filenames = db.query(FileModel.filename).all()
    return {"filenames": [filename[0]  for filename in filenames]}


@router.get("/get-json")
def get_json(filename: str):
    db = SessionLocal()
    try:
        # Query the database for the specific filename
        file_entry = db.query(FileModel).filter(FileModel.filename == filename).first()

        # Check if the file was found
        if file_entry is None:
            raise HTTPException(status_code=404, detail="File not found")

        # Assuming the content is stored as a JSON string
        content_str = file_entry.content.decode('utf-8')  # Decode if stored as bytes
        
        # Attempt to parse the content as JSON
        try:
            content_json = json.loads(content_str)  # Convert string to JSON object
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="File content is not valid JSON")

        # Return the content as JSON
        return {"filename": filename, "content": content_json}  # Return structured as JSON 
    finally:
        db.close()


class ContentModel(BaseModel):
    content: dict  # Specify the type as dict

@router.put("/update/json")
def update_json_file(filename: str, content: ContentModel):
    db= SessionLocal()  
    try:
        file = db.query(FileModel).filter(FileModel.filename == filename).first()

        if not file:
            raise HTTPException(status_code=404, detail="File not found")

        json_content = json.dumps(content.content)  # Convert dict to JSON string
        print("json_content",content.content.keys())
        update_role_function(filename,content.content.keys())
        
        file.content = json_content.encode('utf-8')  # Convert JSON string to bytes
        db.add(file)  # Add the updated file object to the session
        db.commit()  # Commit the changes

        return {"message": "File content updated successfully"}
    
    except Exception as e:
        db.rollback()  # Rollback in case of error
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        db.close()  # Ensure the session is closed after the operation




def create_role_function(data: dict):
    db = SessionLocal()
    try:
        # Clear all existing records in the table
        db.query(RoleFunction).delete()
        db.commit()  # Commit after deletion

        for key, values in data.items():  # Iterate over items in the dictionary
            for function in values:  # Iterate over each function in the list
                # Create a new RoleFunction entry for each function
                new_role_function = RoleFunction(Role=key, Function=function)
                db.add(new_role_function)  # Add the new entry to the session

        db.commit()  # Commit after adding all entries
        return {"detail": "Roles and functions successfully created"}

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Failed to upload files from folder.")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Folder not found.")
    except Exception as e:
        db.rollback()  # Ensure rollback on unexpected error
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


def update_role_function(file:str , data: dict):
    db = SessionLocal()
    try:
        # Clear all existing records in the table
        db.query(RoleFunction).filter(RoleFunction.Role == file).delete()
        db.commit()  # Commit after deletion

        for key in data:  # Iterate over items in the dictionary
                new_role_function = RoleFunction(Role=file, Function=key)
                db.add(new_role_function)  # Add the new entry to the session

        db.commit()  # Commit after adding all entries2
        return {"detail": "Roles and functions successfully created"}

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Failed to upload files from folder.")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Folder not found.")
    except Exception as e:
        db.rollback()  # Ensure rollback on unexpected error
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

