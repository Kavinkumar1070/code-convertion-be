
#step 4
import os
from groq import Groq
import json
import re


import os
from groq import Groq

def convert_models_code_to_natural_language(code_content, filename=None):
    prompt = (
    f"""Please analyze the following {f'code from {filename}' if filename else 'code'} and provide the details as specified below.
    
    Convert the code into natural language and capture the following details for each function and class:

    ### Function and API Route Details:
    
    * **Prefix**: Capture the URL prefix for the API route, if present. If none, indicate "none." If the prefix includes versioning (e.g., `/v1`), include that as well.
    * **Function Name**: Capture the exact function or method name that handles the API request.
    * **Roles**: Identify roles (e.g., 'admin', 'employee') that can access the function. Check in middleware, decorators, annotations, or similar mechanisms. If no roles are defined, state "none."
    * **URL/Endpoint**: Capture the specific URL or endpoint the function handles.
    * **HTTP Method**: Capture the HTTP method (e.g., GET, POST, PUT, DELETE).
    
    ### Parameter Details:
    
    * **Path Parameters**:
        + For each path parameter:
            - **Parameter Name**: The name of the parameter.
            - **Data Type**: The expected data type (e.g., string, int, boolean).
            - **Validations**: Any validation constraints (e.g., min/max values, regex). If none, indicate "none."
            - **Field Requirement**: Whether the parameter is "required" or "optional."
    
    * **Query or Body Parameters**: If the function receives class-based payloads (e.g., Pydantic models), provide the name of the class.
    
    * **Class Parameters**:
        + Capture all class parameters, including injected instances, dependencies, or request bodies passed to the function.
    
    ### Class Definitions:
    
    * **Class Name**: Name of the class or model.
    * **Fields**: 
        - For each field in the class, capture:
            + **Field Name**: Name of the field.
            + **Data Type**: check the Datatype of the field if its in [string, int, EmailStr,Boolean,Emailstr,list] else check any enum or any class matches name then convert it datatype as enum and adjust required , validation field accordingly  or return value none .
            + **Validations**: Any validation constraints (e.g., length, regex, ranges). If none, state "none."
            + **Field Requirement**: Whether the field is "required" or "optional."
        **check twice to fill the fields and values . and also check datatype classes too.
    
    ### Example Output Format:
    
    #### Function Example 1:
    * **Prefix**: `/admin`
    * **Function Name**: `update_employee_data`
    * **Roles**: `admin`
    * **URL/Endpoint**: `/employees/{{employee_id}}`
    * **HTTP Method**: `PUT`
    * **Path Parameters**:
        - `employee_id`: `string`, `required`, `None`
    * **Class Parameters**: `EmployeeUpdate`
    
    #### Function Example 2:
    * **Prefix**: `/admin`
    * **Function Name**: `read_employee`
    * **Roles**: `admin`
    * **URL/Endpoint**: `/employees/{{employee_id}}`
    * **HTTP Method**: `GET`
    * **Path Parameters**:
        - `employee_id`: `string`, `required`
    * **Class Parameters**: `None`
    
    #### Class Example:
    * **Class Name**: `EmployeeUpdate`
        - `firstname`: `string`, `optional`, `None`
        - `lastname`: `string`, `optional`, `None`
        - `dateofbirth`: `string`, `optional`, `None`
        - `email`: `EmailStr`, `required`, `None`
        - `nationality`: `string`, `optional`, `None`

    **Enum Definitions:**

        * **Enum Name: `gender`**
        	+ `ONE_DAY`: `"male"`
        	+ `HALF_DAY`: `"female"`
    
    ### Code to Analyze:
    {code_content}
    """
)


    # Set up the Groq API key
    client = Groq(
        api_key="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",
    )    
    # Make a request to the LLM
    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama3-70b-8192",
        )
        # Extract the response content
        natural_language_explanation = response.choices[0].message.content
        return natural_language_explanation
    except Exception as e:
        print(f"Error communicating with LLM API: {e}")
        return None


