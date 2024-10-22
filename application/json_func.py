from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from typing import List
import json
import os

def process_json_files(input_directory: str, roles_directory: str, user_roles: List[str]):
    # Create the roles directory if it doesn't exist
    os.makedirs(roles_directory, exist_ok=True)
    
    # Create noroles.json file
    noroles_file_path = os.path.join(roles_directory, "nonroles.json")
    noroles_data = {}

    # Process each JSON file in the input directory
    for filename in os.listdir(input_directory):
        if filename.endswith('.json'):
            file_path = os.path.join(input_directory, filename)
            with open(file_path, 'r') as file:
                try:
                    data = json.load(file)

                    # Process each project in the JSON data
                    for key, project in data.items():
                        project_info = {
                            "project": project["project"],
                            "project description": project["project description"],
                            "url": project["url"],
                            "method": project["method"],
                            "payload": project.get("payload", {})
                        }

                        # Check if any roles match the user-provided roles
                        matched = False
                        for role in project["Roles"]:
                            if role in user_roles:
                                matched = True
                                role_filename = os.path.join(roles_directory, f"{role}.json")

                                # Append the project info to the role's file
                                if os.path.exists(role_filename):
                                    with open(role_filename, 'r+') as role_file:
                                        role_data = json.load(role_file)
                                        role_data[key] = project_info
                                        role_file.seek(0)
                                        json.dump(role_data, role_file, indent=4)
                                        role_file.truncate()
                                else:
                                    with open(role_filename, 'w') as role_file:
                                        json.dump({key: project_info}, role_file, indent=4)

                        # If no roles matched, add to noroles.json
                        if not matched:
                            noroles_data[key] = project_info

                except json.JSONDecodeError:
                    print(f"Error decoding JSON from file: {file_path}")
                except Exception as e:
                    print(f"An error occurred while processing file {file_path}: {e}")

    # Save projects with no matching roles to noroles.json
    if noroles_data:
        with open(noroles_file_path, 'w') as noroles_file:
            json.dump(noroles_data, noroles_file, indent=4)

    print(f"Project details saved in '{roles_directory}' folder.")
    if noroles_data:
        print(f"Projects with no matching roles saved in '{noroles_file_path}'.")