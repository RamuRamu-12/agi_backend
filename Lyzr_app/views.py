#Environment Creation
import os

import requests
from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework.response import Response
from rest_framework.decorators import api_view
from vyzeai.models.openai import ChatOpenAI

from .database import PostgreSQLDB

db = PostgreSQLDB(dbname='uibmogli', user='uibmogli', password='8ogImHfL_1G249lXtM3k2EAIWTRDH2mX')


# Create environment
@api_view(['POST'])
def create_environment(request):
    try:
        data = request.data
        name = data.get('name')
        model_vendor = data.get('model_vendor')
        api_key = data.get('api_key')
        model = data.get('model')
        temperature = data.get('temperature', 0.5)
        top_p = data.get('top_p', 0.9)

        environment_id = db.create_environment(name, model_vendor, api_key, model, temperature, top_p)
        return Response({"environment_id": environment_id}, status=201)
    except Exception as e:
        return Response({"error": str(e)}, status=400)


# Read environment by ID
# Read environment by ID
@api_view(['GET'])
def read_environment(request, environment_id):
    try:
        environment = db.read_environment(environment_id)
        if environment:
            response_data = {

                "features": [],  # Assuming no features are provided, keeping it empty
                "llm_config": {
                    "provider": environment[2],  # model_vendor
                    "model": environment[4],  # model
                    "config": {
                        "temperature": environment[5],  # temperature
                        "top_p": environment[6],  # top_p
                    }
                },
                "env": {
                    "Environment_name": environment[1],  # name
                    "OPENAI_API_KEY":environment[3],  #API_KEY
                },

            }

            return Response(response_data, status=200)

        return Response({"error": "Environment not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=400)



# Update environment by ID
@api_view(['POST'])
def update_environment(request, environment_id):
    try:
        data = request.data
        name = data.get('name')
        model_vendor = data.get('model_vendor')
        api_key = data.get('api_key')
        model = data.get('model')
        temperature = data.get('temperature')
        top_p = data.get('top_p')

        updated_rows = db.update_environment(
            environment_id,
            name,
            model_vendor,
            api_key,
            model,
            temperature,
            top_p,
        )

        if updated_rows:
            return Response({"message": f"Environment with ID {environment_id} updated successfully."}, status=200)
        return Response({"message": f"Environment with ID {environment_id} updated successfully."}, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=400)


# Delete environment by ID
@api_view(['GET'])
def delete_environment(request, environment_id):
    try:
        deleted_rows = db.delete_environment(environment_id)
        if deleted_rows:
            return Response({"message": f"Environment with ID {environment_id} deleted successfully."}, status=200)
        return Response({"error": f"Environment with ID {environment_id} not found."}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=400)


# Read all environments
@api_view(['GET'])
def read_all_environments(request):
    try:
        environments = db.read_all_environments()
        if environments:
            environment_list = []
            for environment in environments:
                environment_list.append({
                    "id": environment[0],
                    "name": environment[1],
                    "model_vendor": environment[2],
                    "api_key": environment[3],
                    "model": environment[4],
                    "temperature": environment[5],
                    "top_p": environment[6],

                })
            return Response(environment_list, status=200)
        return Response({"message": "No environments found."}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=400)



from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create Agent
@api_view(['POST'])
def create_agent(request):
    try:
        data = request.data
        name = data.get('name')
        system_prompt = data.get('system_prompt')
        agent_description = data.get('agent_description')
        tools = data.get('tools')
        upload_attachment = data.get('upload_attachment', False)  # Default value set to False
        env_id = data.get('env_id')

        if not env_id:
            return Response({"error": "Environment ID is required"}, status=400)

        # Create the agent in the database
        agent_id = db.create_agent(name, system_prompt, agent_description, tools, upload_attachment, env_id)

        return Response({"agent_id": agent_id}, status=201)
    except Exception as e:
        return Response({"error": str(e)}, status=400)


# Read Agent by ID
@api_view(['GET'])
def read_agent(request, agent_id):
    try:
        agent = db.read_agent(agent_id)
        if agent:
            return Response({
                "id": agent[0],
                "name": agent[1],
                "system_prompt": agent[2],
                "agent_description": agent[3],
                "tools": agent[4],
            "Additional_Features":{
                "upload_attachment": agent[5],  # Include upload_excel

            },
                "env_id": agent[6]
            }, status=200)
        return Response({"error": "Agent not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=400)


# Update Agent by ID
@api_view(['POST'])
def update_agent(request, agent_id):
    try:
        data = request.data
        name = data.get('name')
        system_prompt = data.get('system_prompt')
        agent_description = data.get('agent_description')
        tools = data.get('tools')
        upload_attachment = data.get('upload_attachment')  # Handle upload_excel update

        env_id = data.get('env_id')

        # Update agent in the database
        db.update_agent(agent_id, name, system_prompt, agent_description, tools, upload_attachment, env_id)

        return Response({"message": f"Agent with ID {agent_id} updated successfully."}, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=400)


# Delete Agent by ID
@api_view(['GET'])
def delete_agent(request, agent_id):
    try:
        db.delete_agent(agent_id)
        return Response({"message": f"Agent with ID {agent_id} deleted successfully."}, status=204)
    except Exception as e:
        return Response({"error": str(e)}, status=400)


# Read all Agents
from rest_framework.decorators import api_view
from rest_framework.response import Response
import logging

# Set up logging
logger = logging.getLogger(__name__)

@api_view(['GET'])
def read_all_agents(request):
    try:
        # Fetch all agents from the database
        agents = db.get_all_agents()

        # Check if any agents are returned
        if not agents:
            return Response({"message": "No agents found"}, status=404)

        # Structure the agents' data for JSON response
        agents_data = [
            {
                "id": agent[0],
                "name": agent[1],
                "system_prompt": agent[2],
                "agent_description": agent[3],
                "tools": agent[4],
            "Additional_Features":{
                "upload_attachment": agent[5],  # Include upload_excel

               },
                "env_id": agent[6]
            }
            for agent in agents
        ]

        return Response({"agents": agents_data}, status=200)

    except Exception as e:
        # Log the error for further investigation
        logger.error(f"Error fetching agents: {str(e)}")

        # Return a user-friendly error message
        return Response({"error": "An error occurred while fetching agents"}, status=500)




#Creation of the openai environment.
from rest_framework.decorators import api_view
from vyzeai.agents.prebuilt_agents import ResearchAgent, VideoAudioBlogAgent, YTBlogAgent, BlogAgent,LinkedInAgent, VideoAgent, EmailAgent

from rest_framework.response import Response
from rest_framework import status
import requests
import pandas as pd


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import requests

# Main API to create an OpenAI environment
@api_view(['POST'])
def create_openai_environment_api(request):
    try:
        agent_id = request.data.get('agent_id')

        if not agent_id:
            return Response({"error": "Agent ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the agent details from the database
        agent = db.read_agent(agent_id)
        if not agent:
            return Response({"error": "Agent not found"}, status=status.HTTP_404_NOT_FOUND)

        # Proceed with environment creation logic
        agent_details = {
            "name": agent[1],
            "system_prompt": agent[2],
            "agent_description": agent[3],
            "tools": agent[4],
            "env_id": agent[6]
        }

        # Retrieve API key from the environment table
        env_details = db.read_environment(agent_details['env_id'])
        if not env_details or not env_details[3]:
            return Response({"error": "API key not found in environment table"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        openai_api_key = env_details[3]

        # Create the OpenAI environment
        environment_response = create_openai_environment(agent_details, openai_api_key)

        if environment_response.get("success"):
            return Response({"message": "OpenAI environment created successfully.",
                             "details": environment_response},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "Failed to create OpenAI environment."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Helper function to create OpenAI environment
def create_openai_environment(agent_details, openai_api_key):
    try:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {openai_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-mini",  # Ensure this model exists or use a valid one
            "messages": [
                {"role": "system", "content": agent_details['system_prompt']},
                {"role": "user", "content": agent_details['agent_description']}
            ],
            "max_tokens": 1500
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            return {"success": True, "response": response.json()}
        else:
            return {"success": False, "error": response.text}

    except Exception as e:
        return {"success": False, "error": str(e)}








# # Helper function to create OpenAI environment
# def create_openai_environment(agent_details):
#     try:
#         env_id = agent_details["env_id"]
#         env_details = db.read_environment(env_id)  # Returns a tuple
#
#         if not env_details:
#             raise ValueError("Environment details not found.")
#
#         openai_api_key = env_details[3]
#         if not openai_api_key:
#             raise ValueError("OpenAI API key not found for the specified environment")
#
#         url = "https://api.openai.com/v1/chat/completions"
#         headers = {
#             "Authorization": f"Bearer {openai_api_key}",
#             "Content-Type": "application/json"
#         }
#         payload = {
#             "model": "gpt-4o-mini",  # Ensure this model exists or use a valid one
#             "messages": [
#                 {"role": "system", "content": agent_details['system_prompt']},
#                 {"role": "user", "content": agent_details['agent_description']}
#             ],
#             "max_tokens": 1500
#         }
#
#         response = requests.post(url, headers=headers, json=payload)
#
#         if response.status_code == 200:
#             return {"success": True, "response": response.json()}
#         else:
#             print(f"OpenAI API Error: {response.status_code} - {response.text}")
#             return {"success": False, "error": response.text}
#
#     except Exception as e:
#         print(f"Error creating OpenAI environment: {e}")
#         return {"success": False, "error": str(e)}
#
#
#
from vyzeai.models.openai import ChatOpenAI
def generate_synthetic_data(api_key, file_path, num_rows=10, chunk_size=50):
    """Generate synthetic data."""

    llm = ChatOpenAI(api_key)

    # Load the original data and get the column structure
    data = pd.read_excel(file_path).tail(30)
    sample_str = data.to_csv(index=False, header=False)
    expected_columns = data.columns  # The expected number of columns

    sysp = "You are a synthetic data generator. Your output should only be CSV format without any additional text and code fences."

    generated_rows = []
    rows_generated = 0

    while rows_generated < num_rows:

        if generated_rows:
            # If we have already generated rows, use the last 10 rows for context
            current_sample_str = "\n".join([",".join(row) for row in generated_rows[-10:]])
        else:
            # Use the original sample data if no rows have been generated yet
            current_sample_str = sample_str

        # Calculate how many more rows are needed
        rows_to_generate = min(chunk_size, num_rows - rows_generated)

        prompt = (
            f"Generate {rows_to_generate} more rows of synthetic data following this pattern:\n\n{current_sample_str}\n"
            "\nEnsure the synthetic data does not contain column names or old data. "
            "\nExpected Output: synthetic data as comma-separated values (',').")

        # Generate the synthetic data using the language model
        generated_data = llm.run(prompt, system_message=sysp)

        # Parse the generated data into rows
        rows = [row.split(",") for row in generated_data.strip().split("\n") if row]

        # Ensure that each generated row matches the expected column count
        cleaned_rows = []
        for row in rows:
            if len(row) == len(expected_columns):
                cleaned_rows.append(row)  # Accept rows with the correct number of columns
            elif len(row) < len(expected_columns):
                # If the row has fewer columns, append empty strings to match the column count
                cleaned_rows.append(row + [''] * (len(expected_columns) - len(row)))
            elif len(row) > len(expected_columns):
                # If the row has more columns, truncate the extra columns
                cleaned_rows.append(row[:len(expected_columns)])

        # Add the cleaned rows to the generated rows
        rows_needed = num_rows - rows_generated
        generated_rows.extend(cleaned_rows[:rows_needed])

        rows_generated += len(cleaned_rows[:rows_needed])

    # Create the DataFrame using the original column names
    generated_df = pd.DataFrame(generated_rows, columns=expected_columns)

    return generated_df






from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
import os
import base64
import shutil
from django.core.files.storage import default_storage
from django.conf import settings
from vyzeai.tools.raw_functions import excel_to_sql

@api_view(['POST'])
def run_openai_environment(request):
    try:
        agent_id = request.data.get('agent_id')
        user_prompt = request.data.get('prompt', '')
        url = request.data.get('url', '')
        yt_url = request.data.get('yt_url', '')
        file = request.FILES.get('file')  # File if attached
        num_rows = request.data.get('num_rows', 10)  # Number of synthetic rows to generate

        # Ensure num_rows is an integer
        try:
            num_rows = int(num_rows)
        except ValueError:
            return Response({"error": "Invalid value for num_rows. It must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

        if not agent_id:
            return Response({"error": "Agent ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve agent details
        agent = db.read_agent(agent_id)
        if not agent:
            return Response({"error": "Agent not found"}, status=status.HTTP_404_NOT_FOUND)

        # Retrieve the API key from the environment table using env_id
        env_details = db.read_environment(agent[6])  # agent[6] is env_id
        if not env_details or not env_details[3]:
            return Response({"error": "API key not found in environment table"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        openai_api_key = env_details[3]

        # Process based on input type (prompt, URL, file)
        result = None

        # If file is uploaded and tool type is text-to-SQL
        if file and 'text-to-sql' in agent[4]:
            # Store the Excel file in the database
            table_name = file.name.split('.')[0]
            try:
                file_path = os.path.join(settings.MEDIA_ROOT, file.name)
                with default_storage.open(file_path, 'wb+') as f:
                    for chunk in file.chunks():
                        f.write(chunk)

                # Convert the Excel file to a SQL table
                excel_to_sql(file_path, table_name, "uibcedotbqcywunfl752", "LrdjP9dvLV0GP8PWRDmvREDB9IxmGu", "by80v7itmu1gw3kjmblq-postgresql.services.clever-cloud.com:50013", "by80v7itmu1gw3kjmblq")

                # After storing, generate a graph or text based on the query
                if user_prompt:
                    # Construct a command for the agent
                    query = f"SELECT * FROM {table_name} WHERE {user_prompt}"
                    model_response = send_prompt_to_openai(openai_api_key, agent, query)
                    if model_response.get("success"):
                        return Response({
                            "message": "Prompt processed successfully.",
                            "content": model_response['content'],
                            "total_tokens": model_response['total_tokens']
                        }, status=status.HTTP_200_OK)
                    else:
                        return Response({"error": model_response['error']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                return Response({"error": f"Failed to store and query the Excel file: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # If only a prompt is provided
        elif user_prompt and not (url or yt_url or file):
            model_response = send_prompt_to_openai(openai_api_key, agent, user_prompt)
            if model_response.get("success"):
                return Response({
                    "message": "Prompt processed successfully.",
                    "content": model_response['content'],
                    "total_tokens": model_response['total_tokens']
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": model_response['error']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # If URL + prompt is provided
        elif (url or yt_url) and user_prompt:
            if 'blog_post' in agent[4]:
                result = generate_blog_from_url(user_prompt, url or yt_url, 'blog_post', openai_api_key)
            elif 'linkedin_post' in agent[4]:
                result = generate_blog_from_url(user_prompt, url or yt_url, 'linkedin_post', openai_api_key)

        # If file + prompt is provided for blog or LinkedIn post
        elif file and user_prompt:
            if 'blog_post' in agent[4]:
                result = generate_blog_from_file(user_prompt, file, 'blog_post', openai_api_key)
            elif 'linkedin_post' in agent[4]:
                result = generate_blog_from_file(user_prompt, file, 'linkedin_post', openai_api_key)

        # If file is provided for synthetic data generation
        elif file and 'synthetic_data' in agent[4]:
            result = generate_synthetic_data(openai_api_key, file, num_rows)

        if result:
            # Move the image from the temporary directory to the media directory
            temp_image_path = result.get("image_path", None)
            if temp_image_path:
                # Construct the full path to the temporary image
                temp_full_image_path = os.path.join(settings.TEMP_DIR, temp_image_path)  # Adjust TEMP_DIR as needed
                new_image_name = os.path.basename(temp_full_image_path)
                new_image_path = os.path.join(settings.MEDIA_ROOT, new_image_name)

                try:
                    # Move the image file to the media directory
                    shutil.move(temp_full_image_path, new_image_path)
                    # Read the image and encode it to base64
                    with default_storage.open(new_image_path, 'rb') as image_file:
                        image_data = image_file.read()
                        image_base64 = base64.b64encode(image_data).decode('utf-8')
                except Exception as e:
                    return Response({"error": f"Failed to move or read the image: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({
                "message": "Content generated successfully.",
                "content": result['content'],
                "image": image_base64  # Send base64-encoded image
            }, status=status.HTTP_200_OK)

        else:
            return Response({"error": "No valid tool found for the given input."}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Helper function to process the prompt through OpenAI
def send_prompt_to_openai(api_key, agent, user_prompt):
    try:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-mini",  # Use appropriate model
            "messages": [
                {"role": "system", "content": agent[2]},  # System prompt from agent details
                {"role": "user", "content": user_prompt}  # User's input prompt
            ],
            "max_tokens": 1500
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            response_data = response.json()
            content = response_data['choices'][0]['message']['content']
            total_tokens = response_data['usage']['total_tokens']
            return {
                "success": True,
                "content": content,
                "total_tokens": total_tokens
            }
        else:
            return {"success": False, "error": response.text}

    except Exception as e:
        return {"success": False, "error": str(e)}


# Generate content from URL (for blog or LinkedIn post)
def generate_blog_from_url(prompt, url, option, api_key):
    try:
        if option == 'blog_post':
            research_agent = ResearchAgent(api_key)
            blog_agent = BlogAgent(api_key)
            context = research_agent.research(prompt, url)
            contents = blog_agent.generate_blog(prompt, url, context)
            content = contents[0][0]
            image_path = contents[-1][-1][0]
            return {"content": content, "image_path": image_path}
        elif option == 'linkedin_post':
            linkedin_agent = LinkedInAgent(api_key)
            research_agent = ResearchAgent(api_key)
            context = research_agent.research(prompt, url)
            content, image_path = linkedin_agent.generate_linkedin_post(context)
            return {"content": content, "image_path": image_path}
    except Exception as e:
        return {"error": str(e)}


# Generate content from file (for blog or LinkedIn post)
def generate_blog_from_file(prompt, file, option, api_key):
    try:
        file_path = save_file(file)

        if option == 'blog_post':
            va_agent = VideoAudioBlogAgent(api_key)
            contents = va_agent.generate_blog(file_path)
            content = contents[0][0]
            image_path = contents[-1][-1][0]
            return {"content": content, "image_path": image_path}
        elif option == 'linkedin_post':
            va_agent = VideoAudioBlogAgent(api_key)
            linkedin_agent = LinkedInAgent(api_key)
            context = va_agent.extract_text(file_path)
            content, image_path = linkedin_agent.generate_linkedin_post(context)
            return {"content": content, "image_path": image_path}
    except Exception as e:
        return {"error": str(e)}


# Generate synthetic data based on uploaded file
def generate_synthetic_data(api_key, file, num_rows=10, chunk_size=50):
    """Generate synthetic data."""

    # Save the file and read its contents
    file_path = save_file(file)
    data = pd.read_excel(file_path).tail(30)

    # Fix: Use .empty to check if the DataFrame is empty
    if data.empty:
        return {"error": "Uploaded file contains no data"}

    sample_str = data.to_csv(index=False, header=False)
    expected_columns = data.columns

    llm = ChatOpenAI(api_key)
    sysp = "You are a synthetic data generator. Your output should only be CSV format without any additional text and code fences."

    generated_rows = []
    rows_generated = 0

    while rows_generated < num_rows:
        if generated_rows:
            current_sample_str = "\n".join([",".join(row) for row in generated_rows[-10:]])
        else:
            current_sample_str = sample_str

        rows_to_generate = min(chunk_size, num_rows - rows_generated)

        prompt = (
            f"Generate {rows_to_generate} more rows of synthetic data following this pattern:\n\n{current_sample_str}\n"
            "\nEnsure the synthetic data does not contain column names or old data. "
            "\nExpected Output: synthetic data as comma-separated values (',')."
        )

        generated_data = llm.run(prompt, system_message=sysp)

        rows = [row.split(",") for row in generated_data.strip().split("\n") if row]

        cleaned_rows = []
        for row in rows:
            if len(row) == len(expected_columns):
                cleaned_rows.append(row)
            elif len(row) < len(expected_columns):
                cleaned_rows.append(row + [''] * (len(expected_columns) - len(row)))
            elif len(row) > len(expected_columns):
                cleaned_rows.append(row[:len(expected_columns)])

        rows_needed = num_rows - rows_generated
        generated_rows.extend(cleaned_rows[:rows_needed])
        rows_generated += len(cleaned_rows[:rows_needed])

    generated_df = pd.DataFrame(generated_rows, columns=expected_columns)
    return {"message": "Synthetic data generated successfully.", "data": generated_df.to_csv(index=False)}


# Helper function to save uploaded file
def save_file(file):
    directory = 'temp'
    if not os.path.exists(directory):
        os.makedirs(directory)

    file_path = os.path.join(directory, file.name)
    with open(file_path, "wb") as f:
        f.write(file.read())
    return file_path






#Uploading an excel file
import pandas as pd
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import parser_classes, api_view
from rest_framework.response import Response
from rest_framework import status
import requests

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])  # Allow multipart form data
def run_openai_with_excel(request):
    try:
        # Retrieve the environment details using agent_id
        agent_id = request.data.get('agent_id')
        if not agent_id:
            return Response({"error": "Agent ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve agent and environment details
        agent = db.read_agent(agent_id)
        if not agent:
            return Response({"error": "Agent not found"}, status=status.HTTP_404_NOT_FOUND)

        # Retrieve the uploaded Excel file
        excel_file = request.FILES.get('file')
        if not excel_file:
            return Response({"error": "Excel file is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the user query (analysis type question)
        user_query = request.data.get('query')
        if not user_query:
            return Response({"error": "Query is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Read the Excel file into a pandas DataFrame
        try:
            df = pd.read_excel(excel_file)
        except Exception as e:
            return Response({"error": f"Error reading Excel file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        # You can process the DataFrame as needed before sending it to OpenAI
        data_summary = df.describe().to_string()  # Summary of the data
        print(data_summary)

        # Get environment details
        env_id = agent[6]
        env_details = db.read_environment(env_id)
        if not env_details:
            return Response({"error": "Environment details not found"}, status=status.HTTP_404_NOT_FOUND)

        # Extract the OpenAI API key
        openai_api_key = env_details[3]
        if not openai_api_key:
            return Response({"error": "OpenAI API key not found for the specified environment"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Send the Excel data summary and user query to OpenAI for processing
        model_response = send_query_to_openai(openai_api_key, agent, data_summary, user_query)

        # Check response from OpenAI
        if model_response.get("success"):
            return Response({
                "content": model_response['content'],
                "total_tokens": model_response['total_tokens']
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": model_response['error']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Helper function to send Excel data and user query to OpenAI API
def send_query_to_openai(api_key, agent, data_summary, user_query):
    try:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Prepare the message format required by the OpenAI API
        payload = {
            "model": "gpt-4o-mini",  # Use the model stored in the environment
            "messages": [
                {"role": "system", "content": agent[2]},  # system_prompt from agent details
                {"role": "user", "content": f"Here's the summary of the Excel data: {data_summary}. Now, based on this data, {user_query}"}
            ],
            "max_tokens": 1500  # Modify as per the requirement
        }

        # Make the POST request to OpenAI API
        response = requests.post(url, headers=headers, json=payload)

        # Check if the response is successful
        if response.status_code == 200:
            response_data = response.json()
            # Extract only the content and number of tokens used
            content = response_data['choices'][0]['message']['content']
            total_tokens = response_data['usage']['total_tokens']
            return {
                "success": True,
                "content": content,
                "total_tokens": total_tokens
            }
        else:
            return {"success": False, "error": response.text}

    except Exception as e:
        return {"success": False, "error": str(e)}

