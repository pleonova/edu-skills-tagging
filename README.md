# 📚 Educational Intervention Skill Tagging

## Overview

This application analyzes educational text passages to identify optimal intervention points by mapping content to specific academic skills and providing targeted discussion questions for follow-up learning. It uses large language models (LLMs) to intelligently detect, rate, and explain skill alignment—helping educators personalize instruction and improve learning outcomes.

---

## Sample Output

![User Interface Mock](diagrams/ui_mock.jpg)

See full output here: **[output/combined_data_final.xlsx](output/combined_data_final.xlsx)**

---

## 🧠 System Design & Methodology

### 🧩 1. Skill-Based Analysis Framework

- Uses a comprehensive taxonomy of **69 educational competencies**
- Skills span a wide range of domains:
  - **Science** (e.g., life sciences, physics, earth science)
  - **Social Studies** (e.g., history, geography, civics)
  - **Language Arts**
  - **Mathematics**
  - **Arts & Physical Education**
  - **Digital Literacy**

---

### 🤖 2. AI-Powered Skill Assessment

- Powered by **Groq LLM API (llama3-70b-8192)**
- Uses structured prompt templates to ensure consistency
- **Low temperature (0.01)** for deterministic, repeatable outputs

Each model response includes:
- Identified **skill tag(s)**
- **Alignment rating** (scale of 0–10)
- Pedagogical **explanation**
- Highlighted **text excerpt** supporting the alignment

---

### 🎯 3. Intervention Point Detection

The system pinpoints passages that:
- **Strongly align** with specific skills (ratings: 9–10)
- Show **partial alignment** or emerging understanding (ratings: 5–6)
- Offer opportunities for teacher-led **discussion or review**
- **Map multiple skills** to the same passage when relevant

### 💬 4. Follow up Discussion

The system generates targeted discussion points that:
- **Reinforce key concepts** through guided questioning
- **Connect skills** across different subject areas
- **Promote critical thinking** with open-ended prompts
- **Support differentiated instruction** with varying difficulty levels

---

## 🛠️ Technical Implementation

- Python-based processing pipeline
- Structured prompt engineering - JSON Output
- Various Pompt Techniques (RAG, Few-Shot, Tooling, Chaining)
- LLM output stored and analyzed using DataFrames
- Embedding-based dataset joins to reduce hallucinations
- Final output: Excel reports for easy review & collaboration

### ▶️ How to Run

1. Sign up at [Groq](https://groq.com) and obtain a free API key.

2. Set up your environment variable:
   ```bash
   export GROQ_API_KEY='your-api-key-here'
   ```
   
3. Set up the virtual environment:

   ```bash
   # Create a new virtual environment
   python -m venv skill-venv
   
   # Activate the virtual environment
   source skill-venv/bin/activate  # On macOS/Linux
   # or
   .\skill-venv\Scripts\activate  # On Windows
   
   # Install dependencies
   pip install -r requirements.txt
   ```

4. Run the skill alignment script:
   ```bash
   python run_01_align_skills_to_stories.py
   ```
   This will process the stories and generate skill alignments.

5. Combine the data:
   ```bash
   python run_02_combine_data.py
   ```
   This will generate the final combined output.

6. (Optional) Generate discussion questions:
   ```bash
   python run_03_generate_discussion_questions.py
   ```
   This will create additional discussion questions based on the aligned skills.

The final outputs will be available in the `output/` directory:
- **combined_data_final.xlsx**: Main output with skill alignments
- **discussion_questions.xlsx**: Secondary output with associated questions for skill discussion

#### 🤖 LLM Service Implementation

The `llm_service.py` file provides a robust implementation for processing educational content using the Groq LLM API. Here's a detailed breakdown of its functionality:

1. **Key Prompt Components**:
   - **Skills Augmented Analysis**: Analyzes text passages to identify and rate educational skills
   - **Discussion Generation**: Creates targeted questions based on identified skills
   - **Custom Tooling**: Supports GPT-4 function calling for structured outputs
   - **Few-Shot Learning**: Uses example-based prompting for better results

2. **Output Structure & Sample Output**:
   - **Skills Analysis Output Structure**:
     ```json
     {
       "skills": [
         {
           "skill": "skill description",
           "explanation": "why it is aligned",
           "story_excerpt": "where in the story to stop to review this skill",
           "rating": 0-10
         }
       ]
     }
     ```
     Skills Result Sample Output:
     ```json
     {
       "skills": [
         {
           "skill": "Knows about transportation",
           "explanation": "The story mentions going in a car and on a train, showing an understanding of different modes of transportation.",
           "story_excerpt": "Some days, Dad and I go in the car. Dad drives. I ride. Some days, Dad and I go on the train.",
           "rating": 10
         }
       ]
     }
     ```
   - **Discussion Questions Output Structure**:
     ```json
     [
       {
         "question": "question text",
         "type": "Recall/Comprehension/Application",
         "instructional_purpose": "purpose of the question"
       }
     ]
     ```
     Discussion Questions Sample Output:
     ```json
     {
       "questions": [
         {
           "question": "What are two ways the family travels?",
           "type": "Recall",
           "instructional_purpose": "Assess whether the student can recall the modes of transportation mentioned in the story."
         },
         {
           "question": "Why did the family choose to take the train for their vacation?",
           "type": "Comprehension",
           "instructional_purpose": "Assess whether the student understands the reason behind the family's transportation choice."
         },
         {
           "question": "What other ways can people travel besides cars and trains?",
           "type": "Application",
           "instructional_purpose": "Requires the student to think about other modes of transportation beyond what was mentioned in the story."
         }
       ]
     }
     ```

3. **Quality Control**:
   - **Prompt Templates**: Implements structured prompt templates
   - **Validation**: Uses JSON schema validation
   - **Error Handling**: Includes comprehensive error handling and retry mechanisms
   - **Debugging**: Supports debugging through message printing

4. **Sample Usage**:
   ```python llm_service.py
   ```

To see a sample output for one story, checkout the `output/sample_prompt_chain.txt` file, which demonstrates the full processing pipeline from story analysis to question generation.



---

## 🧪 Human Review & Quality Control

### 🧷 Feedback-Informed Few-Shot Learning
- Create a reference dataset with human-reviewed examples.
- Use these examples as few-shot prompts to guide and improve LLM output quality.

### 🔍 Evaluation with Human Ratings
- Randomly sample and review LLM-generated outputs.
- Human raters evaluate skill alignment, clarity, and pedagogical value.

### 🧠 Prompt Optimization & Edge Case Analysis
- Compare human and model ratings to fine-tune prompts.
- Identify skill categories or content formats where the model underperforms.

### 🤖 LLM-as-a-Judge for Scalable Review
- Fine-tune a model to serve as a proxy reviewer.
- Helps reduce reliance on manual reviews for future outputs.

### 🧪 Lightweight A/B Testing
- Run controlled comparisons of LLM-generated interventions.
- Use engagement or comprehension metrics to assess effectiveness.

---

## 📈 Planned Improvements

- [ ] Improve LLM output validation and error handling  
- [ ] Implement a scalable **LLM-as-a-Judge** system for reviews  
- [x] Add another prompt for skills assessment
- [ ] Add dynamic **text highlighting** based on skill strength  
- [ ] Integrate **student engagement metrics** for optimization  
- [ ] Visualize and track **skill dependencies** across stories  
