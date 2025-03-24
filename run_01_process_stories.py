# Setup
import json
import os
import random
import urllib.parse
from datetime import datetime

import requests
from groq import Groq
import pandas as pd
from create_skills_extraction_prompt import skills_prompt

# Initialize Groq client and model
client = Groq(api_key=os.getenv("GROQ_API_KEY")) 
MODEL = "llama3-70b-8192"


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


def process_story(story_id, story_text, model=MODEL):
    """
    Process a single story through the Groq API and save results to Excel
    
    Args:
        story_id (str): The ID of the story
        story_text (str): The text content of the story
        model (str): The model to use for processing (defaults to MODEL constant)
    
    Returns:
        pandas.DataFrame: DataFrame containing the processed results
    """
    system_message = """
    You are a helpful teacher that knows how to help students learn. You return answers in JSON format.
    """

    # Generate prompt
    user_prompt = skills_prompt(story_id, story_text)
    
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_prompt},
    ]

    # Call API
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.01,
        max_tokens=4096,
        top_p=0.95,
        stop=None,
        seed=123,
        response_format={"type": "json_object"}
    )

    response = completion.choices[0].message.content
    print(response)
    
    # Convert to DataFrame and save
    df = json_to_dataframe(response)
    save_to_excel(df, filename='output/analysis.xlsx', sheet_name='Skills_Report')
    
    return df


def process_all_stories(stories_file='input/stories.csv'):
    """
    Process all stories from the CSV file
    
    Args:
        stories_file (str): Path to CSV file containing stories
    
    Returns:
        pandas.DataFrame: Combined DataFrame of all processed stories
    """
    if not os.path.exists(stories_file):
        raise FileNotFoundError(f"Stories file '{stories_file}' not found")
    
    all_results = []
    
    try:
        # Read the stories CSV file
        stories_df = pd.read_csv(stories_file)
        # Select a random sample of 10 stories
        # stories_df = stories_df.sample(n=10)
        
        # Verify required columns exist
        if not all(col in stories_df.columns for col in ['story_id', 'story_text']):
            raise KeyError("CSV must contain 'story_id' and 'story_text' columns")
        
        # Process each story
        for _, row in stories_df.iterrows():
            story_id = row['story_id']
            story_text = row['story_text']
            
            try:
                print(f"Processing story: {story_id}")
                df = process_story(story_id, story_text)
                if df is not None:
                    all_results.append(df)
                else:
                    print(f"No results for story: {story_id}")
                print()
                print()
                
            except Exception as e:
                print(f"Error processing story {story_id}: {str(e)}")
    
    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")
        return None
    
    # Combine all results
    if all_results:
        final_df = pd.concat(all_results, ignore_index=True)
        return final_df
    return None


if __name__ == "__main__":
    # Process all stories
    try:
        results_df = process_all_stories()
        if results_df is not None:
            print("\nProcessing complete!")
            print(f"Total stories processed: {len(results_df['story_id'].unique())}")
            print(f"Total skills analyzed: {len(results_df)}")
    except Exception as e:
        print(f"Error during processing: {str(e)}")
