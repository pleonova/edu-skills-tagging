# Educational Intervention Skill Tagging

## Overview
This app analyzes educational text passages to identify optimal learning intervention points by mapping text content to specific educational skills and competencies. The system employs Large Language Models (LLMs) to perform intelligent skill mapping and rating.

## User Interface
![User Interface Mock](diagrams/user_interface_mock.jpg)

## System Design and Methodology

### Key Design Choices

#### 1. Skill-Based Analysis Framework
- Implemented a comprehensive skills taxonomy covering 69 distinct educational competencies
- Skills span multiple domains including:
  - Science (e.g., plant/animal life, physics, earth science)
  - Social Studies (e.g., community roles, history, geography)
  - Language Arts
  - Mathematics
  - Arts and Physical Education
  - Digital Literacy

#### 2. AI-Powered Assessment
- Utilizes the Groq LLM API with the llama3-70b-8192 model
- Structured JSON output format for consistent analysis
- Low temperature setting (0.01) to ensure consistent, deterministic responses
- Response includes:
  - Skill identification
  - Alignment rating (0-10 scale)
  - Detailed pedagogical explanation
  - Relevant text excerpt mapping

#### 3. Intervention Point Detection
The system determines suitable learning intervention moments by:
- Identifying text segments that strongly align with specific skills (ratings 9-10)
- Capturing partial skill alignment opportunities (ratings 5-6)
- Providing context for why certain passages are pedagogically meaningful
- Mapping multiple skills to the same text segment where appropriate

### Technical Implementation
- Python-based processing pipeline
- Structured prompt engineering for consistent LLM responses
- DataFrame-based results storage for analysis
- Joining to datasets using embeddings to remove any hallucinations
- Excel report generation for easy review and sharing

### Instructions for how to run the code
- Make sure that you have sign up for groq and gotten a free API key 
- Create a virtual environment using the requirements.txt
- run files run_01.. and then run_02


### Human Review Integration & Quality Control

#### Feedback-Informed Few-Shot Learning
We would construct a reference dataset containing examples with human feedback. This dataset would be used for few-shot prompting to guide the AI toward more aligned outputs.

#### Evaluation with Human Ratings
A randomized subset of outputs would be selected as a test set. Multiple reviewers would rate these outputs based on their agreement with the AI's decisions. These ratings would be used to benchmark model performance across various prompt strategies.

#### Prompt Optimization and Edge Case Analysis
By comparing AI outputs to human ratings, we would iterate on prompt engineering to increase alignment. Edge cases where the AI underperforms would be flagged for deeper discussion, potentially revealing categories of tasks or skills that are inherently more difficult for the model.

#### LLM-as-a-Judge for Scalable Evaluation
To reduce human review burden in the long term, we would train or fine-tune an LLM-as-a-judge model using the labeled dataset. This model would act as a proxy evaluator for future iterations.

#### Lightweight A/B Testing
In scenarios with limited review capacity, A/B testing serves as an effective low-touch evaluation method. For example, by comparing cohorts receiving different AI-generated interventions, we can assess performance and engagement outcomes to infer alignment and utility.


### Planned Improvements
- [ ] Enhance LLM output validation and error handling
- [ ] Implementation of a LLM-as-a-Judge review system for quality control
- [ ] Development of a dynamic highlighting system based on skill ratings
- [ ] Integration of student engagement metrics for intervention optimization
- [ ] Identify certain skill dependencies
