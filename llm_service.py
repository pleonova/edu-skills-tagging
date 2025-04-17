import pandas as pd
import json
import os
import time
from groq import Groq
from utils import load_skills


class LLMChat:
    def __init__(self, model="llama3-70b-8192"):
        """
        Initialize the LLMChat class with model configuration.
        
        Args:
            model (str): The model to use for processing
        """
        self.model = model
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def create_skills_prompt(self, story_text, skills_list):
        """
        Create a prompt for skills extraction from a story.
        
        Args:
            story_text (str): Text content of the story
            skills_list (str): Formatted list of skills to use in the prompt
            
        Returns:
            list: List of messages for the LLM
        """
        system_prompt = """You are a helpful teacher that knows how to help students learn. You return answers in JSON format."""
        messages = [{"role": "system", "content": system_prompt}]

        prompt = f"""
        Skills:
        {skills_list}

        Story:
        {story_text}

        Only return the relevant Skills from the list above.
        Make sure to provide a clear explanation why the rating was 9-10 perfect, why parts of it are not well aligned 5-6, or it is very bad alignment 3 or less.
        The same excerpt could have multiple skills and different ratings, separate those out.
        The JSON schema should include:
        {{
            "skill": "skill description", 
            "explanation": "why it is aligned", 
            "story_excerpt": "where in the story to stop to review this skill",
            "rating": 0-10
        }}"""
        
        # Remove indentation from each line
        prompt = '\n'.join(line.lstrip() for line in prompt.split('\n'))

        messages.append({"role": "user", "content": prompt})
        return messages

    @staticmethod
    def _format_instruction(story_text, story_excerpt, skill_description, explanation):
        """
        Format instructions for discussion questions.
        
        Args:
            story_text (str): The story text
            story_excerpt (str): The specific excerpt from the story
            skill_description (str): Description of the skill
            explanation (str): Explanation of the skill alignment
            
        Returns:
            str: Formatted instruction string
        """
        instruction = f"""Given the following story, skill description, and explanation, please provide 3 discussion questions that would be appropriate to assess the skill.
        Story: {story_text}
        Story Excerpt: {story_excerpt}
        Skill Description: {skill_description}
        Explanation: {explanation}

        The questions should:
        1. Assess different levels of understanding (Recall, Comprehension, Application)
        2. Be clear and age-appropriate
        3. Have a clear instructional purpose
        4. Be directly related to the story content
        5. Be directly related to the skill description
        """
        instruction = '\n'.join(line.lstrip() for line in instruction.split('\n'))

        return instruction

    def create_discussion_question_prompt(self, story_text, story_excerpt, skill_description, explanation):
        """
        Create a prompt for generating discussion questions.
        
        Args:
            story_text (str): The story text
            story_excerpt (str): The specific excerpt from the story
            skill_description (str): Description of the skill
            explanation (str): Explanation of the skill alignment
            
        Returns:
            list: List of messages for the LLM
        """
        system_prompt = """You are a helpful teacher that knows how to create effective discussion questions for students. Return the response in JSON format."""
        system_prompt = system_prompt.lstrip()

        prompt = [{"role": "system", "content": system_prompt}] 

        # Load examples from JSON file
        try:
            examples = json.load(open("examples/few_shot_examples_discussion_questions.json"))
            # Add examples to the prompt
            for example in examples:
                example_instructions = self._format_instruction(
                    example['story_text'],
                    example['story_excerpt'],
                    example['skill_description'],
                    example['explanation']
                )
                prompt.append({"role": "user", "content": example_instructions})
                prompt.append({"role": "assistant", "content": json.dumps(example['discussion_questions'], indent=2)})
        except FileNotFoundError:
            print("Warning: Few-shot examples file not found. Proceeding without examples.")

        # Add the current story's instructions
        current_instructions = self._format_instruction(story_text, story_excerpt, skill_description, explanation)
        prompt.append({"role": "user", "content": current_instructions})

        return prompt

    def apply_custom_tooling_for_discussion_question_prompt(self):
        """
        Get the tools configuration for GPT-4 function calling.
        
        Returns:
            dict: Tools configuration for GPT-4
        """
        return {
            "tool_choice": "required",
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "create_discussion_questions",
                        "description": "Create discussion questions for a story",   
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "questions": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "question": {
                                                "type": "string",
                                                "description": "The discussion question text"
                                            },
                                            "type": {
                                                "type": "string",
                                                "enum": ["Recall", "Comprehension", "Application"],
                                                "description": "The type of question based on Bloom's taxonomy"
                                            },
                                            "instructional_purpose": {
                                                "type": "string",
                                                "description": "The purpose of the question in assessing the skill"
                                            }
                                        },
                                        "required": ["question", "type", "instructional_purpose"]
                                    }
                                }
                            },
                            "required": ["questions"]
                        }
                    }
                }
            ]
        }

    def get_model_params(self, messages, response_format={"type": "json_object"}):
        """
        Get the model parameters for the API call.
        
        Args:
            messages (list): List of messages for the model
            response_format (dict): Format for the response
            
        Returns:
            dict: Parameters for the model API call
        """
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.01,
            "max_tokens": 4096,
            "top_p": 0.95,
            "stop": None,
            "seed": 123,
            "response_format": response_format
        }

        return params

    def _print_messages(self, messages):
        """
        Helper method to print messages being sent to the model.
        
        Args:
            messages (list): List of messages to print
        """
        print("\n=== Messages being sent to the model ===")
        for i, msg in enumerate(messages, 1):
            print(f"\nMessage {i} ({msg['role']}):")
            print("-" * 80)
            print(msg['content'])
            print("-" * 80)
        print("\n" + "=" * 80 + "\n")

    def call_model(self, prompt_function, *args, params=None, print_messages=False, max_retries=3):
        """
        Call the model with the given prompt function and arguments.
        
        Args:
            prompt_function (callable): Function that generates the prompt messages
            *args: Arguments to pass to the prompt function
            params (dict, optional): Additional parameters for the model call
            print_messages (bool, optional): Whether to print the messages being sent to the model
            max_retries (int, optional): Maximum number of retries for JSON parsing failures
            
        Returns:
            dict: The model's response
        """
        messages = prompt_function(*args)
        if print_messages:
            self._print_messages(messages)
        
        base_params = self.get_model_params(messages)
        if params:
            base_params.update(params)
        
        for attempt in range(max_retries):
            try:
                completion = self.client.chat.completions.create(**base_params)
                response = completion.choices[0].message.content
                return json.loads(response)
            except json.JSONDecodeError as e:
                print(f"Attempt {attempt + 1}/{max_retries}: Error parsing JSON response: {str(e)}")
                if attempt < max_retries - 1:
                    print("Retrying after a short delay...")
                    time.sleep(1)  # Add a small delay between retries
                else:
                    print("Max retries reached. Returning None.")
                    return None
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
                return None

