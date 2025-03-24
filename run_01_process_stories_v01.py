# Setup
import json
import os
import random
import urllib.parse
from datetime import datetime

import requests
from groq import Groq
import pandas as pd

# Initialize Groq client and model
client = Groq(api_key=os.getenv("GROQ_API_KEY")) 
# MODEL = "deepseek-r1-distill-llama-70b"
MODEL = "llama3-70b-8192"

SYSTEM_MESSAGE = """
You are a helpful teacher that knows how to help students learn. You return answers in JSON format.
"""

# Read prompt from demo_prompt1.txt
with open('demo-prompt.txt', 'r') as file:
    USER_PROMPT = file.read()


MESSAGES = [
    {"role": "system", "content": SYSTEM_MESSAGE},
    {"role": "user","content": USER_PROMPT},
]

# Call with streaming
completion = client.chat.completions.create(
    model=MODEL,
    messages=MESSAGES,
    temperature=0.01,
    max_tokens=4096,
    top_p=0.95,
    stop=None,
    seed=123,
    response_format = {"type": "json_object"} 
)

response = completion.choices[0].message.content
print(response)

def json_to_dataframe(json_response):
    """
    Convert the JSON response from the Groq API to a pandas DataFrame
    
    Args:
        json_response (str): JSON string from the API response
    
    Returns:
        pandas.DataFrame: DataFrame containing story_id, skills, explanations, ratings, and excerpts
    """
    try:
        # Parse the JSON string if it's not already a dictionary
        if isinstance(json_response, str):
            data = json.loads(json_response)
        else:
            data = json_response
            
        # Get the story_id
        story_id = data['story_id']
        
        # Convert the skills list to a DataFrame
        df = pd.DataFrame(data['skills'])
        
        # Add story_id column
        df['story_id'] = story_id
        
        # Reorder columns to put story_id first
        columns_order = ['story_id', 'skill', 'explanation', 'story_excerpt', 'rating']
        df = df[columns_order]
        
        return df
    
    except Exception as e:
        print(f"Error converting to DataFrame: {str(e)}")
        return None

# Use the function with your API response
df = json_to_dataframe(response)

def save_to_excel(df, filename='analysis.xlsx', sheet_name='Skills_Report'):
    """
    Save DataFrame to Excel:
    - If file/sheet doesn't exist: create new file and sheet
    - If file/sheet exists: append data to existing sheet
    
    Args:
        df: pandas DataFrame to save
        filename: name of the Excel file
        sheet_name: name of the sheet
    """
    try:
        if not os.path.exists(filename):
            # Create new file and sheet if doesn't exist
            df.to_excel(filename, sheet_name=sheet_name, index=False)
            print(f"Created new file '{filename}' with sheet '{sheet_name}'")
        else:
            # File exists, try to load existing sheet
            try:
                existing_df = pd.read_excel(filename, sheet_name=sheet_name)
                # Append new data to existing data
                combined_df = pd.concat([existing_df, df], ignore_index=True)
                
                # Save back to file
                with pd.ExcelWriter(filename, mode='a', if_sheet_exists='replace') as writer:
                    combined_df.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"Appended data to existing sheet '{sheet_name}' in '{filename}'")
                
            except ValueError:  # Sheet doesn't exist
                # Append new sheet to existing file
                with pd.ExcelWriter(filename, mode='a') as writer:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"Created new sheet '{sheet_name}' in existing file '{filename}'")
                
    except Exception as e:
        print(f"Error saving to Excel: {str(e)}")

# Use the function
save_to_excel(df, filename='analysis.xlsx', sheet_name='Skills_Report')


# print("Response:")
# for chunk in completion:
#     if chunk.choices[0].delta.content:
#         print(chunk.choices[0].delta.content, end="", flush=True)