# Function to read code from a file and process it
def process_code_file(file_path):
    try:
        with open(file_path, 'r') as file:
            code_content = file.read()

        # Call the conversion function
        explanation = convert_models_code_to_natural_language(code_content, filename=os.path.basename(file_path))
        return explanation

    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None
    
# Function to process all files in a folder
def process_code_folder(folder_path):
    try:
        # Loop through each file in the folder
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)

            # Process only files (ignore subdirectories)
            if os.path.isfile(file_path):
                explanation = process_code_file(file_path)
                
                if explanation:
                    # Save the explanation to a .txt file with the same name as the original file
                    output_file = os.path.splitext(filename)[0] + '.txt'
                    output_path = os.path.join(folder_path, output_file)

                    with open(output_path, 'w') as f:
                        f.write(explanation)
                    print(f"Processed {filename}, saved explanation to {output_file}")
                else:
                    print(f"Could not process {filename}")
    
    except Exception as e:
        print(f"Error processing folder {folder_path}: {e}")
        
#step 5

import json
import re

def extract_api_details_from_text(text):
    # Construct a prompt to instruct the model
    prompt = f"""
Analyze the following text and extract the details for each endpoint in the specified format:

## For payload - include both path parameters and class parameters - explain everything in structure fieldname - for each field datatype,field requirement,validation.
# check the Datatype of the field if its in [string, int, EmailStr,Boolean,Emailstr,list] else check any enum or any class matches name then convert it datatype as enum and adjust required , validation field accordingly  or return value none .

Expected format of output is like json:
{{
    "function name": {{
        "project": "function name",
        "url": "url/endpoint",
        "method": "POST/GET/PUT/DELETE/etc.",
        "Roles": ["role1", "role2", ...],
        "payload": {{
            "path_param":{{
            "field_name1": {{
                "datatype": "string/integer/enum/etc.",
                "required": true,
                "validation": "choices/format/length/etc. or None."
            }},
            }},
            "class_param": {{
                "class_field1": {{
                    "datatype": "string/integer/etc.",
                    "required": true,
                    "validation": "None"
                }},
                ...
            }},
            ...
        }}
    }},
    "get employee details": {{
        "project": "get employee details",
        "url": "employee/edrfghj",
        "method": "GET",
        "Roles": ["employee", "admin", ...],
        "payload": {{
            "path_param":{{
            "employee_id": {{
                "datatype": "integer",
                "required": true,
                "validation": "None"
            }},
            "type": {{
                "datatype": "enum",
                "required": true,
                "validation": ["a","b","c"]
            }}
            ...
            }}
        }}
    }}
}}
If no fields are provided for the Payload, return an empty dictionary: {{}}. If any fields are mentioned, include them in the specified dictionary format.

Please ensure that:
- You do not omit any details, including optional ones.
- The output strictly follows the format shown above without additional phrases like "and so on."
- Include any nested class parameters fully, detailing their fields, data types, required status, and validations.

Here is the text:
{text}

Please enclose the response with `~~~` before and after the output.
"""


    # Set up the Groq API key
    client = Groq(
        api_key="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",
    )

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-70b-8192",
    )
    # Extract the content from the response
    natural_language_explanation = response.choices[0].message.content.strip()
    #print(natural_language_explanation)
    # Locate the JSON section based on the '~~~' markers
    json_start_idx = natural_language_explanation.find("~~~") + 3
    json_end_idx = natural_language_explanation.rfind("~~~")
    # Check if markers are present
    if json_start_idx > -1 and json_end_idx > json_start_idx:
        result = natural_language_explanation[json_start_idx:json_end_idx].strip()
        result = escape_backslashes(result)
        return result

   
def escape_backslashes(text):
    # Escape all backslashes in regular expressions for JSON compatibility
    return text.replace("\\", "\\\\")



