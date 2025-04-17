# Setup
import json
import os
import random
import urllib.parse
from datetime import datetime

import requests
import pandas as pd
from utils import llm_skills_json_to_dataframe, save_to_excel, load_skills
from llm_service import LLMChat

# Initialize LLMChat
llm_chat = LLMChat()

def generate_skills_per_story(story_id, story_text, model="llama3-70b-8192"):
    """
    Process a single story through the LLMChat service and save results to Excel
    
    Args:
        story_id (str): The ID of the story
        story_text (str): The text content of the story
        model (str): The model to use for processing (defaults to llama3-70b-8192)
    
    Returns:
        pandas.DataFrame: DataFrame containing the processed results
    """
    # Load skills list
    skills_list, success = load_skills()
    if not success:
        print(f"Error: Failed to load skills list for story {story_id}")
        return None
    
    # Call LLM service
    response = llm_chat.call_model(
        llm_chat.create_skills_prompt,
        story_text,
        skills_list,
        print_messages=False
    )
    
    if response is None:
        print(f"Failed to process story {story_id}")
        return None
        
    print(response)
    
    # Convert to DataFrame and save
    df = llm_skills_json_to_dataframe(response, story_id=story_id)
    
    save_to_excel(df, filename='output/analysis.xlsx', sheet_name='Skills_Report')
    
    return df

def process_stories_for_skills(stories_file='input/stories.csv'):
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
        # stories_df = stories_df.sample(n=2)
        
        # Verify required columns exist
        if not all(col in stories_df.columns for col in ['story_id', 'story_text']):
            raise KeyError("CSV must contain 'story_id' and 'story_text' columns")
        
        # Process each story
        for _, row in stories_df.iterrows():
            story_id = row['story_id']
            story_text = row['story_text']
            
            try:
                print(f"Processing story: {story_id}")
                df = generate_skills_per_story(story_id, story_text)
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

def pretty_print_results(results_df):
    """
    Pretty print the results in a readable format
    
    Args:
        results_df (pandas.DataFrame): DataFrame containing the processed results
    """
    if results_df is None:
        print("No results to display")
        return
        
    print("\n=== Skills Analysis Results ===")
    print(f"Total stories processed: {len(results_df['story_id'].unique())}")
    print(f"Total skills analyzed: {len(results_df)}")
    print("\nDetailed Results:")
    print("-" * 80)
    
    for story_id in results_df['story_id'].unique():
        story_skills = results_df[results_df['story_id'] == story_id]
        print(f"\nStory ID: {story_id}")
        print("-" * 40)
        
        for _, row in story_skills.iterrows():
            print(f"\nSkill: {row['skill']}")
            print(f"Rating: {row['rating']}/10")
            print(f"Explanation: {row['explanation']}")
            print(f"Story Excerpt: {row['story_excerpt']}")
            print("-" * 40)

if __name__ == "__main__":
    # Process all stories
    try:
        results_df = process_stories_for_skills()
        if results_df is not None:
            pretty_print_results(results_df)
    except Exception as e:
        print(f"Error during processing: {str(e)}")
