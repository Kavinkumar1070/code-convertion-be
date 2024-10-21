import os
import shutil
import logging
import git
import stat
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from clone_func import *
from nlp_func import *
# Initialize FastAPI
app = FastAPI()

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
    output_folder: str
    
#step1

@app.post("/clone_or_copy/")
def clone_code(request: CloneRequest):
    """Endpoint to clone a GitHub repo or copy from a local directory."""
    fixed_target_directory = os.path.join(os.getcwd(), 'new_project')

    # Clean the target directory before processing
    clean_folder(fixed_target_directory)

    source_type = request.source_type.strip().lower()
    source_path = request.source_path.strip()

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

#step3

@app.post("/process_routers/")
def process_routers(request: ProcessRequest):
    """Endpoint to process router files and extract schema imports."""
    routers_directory = os.path.join(request.root_directory, request.routers_name)  # Adjusted path
    logging.info(f"Routers directory: {routers_directory}")

    # Check if the routers directory exists
    if not os.path.exists(routers_directory):
        raise HTTPException(status_code=404, detail=f"Routers directory '{routers_directory}' not found.")
    
    # Iterate over each router file in the directory
    for root, _, files in os.walk(routers_directory):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                router_file_path = os.path.join(root, file)
                logging.info(f"Processing router file: {router_file_path}")
                print(request.root_directory)
                # Find schema imports in the current router file
                schema_imports = find_schema_imports_in_router(router_file_path, request.root_directory, request.schemas_name)
                for schema_name, classes in schema_imports:
                    logging.info(f"Found schema imports: {schema_name} - {classes}")

                    # Construct schema file path
                    schema_file_path = os.path.join(request.root_directory, request.schemas_name, f"{schema_name.split('.')[-1]}.py")
                    logging.info(f"Processing schema file: {schema_file_path}")

                    # Extract class code from the schema file
                    class_codes = extract_class_code(schema_file_path, classes)

                    # Write the extracted class code back into the router file
                    try:
                        with open(router_file_path, 'a') as router_file:  # Append to the router file
                            router_file.write("\n\n# Inserted class definitions\n")
                            router_file.write(class_codes)
                        
                        logging.info(f"Extracted classes from {schema_file_path} and pasted into {router_file_path}.")  # Success message
                    except Exception as e:
                        logging.error(f"Error writing to {router_file_path}: {e}")
                        raise HTTPException(status_code=500, detail=f"Error writing to {router_file_path}: {e}")

    return {"message": "Router files processed successfully."}

#step 4
@app.post("/process_code/")
def process_code(request: FolderRequest):
    """Endpoint to process all files in a specified folder."""
    # Construct the folder path using CWD, root_directory, and routers_name
    current_working_directory = os.getcwd()
    folder_path = os.path.join(current_working_directory, request.root_directory, request.routers_name)

    process_code_folder(folder_path)
    return {"message": "Code processing completed successfully."}

#step 5
@app.post("/process_files/")
def process_files_endpoint(request: FileProcessingRequest):
    """Endpoint to process files from input folder and save results to output folder."""
    # Construct the input folder path using cwd, root_directory, and routers_name
    current_working_directory = os.getcwd()
    input_folder = os.path.join(current_working_directory, request.root_directory, request.routers_name)
    
    # Use the output folder provided in the request
    output_folder = os.path.join(current_working_directory,request.output_folder)

    # Call the process_files function
    process_files(input_folder, output_folder)

    return {"message": "File processing completed successfully."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

