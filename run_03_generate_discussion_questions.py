import pandas as pd
from llm_service import LLMChat
import json
from tqdm import tqdm
from utils import save_to_excel


# Initialize LLMChat
llm_chat = LLMChat()

def generate_discussion_questions(story_id, story_data, llm_chat):
    """
    Process a single story to generate discussion questions
    
    Args:
        story_id (str): The ID of the story
        story_data (dict): Dictionary containing story data
        llm_chat (LLMChat): Initialized LLMChat instance
    
    Returns:
        pandas.DataFrame: DataFrame containing the generated discussion questions
    """
    if story_data.get("rating", 0) <= 8:  # Skip low-rated skills
        print(f"Skipping story {story_id} due to low rating")
        return None
        
    try:
        print(f"\nProcessing story {story_id}...")
        discussion_result = llm_chat.call_model(
            llm_chat.create_discussion_question_prompt,
            story_data["story_text"],
            story_data["story_excerpt"],
            story_data["description"],
            story_data["explanation"],
            print_messages=False
        )
        
        print(f"Raw LLM response for story {story_id}: {discussion_result}")
        
        # If discussion_result is a string (JSON), parse it
        if isinstance(discussion_result, str):
            discussion_result = json.loads(discussion_result)
        
        # Extract questions from the nested structure
        if isinstance(discussion_result, dict) and 'questions' in discussion_result:
            questions = discussion_result['questions']
        elif isinstance(discussion_result, list) and len(discussion_result) > 0 and 'questions' in discussion_result[0]:
            questions = discussion_result[0]['questions']
        else:
            questions = discussion_result if isinstance(discussion_result, list) else [discussion_result]
        
        print(f"Processed questions for story {story_id}: {questions}")
        
        # Create a list to store results
        results = []
        
        # Add each question as a separate row
        for question_data in questions:
            results.append({
                "story_id": story_id,
                "title": story_data["title"],
                "story_text": story_data["story_text"],
                "skill_id": story_data["skill_id"],
                "description": story_data["description"],
                "story_excerpt": story_data["story_excerpt"],
                "explanation": story_data["explanation"],
                "question": question_data.get("question", ""),
                "type": question_data.get("type", ""),
                "instructional_purpose": question_data.get("instructional_purpose", "")
            })
        
        # Convert to DataFrame
        df = pd.DataFrame(results)
        print(f"Created DataFrame with {len(df)} rows for story {story_id}")
        return df
        
    except Exception as e:
        print(f"Error processing story {story_id}: {e}")
        import traceback
        traceback.print_exc()
        return None

def process_stories_for_discussion_questions(input_file="output/combined_data_final.xlsx"):
    """
    Process all stories from the Excel file and generate discussion questions
    
    Args:
        input_file (str): Path to the input Excel file
    
    Returns:
        pandas.DataFrame: Combined DataFrame of all processed stories
    """
    print(f"Reading data from {input_file}...")
    df = pd.read_excel(input_file)
    df = df.sample(n=10)
    
    
    # Process each row
    print("Generating discussion questions...")
    for _, row in tqdm(df.iterrows(), total=len(df)):
        story_id = row["story_id"]
        try:
            # Generate questions for this story
            questions_df = generate_discussion_questions(story_id, row, llm_chat)
            
            if questions_df is not None:
                print(f"Saving results for story {story_id}...")
                # Save results incrementally
                save_to_excel(questions_df, "output/discussion_questions.xlsx", "questions")
                print(f"Saved discussion questions for story {story_id}")
            else:
                print(f"No questions generated for story {story_id}")
            
        except Exception as e:
            print(f"Error processing story {story_id}: {str(e)}")
            continue

def pretty_print_results(results_df):
    """
    Pretty print the results in a readable format
    
    Args:
        results_df (pandas.DataFrame): DataFrame containing the processed results
    """
    if results_df is None:
        print("No results to display")
        return
        
    print("\n=== Discussion Questions Results ===")
    print(f"Total stories processed: {len(results_df['story_id'].unique())}")
    print(f"Total questions generated: {len(results_df)}")
    print("\nDetailed Results:")
    print("-" * 80)
    
    for story_id in results_df['story_id'].unique():
        story_questions = results_df[results_df['story_id'] == story_id]
        print(f"\nStory ID: {story_id}")
        print("-" * 40)
        
        for _, row in story_questions.iterrows():
            print(f"\nQuestion: {row['question']}")
            print(f"Type: {row['type']}")
            print(f"Instructional Purpose: {row['instructional_purpose']}")
            print("-" * 40)

if __name__ == "__main__":
    # Process all stories
    try:
        process_stories_for_discussion_questions()
        print("Processing complete!")
    except Exception as e:
        print(f"Error during processing: {str(e)}")