# Example usage
if __name__ == "__main__":

    # Constants
    separator = "#" * 80

    # Initialize the llm_chat class
    llm_chat = LLMChat()
    
    # Example story and skills
    story_id = "sample-7-1978-4243-85a9-5f788bfb5ecd"
    story_text = "Some days, Dad and I go in the car. Dad drives. I ride. Some days, Dad and I go on the train. I ride. But Dad does not drive the train. Dad rides too. The family is going on a vacation. Can they take the car? No, the car is too small. Can they take the train? Yes, it is just right. All of the family can go on the vacation."
    skills_list, success = load_skills()
    if not success:
        print("Error: Failed to load skills list")
        exit(1)
    
    # First, generate skills from the story
    print(separator)
    print("Generating skills from story...")
    print(separator)
    skills_result = llm_chat.call_model(
        llm_chat.create_skills_prompt,
        story_text,
        skills_list,
        print_messages=True
    )
    print("Skills Result:")
    print(json.dumps(skills_result, indent=2))
    print("\n\n\n\n")

    # Then, for each skill found with rating >= 9, generate discussion questions
    if skills_result and isinstance(skills_result, dict) and "skills" in skills_result:
        print(separator)
        print("Generating discussion questions for high-rated skills (rating > 8)...")
        print(separator)
        for skill in skills_result["skills"]:
            if skill.get("rating", 0) > 8:
                print(f"\nGenerating questions for skill: {skill['skill']} (Rating: {skill['rating']})")
                discussion_result = llm_chat.call_model(
                    llm_chat.create_discussion_question_prompt,
                    story_text,
                    skill['story_excerpt'],
                    skill['skill'],
                    skill['explanation'],
                    print_messages=True
                )
                print("Discussion Questions:")
                print(json.dumps(discussion_result, indent=2))
            else:
                print(f"\nSkipping skill: {skill['skill']} (Rating: {skill['rating']})")
    else:
        print("No skills were generated from the story.")
