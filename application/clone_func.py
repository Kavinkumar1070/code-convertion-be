import os
import shutil
import logging
import git
import stat
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import re
from groq import Groq

#step1

def clone_github_repo(repo_url, clone_dir):
    """Clone the GitHub repository to the local directory."""
    try:
        git.Repo.clone_from(repo_url, clone_dir)
        logging.info(f"Cloned GitHub repo: '{repo_url}' into '{clone_dir}'")
    except Exception as e:
        logging.error(f"Error cloning repository: {e}")
        raise HTTPException(status_code=500, detail=f"Error cloning repository: {e}")

def copy_project_to_directory(source_directory, target_directory):
    """Copy the entire project from source_directory to target_directory."""
    os.makedirs(target_directory, exist_ok=True)

    try:
        for item in os.listdir(source_directory):
            source_path = os.path.join(source_directory, item)
            target_path = os.path.join(target_directory, item)

            if os.path.isdir(source_path):
                shutil.copytree(source_path, target_path, dirs_exist_ok=True)
            else:
                shutil.copy2(source_path, target_path)

        logging.info(f"Copied project from '{source_directory}' to '{target_directory}'")
    except Exception as e:
        logging.error(f"Failed to copy project: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to copy project: {e}")

def remove_readonly(func, path, excinfo):
    """Function to remove readonly files before deleting."""
    os.chmod(path, stat.S_IWRITE)  # Change the file's permission to writable
    func(path)  # Retry the operation

def clean_folder(folder_path):
    """Removes all files and subdirectories in the specified folder."""
    if not os.path.exists(folder_path):
        logging.warning(f"The folder {folder_path} does not exist.")
        return

    git_dir = os.path.join(folder_path, '.git')
    if os.path.exists(git_dir):
        try:
            shutil.rmtree(git_dir, onerror=remove_readonly)
            logging.info(f"Removed directory: {git_dir}")
        except Exception as e:
            logging.error(f"Error deleting {git_dir}: {e}")

    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        try:
            if os.path.isfile(item_path):
                os.remove(item_path)
                logging.info(f"Removed file: {item_path}")
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path, onerror=remove_readonly)
                logging.info(f"Removed directory: {item_path}")
        except Exception as e:
            logging.error(f"Error deleting {item_path}: {e}")

    logging.info(f"All accessible files and subdirectories in {folder_path} have been removed.")
    
    
    
#step2

def find_folder(target_folder_name, search_path):
    """Finds the target folder in the given search path and returns the full path."""
    for root, dirs, files in os.walk(search_path):
        if target_folder_name in dirs:
            found_folder_path = os.path.join(root, target_folder_name)
            logging.info(f"Found folder: {found_folder_path}")
            return found_folder_path
    logging.warning(f"Folder '{target_folder_name}' not found in '{search_path}'")
    return None


def copy_selected_folders(source_directory, target_directory, selected_folders, root_directory):
    """
    Copies selected folders from source_directory to target_directory.
    Checks if the root_directory exists in source_directory before proceeding.
    """
    # Check if the root directory exists in the source directory
    root_folder_path = find_folder(root_directory, source_directory)
    if not root_folder_path:
        return None # Exit the function if the root directory is not found
    
    # Ensure the target directory exists
    os.makedirs(target_directory, exist_ok=True)

    # Iterate over the selected folders
    for folder in selected_folders:
        folder_path = find_folder(folder, root_folder_path)  # Use find_folder to get the full path inside root_directory

        # Check if the folder was found
        if folder_path:
            try:
                target_folder_path = os.path.join(target_directory, os.path.basename(folder_path))
            
                # Copy the entire folder to the target directory
                shutil.copytree(folder_path, target_folder_path)
                return {"message":f"Copied folder: '{folder_path}' to '{target_folder_path}'"} 
            except Exception as e:
                return {"message":f"Failed to copy '{folder}': {e}"}
        else:
            return {"message":f"Folder '{folder}' does not exist in the root directory '{root_directory}'."}

#step 3

# Function to find schema imports in a single router file
def find_schema_imports_in_router(router_file_path,root_directory,schemas_):
    schema_imports = set()  # Use a set to avoid duplicates

    # Updated regex pattern to match both single-line and multiline imports
    import_pattern_start = re.compile(rf'^(from\s+({root_directory}(\.\w+)*\.{schemas_}\.\w+)\s+import\s+(.+))')
    import_pattern_continue = re.compile(r'^\s*(.+)')  # Pattern for multiline imports

    try:
        with open(router_file_path, 'r') as f:
            multiline_import = False
            current_imports = []
            current_schema = None
            
            for line_number, line in enumerate(f, start=1):
                line = line.strip()  # Strip whitespace from the line

                if multiline_import:
                    # We're in the middle of a multiline import
                    match_continue = import_pattern_continue.match(line)
                    if match_continue:
                        part = match_continue.group(1).strip()
                        current_imports.append(part)
                        if part.endswith(')'):  # End of multiline import
                            multiline_import = False
                            classes = ''.join(current_imports).replace(')', '').replace('(', '').split(',')
                            classes = [cls.strip() for cls in classes if cls.strip()]
                            schema_imports.add((current_schema, tuple(classes)))  # Add multiline import
                            current_imports = []  # Reset
                    continue
                
                match_start = import_pattern_start.match(line)
                if match_start:
                    # Capture details from the matched line
                    schema_name = match_start.group(2)  # Schema name
                    imports = match_start.group(4).strip()  # Imported classes/functions

                    if '(' in imports:  # Start of a multiline import
                        multiline_import = True
                        current_schema = schema_name
                        current_imports = [imports]  # Start collecting imports
                    else:
                        # Single-line import
                        classes = [cls.strip() for cls in imports.split(',')]
                        schema_imports.add((schema_name, tuple(classes)))  # Store schema filename and classes

    except Exception as e:
        print(f"Error reading {router_file_path}: {e}")

    return schema_imports

def extract_class_code(schema_file, classes):
    # Read the content of the schema file
    try:
        with open(schema_file, 'r') as file:
            file_content = file.read()
    except FileNotFoundError:
        print(f"Error: The file {schema_file} does not exist.")
        return None 

    # Customize the prompt based on the filename and classes
    prompt = f"""
Please extract only the definitions of the following classes and their parent classes from the provided Python code dynamically:
- For each class, check its fields, inheritance, and methods. If the class inherits from any other class or references Enums (like LeaveDuration, LeaveStatus) within the file, include those as well.
- Ensure that all parent classes, fields, and validators used within the requested classes are captured.
- Exclude all other unrelated classes.
- Keep the output in the original Python code format.
 
The classes to extract are:
{', '.join(classes)}.
 
Here is the Python code:
{file_content}
 
Ensure the response is enclosed with `~~~` before and after the output.
"""

    # Set up the Groq API key
    client = Groq(
        api_key="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",
    )

    # Make the API call to the Groq model
    response = client.chat.completions.create(
        messages=[{
            "role": "user",
            "content": prompt,
        }],
        model="llama3-70b-8192",
    )

    # Extract the response content
    natural_language_explanation = response.choices[0].message.content.strip()
    json_start_idx = natural_language_explanation.find("~~~") + 3
    json_end_idx = natural_language_explanation.rfind("~~~") 
    if json_start_idx > -1 and json_end_idx > json_start_idx:
        result = natural_language_explanation[json_start_idx:json_end_idx].strip()
    else:
        result = "No valid response found."  # Add a fallback if markers aren't present
    return result