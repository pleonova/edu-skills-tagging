import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load data
llm_output = pd.read_excel("output/analysis.xlsx", sheet_name="Skills_Report")
llm_output.rename(columns={'skill': 'description'}, inplace=True)

stories = pd.read_csv("input/stories.csv")
skills = pd.read_csv("input/skills.csv")

# Clean descriptions
llm_output["description"] = llm_output["description"].str.replace(".", "", regex=False).str.strip('"').str.strip()
skills["description"] = skills["description"].str.replace(".", "", regex=False).str.strip('"').str.strip()

# Load embedding model (e.g., MiniLM, which is fast and decent quality)
model = SentenceTransformer("all-MiniLM-L6-v2")

# Embed skills descriptions
skill_embeddings = model.encode(skills["description"].tolist(), convert_to_tensor=True)
skill_embeddings = skill_embeddings.cpu()  # Move to CPU before numpy conversion

# Embed LLM output descriptions
llm_embeddings = model.encode(llm_output["description"].tolist(), convert_to_tensor=True)
llm_embeddings = llm_embeddings.cpu()  # Move to CPU before numpy conversion

# Compute cosine similarity between each llm_output description and all skills
cos_sim_matrix = cosine_similarity(llm_embeddings, skill_embeddings)

# For each LLM output, find index of most similar skill
best_match_indices = cos_sim_matrix.argmax(axis=1)
best_sim_scores = cos_sim_matrix.max(axis=1)

# Add best match info back to llm_output
llm_output["matched_skill_id"] = skills.loc[best_match_indices, "skill_id"].values
llm_output["matched_skill_description"] = skills.loc[best_match_indices, "description"].values
llm_output["similarity_score"] = best_sim_scores

# Merge with stories
df = pd.merge(llm_output, stories, on="story_id", how="left")

# Save to Excel
df.to_excel("output/combined_data_with_similarity.xlsx", index=False)

# Remove hallcuinsations, where the similarity score is less than 0.9
df = df[df["similarity_score"] >= 0.95]

# Rename columns
df.rename(columns={'matched_skill_id': 'skill_id'}, inplace=True)
df.rename(columns={'matched_skill_description': 'ai_skill_description'}, inplace=True)
# Rorder columns
df = df[['skill_id', 'description', 'story_id', 'title', 'story_text', 'story_excerpt', 'explanation', 'rating', 'ai_skill_description', 'similarity_score']]
# Sort resutls by skill_id
df = df.sort_values(by='skill_id')

# Save to Excel
df.to_excel("output/combined_data_final.xlsx", index=False)

print("Combined data with embedding similarity saved to output folder.")
