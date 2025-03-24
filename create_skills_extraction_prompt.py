import pandas as pd

def skills_prompt(story_id, story_text):
    # Read skills from CSV file
    try:
        skills_df = pd.read_csv('data/skills.csv')
        skills_list = skills_df['description'].tolist()
        skills_formatted = '\n'.join(f"- {skill}" for skill in skills_list)
    except FileNotFoundError:
        raise FileNotFoundError("skills.csv file not found in data directory")
    except KeyError:
        raise KeyError("'description' column not found in skills.csv")

    # Create the prompt with proper formatting
    prompt = f"""Skills:
{skills_formatted}

Story ID: {story_id}
{story_text}

Only return the relevant Skills from the list above.
Make sure to provide a clear explanation why the rating was 9-10 perfect, why parts of it are not well aligned 5-6, or it is very bad alignment 3 or less.
The same excerpt could have multiple skills and different ratings, separate those out.
The JSON schema should include:
{{
    "story_id": "sample",
    "skill": "skill description", 
    "explanation": "why it is aligned", 
    "story_excerpt": "where in the story to stop to review this skill",
    "rating": 0-10
}}"""

    return prompt

if __name__ == "__main__":
    # Example usage
    story_id = "sample-7-1978-4243-85a9-5f788bfb5ecd"
    story_text = "Some days, Dad and I go in the car. Dad drives. I ride. Some days, Dad and I go on the train. I ride. But Dad does not drive the train. Dad rides too. The family is going on a vacation. Can they take the car? No, the car is too small. Can they take the train? Yes, it is just right. All of the family can go on the vacation."

    prompt = skills_prompt(story_id, story_text)
    print(prompt)
