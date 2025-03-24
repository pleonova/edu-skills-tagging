import pandas as pd


# Read output file
llm_output = pd.read_excel("output/analysis.xlsx", sheet_name="Skills_Report")
llm_output.rename(columns={'skill': 'description'}, inplace=True)
# Read input files
stories = pd.read_csv("input/stories.csv")
skills = pd.read_csv("input/skills.csv")

# Test cases
# Period dicrepency issues
skill_description_text = 'Knows about animal behaviors and diets'
keyword_search = 'animal behaviors'
skill_description_text = 'Knows about leadership, elections, and voting'
keyword_search = 'leadership'
# Missing "the" in the description
skill_description_text = 'Knows about animal life cycle'
keyword_search = 'animal life'
# Keyword is different?
skill_description_text = 'Knows about natural resources'
keyword_search = 'natural resources'


# Then your existing filter
print("\nSkills Dataset - Keyword Search")
print(skills[skills['description'].str.contains(keyword_search, case=False, na=False)].head())
print('--------------------------------')

# Remove period from skills dataset
skills["description"] = skills["description"].str.replace(".", "", regex=False)
skills["description"] = skills["description"].str.strip('"').str.strip()
# Then your existing filter
print("\nSkills Dataset - Keyword Search after removing period:")
print(skills[skills['description'].str.contains(keyword_search, case=False, na=False)].head())
print('--------------------------------')
print("Skills Dataset - Full Text after removing period")
print(skill_description_text)
print(skills[skills['description']==skill_description_text].head())
print('--------------------------------')
print()
print()


# Remove period from llm_output dataset
llm_output["description"] = llm_output["description"].str.replace(".", "", regex=False)
llm_output["description"] = llm_output["description"].str.strip('"').str.strip()
print("LLM Output Dataset")
print(llm_output[llm_output['description']==skill_description_text].head())
print()


# Merge based on 'story_id' and 'description'
df0 = pd.merge(llm_output, stories, on="story_id", how="left")
# Merge based on 'story_id' and 'description'
df = pd.merge(df0, skills, on="description", how="left")

# Rorder columns
# df = df[['skill_id', 'description', 'story_id', 'title', 'story_text', 'story_excerpt', 'explanation', 'rating']]


# Save the result to an Excel file
df.to_excel("output/combined_data.xlsx", index=False)

print(f"Combined data saved to Output Folder")