import json
import re
def final_formatting(text):
    # Construct a prompt to instruct the model
    prompt = f"""
Analyze the following API documentation text and extract the details for each endpoint in the specified format:
##add new details in response
**project description** - write a description based on method and function name.
**description** - write a description based on method, function name, and field name.
**Both are used for capturing the project or filling field values from user query, so write accordingly.**

**add format** - based on validation, convert the natural language into regex format for all datatypes- use double slash // for regex,
                except enum for enum return validation values;
                if None in validation, return 'None' for format also, do not try to convert.

**add assigned value** - "assigned": "None" for all.

Expected format of output is like json:
{{
    "function name": {{
        "project": "function name",
        "project description": "about project",
        "url": "url/endpoint",
        "method": "POST/GET/PUT/DELETE/etc.",
        "Roles": ["role1", "role2", ...],
        "payload": {{
            "field_name1": {{
                "description": "about field for function name",
                "datatype": "string/integer/enum/etc.",
                "required": true,
                "validation": "choices/format/length/etc. or None.",
                "format": "value", 
                "assigned": "None"
            }},
            "gender": {{
                "description": "gender needed for function name",
                "datatype": "enum",
                "required": true,
                "validation": ["male", "female"],
                "format": ["male", "female"],
                "assigned": "None"
            }},
            "father_contact_no": {{
                "description": "Father's contact number for function name",
                "datatype": "integer",
                "required": true,
                "validation": "must be at least 10 digits long",
                "format": "^\\d{{10,}}$",
                "assigned": "None"
            }},
            ...
        }}
    }},
    "get employee details": {{
        "project": "get employee details",
        "project description": "Retrieve the employee details by employee id",
        "url": "employee/edrfghj",
        "method": "GET",
        "Roles": ["employee", "admin", ...],
        "payload": {{
            "employee_id": {{
                "description": "employee ID to get employee details",
                "datatype": "integer",
                "required": true,
                "validation": "None",
                "format": "None",
                "assigned": "None"
            }}
        }}
    }}
}}

Here is the text:
{text}

Please enclose the response with `~~~` before and after the output.
"""

    # Set up the Groq API key
    client = Groq(
        api_key="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",
    )

    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-70b-8192",
        )

        # Extract the content from the response
        natural_language_explanation = response.choices[0].message.content.strip()

        # Locate the JSON section based on the '~~~' markers
        json_start_idx = natural_language_explanation.find("~~~") + 3
        json_end_idx = natural_language_explanation.rfind("~~~")

        # Check if markers are present
        if json_start_idx > -1 and json_end_idx > json_start_idx:
            result = natural_language_explanation[json_start_idx:json_end_idx].strip()
            result = escape_backslashes(result)
            #print(result)
            try:
                # Load the sanitized JSON
                result = json.loads(result)
                print('Parsed JSON successfully.')
            except json.JSONDecodeError as e:
                print(f"Final JSON parsing error: {e}")
                result = "No valid response found."
        else:
            result = "No valid response found."  # Add a fallback if markers aren't present

    except Exception as e:
        print(f"API call error: {e}")
        result = "No valid response found."

    return result


def process_files(input_folder, output_folder):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Loop through all files in the input folder
    for filename in os.listdir(input_folder):
        # Construct full file path
        file_path = os.path.join(input_folder, filename)

        # Check if it is a file and has a .txt extension
        if os.path.isfile(file_path) and filename.endswith('.txt'):
            # Read the text file containing the API documentation
            with open(file_path, 'r') as file:
                api_text = file.read()

            # Extract API details (Assuming `extract_api_details_from_text` returns a dictionary or similar JSON-serializable structure)
            api_info = extract_api_details_from_text(api_text)
            api_info1 = final_formatting(api_info)

            # Define output file path, changing the extension to .json
            output_file_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}.json")

            # Save the extracted API details to a JSON file
            with open(output_file_path, 'w') as output_file:
                json.dump(api_info1, output_file, indent=4)

            print(f"Processed {filename} and saved as {output_file_path}")