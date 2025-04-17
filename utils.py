import pandas as pd
import json
import os

def load_skills(skills_csv_path='input/skills.csv'):
    """
    Load skills from CSV file and format them.
    
    Args:
        skills_csv_path (str): Path to the skills CSV file
        
    Returns:
        str: Formatted skills list as a string with each skill on a new line with a bullet point
        bool: True if skills were loaded successfully, False otherwise
    """
    try:
        skills_df = pd.read_csv(skills_csv_path)
        skills_list = skills_df['description'].tolist()
        skills_formatted = '\n'.join(f"- {skill}" for skill in skills_list)
        return skills_formatted, True
    except FileNotFoundError:
        print(f"Warning: skills.csv file not found at {skills_csv_path}")
        return None, False
    except KeyError:
        print("Warning: 'description' column not found in skills.csv")
        return None, False

def llm_skills_json_to_dataframe(json_response, story_id=None):
    """
    Convert the JSON response from the Groq API to a pandas DataFrame
    
    Args:
        json_response (str): JSON string from the API response
        story_id (str, optional): The story ID to add to the DataFrame
    
    Returns:
        pandas.DataFrame: DataFrame containing story_id, skills, explanations, ratings, and excerpts
    """
    try:
        # Parse the JSON string if it's not already a dictionary
        if isinstance(json_response, str):
            data = json.loads(json_response)
        else:
            data = json_response
            
        # Get the story_id from the response or use the provided one
        if 'story_id' in data:
            story_id = data['story_id']
        elif story_id is None:
            raise ValueError("story_id must be provided if not present in the response")
        
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

def save_to_excel(df, filename, sheet_name):
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