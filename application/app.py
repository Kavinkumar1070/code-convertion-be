import os
import shutil
import logging
import git
import stat
from fastapi import FastAPI, HTTPException,Request
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from typing import List
from fastapi.middleware.cors import CORSMiddleware

from clone_func import *
from nlp_func import *
from json_func import *
from fastapi import FastAPI, UploadFile, File
import os
from pathlib import Path
from models import router
# Initialize FastAPI
app = FastAPI()

app.include_router(router)

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500/","*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Set up logging
logging.basicConfig(level=logging.INFO)

class CloneRequest(BaseModel):
    source_type: str
    source_path: str

class FolderCopyRequest(BaseModel):
    project_name: str
    routers_name: str
    schemas_name: str
    
class ProcessRequest(BaseModel):
    root_directory: str
    routers_name: str
    schemas_name: str

class FolderRequest(BaseModel):
    root_directory: str
    routers_name: str
    
class FileProcessingRequest(BaseModel):
    root_directory: str
    routers_name: str
    schemas_name: str


    
#step1
@app.post("/upload-folder")
async def upload_folder(files: list[UploadFile] = File(...)):
    already= os.path.join(os.getcwd(), 'new_project')
    clean_folder(already)
    upload_directory = Path("new_project")
    upload_directory.mkdir(exist_ok=True)

    for file in files:
        file_path = upload_directory / file.filename

        # Create necessary directories to mimic the folder structure
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write the uploaded file to the destination path
        with open(file_path, "wb") as f:
            f.write(await file.read())

    return {"message": f"Uploaded {len(files)} files successfully."}

@app.post("/git-link")
async def git_link(request: Request):
    data = await request.json()  # Extract the request body
    source_path = data.get('source_path')
    token = data.get('token', None)

    if not source_path:
        raise HTTPException(status_code=400, detail="Source path is required.")

    # If a token is provided, use HTTPS with token authentication
    if token:
        if source_path.startswith("git@"):
            raise HTTPException(status_code=400, detail="SSH URL cannot be used with a token. Use HTTPS URL for token authentication.")
        # Use the token in the HTTPS URL
        auth_repo_url = source_path.replace("https://", f"https://{token}@")
    else:
        # For SSH URL or HTTPS without token
        if source_path.startswith("https://"):
            auth_repo_url = source_path  # Use HTTPS URL without token
        elif source_path.startswith("git@"):
            auth_repo_url = source_path  # Use SSH URL directly
        else:
            raise HTTPException(status_code=400, detail="Invalid repository URL format.")

    print("Received request to clone repository...")

    fixed_target_directory = os.path.join(os.getcwd(), 'new_project')

    # Clean the folder before cloning
    clean_folder(fixed_target_directory)

    try:
        print(f"Cloning from: {auth_repo_url}")
        clone_github_repo(auth_repo_url, fixed_target_directory)
        print("Clone completed successfully.")
        return {"message": f"Repository cloned successfully from {source_path}"}
    except Exception as e:
        print("Error while cloning the repository:", e)
        raise HTTPException(status_code=500, detail=f"GitHub token is required for private repositories.")
   

@app.post("/clone_or_copy/")
def clone_code(request: CloneRequest):
    """Endpoint to clone a GitHub repo or copy from a local directory."""
    fixed_target_directory = os.path.join(os.getcwd(), 'new_project')

    # Clean the target directory before processing
    clean_folder(fixed_target_directory)

    source_type = request.source_type.strip().lower()
    source_path = request.source_path.strip()
    print('**************')
    print(source_path)
    print('**************')
    if source_type == 'local':
        if not os.path.exists(source_path):
            raise HTTPException(status_code=404, detail=f"The directory '{source_path}' does not exist.")
        copy_project_to_directory(source_path, fixed_target_directory)

    elif source_type == 'github':
        clone_github_repo(source_path, fixed_target_directory)

    else:
        raise HTTPException(status_code=400, detail="Invalid input. Please enter 'local' or 'github'.")

    return {"message": "Cloning/Copying Completed"}

#step2

@app.post("/copy_folders/")
def copy_folders(request: FolderCopyRequest):
    """Endpoint to copy specified folders from a project directory."""
    # Use the current working directory as the base path
    current_working_directory = os.getcwd()  # Get the current working directory
    project_directory = os.path.join(current_working_directory, 'new_project')  # Set project directory to 'new_project' folder in CWD
    target_directory = os.path.join(current_working_directory, request.project_name)  # Target directory
    selected_folders = [request.routers_name, request.schemas_name]  # Specify the folders to copy

    # Perform the folder copy operation
    copy_selected_folders(project_directory, target_directory, selected_folders)

    return {"message": "Folders copied successfully."}

#step 3

@app.post("/process/")
def process_all(request: FileProcessingRequest):
    """
    Endpoint to process routers, code, and files.
    This endpoint handles the following:
    - Process router files to extract schema imports and insert class definitions
    - Process code in a specified folder
    - Process files from input to output folder
    """
    current_working_directory = os.getcwd()

    # Step 1: Process Routers
    routers_directory = os.path.join(current_working_directory, request.root_directory, request.routers_name)
    logging.info(f"Routers directory: {routers_directory}")

    if not os.path.exists(routers_directory):
        raise HTTPException(status_code=404, detail=f"Routers directory '{routers_directory}' not found.")

    # Iterate over each router file in the directory
    for root, _, files in os.walk(routers_directory):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                router_file_path = os.path.join(root, file)
                logging.info(f"Processing router file: {router_file_path}")

                # Find schema imports in the current router file
                schema_imports = find_schema_imports_in_router(router_file_path, request.root_directory, request.routers_name)
                for schema_name, classes in schema_imports:
                    logging.info(f"Found schema imports: {schema_name} - {classes}")

                    # Construct schema file path
                    schema_file_path = os.path.join(f"{request.root_directory}/{request.schemas_name}/{schema_name.split('.')[-1]}.py")
                    logging.info(f"Processing schema file: {schema_file_path}")

                    # Extract class code from the schema file
                    # class_codes = extract_class_code(schema_file_path, classes)

                    # # Write the extracted class code back into the router file
                    # try:
                    #     with open(router_file_path, 'a') as router_file:
                    #         router_file.write("\n\n# Inserted class definitions\n")
                    #         router_file.write(class_codes)
                    class_codes = extract_class_code(schema_file_path, classes) or ""
                    try:
                        with open(router_file_path, 'a') as router_file:
                            router_file.write("\n\n# Inserted class definitions\n")
                            router_file.write(class_codes)

                        logging.info(f"Extracted classes from {schema_file_path} and pasted into {router_file_path}.")
                    except Exception as e:
                        logging.error(f"Error writing to {router_file_path}: {e}")
                        raise HTTPException(status_code=500, detail=f"Error writing to {router_file_path}: {e}")

    # Step 2: Process Code
    folder_path = os.path.join(current_working_directory, request.root_directory, request.routers_name)
    logging.info(f"Processing code folder: {folder_path}")
    process_code_folder(folder_path)

    # Step 3: Process Files
    input_folder = os.path.join(current_working_directory, request.root_directory, request.routers_name)
    output_folder = os.path.join(current_working_directory, "output_f")
    logging.info(f"Processing files from {input_folder} to {output_folder}")
    process_files(input_folder, output_folder)

    return {"message": "Processing of routers, code, and files completed successfully."}

#step4

@app.post("/process_json/")
async def process_json(roles: List[str] = Form(...)):
    try:
        # If roles are concatenated into a single string, split them
        if len(roles) == 1 and ',' in roles[0]:
            roles = roles[0].split(',')
            
        roles_directory = "roles"
        current_working_directory = os.getcwd()
        input_directory = os.path.join(current_working_directory, "output_f")
        print(f"Input directory: {input_directory}")
        print(f"Roles received: {roles}")  # Adjusted for clarity

        # Process the JSON files with the user-provided roles
        process_json_files(input_directory, roles_directory, roles)
        return {"message": "JSON files processed successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


