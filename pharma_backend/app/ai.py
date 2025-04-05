import requests
import json
from typing import List, Optional
from .config import settings
from .schemas import AIPlanRequest, AIChatRequest
from datetime import datetime, timedelta

class AIService:
    def __init__(self):
        self.api_key = settings.openrouter_api_key
        self.site_url = settings.site_url
        self.site_name = settings.site_name

    def generate_study_plan(self, plan_request: AIPlanRequest) -> dict:
        prompt = f"""
        Create a detailed study plan for pharmacology with the following requirements:
        - Goal: {plan_request.goal}
        - Duration: {plan_request.duration_weeks} weeks
        - Intensity: {plan_request.intensity}
        - Topics: {', '.join(plan_request.topics)}
        {f"- Materials: {plan_request.materials}" if plan_request.materials else ""}

        The plan should include:
        1. Weekly breakdown with specific topics to cover
        2. Recommended study hours per week
        3. Suggested resources and materials
        4. Study techniques for each topic
        5. Self-assessment recommendations

        Format the response as a JSON object with the following structure:
        {{
            "title": "Generated Study Plan",
            "goal": "...",
            "duration_weeks": ...,
            "intensity": "...",
            "weekly_breakdown": [
                {{
                    "week": 1,
                    "topics": ["..."],
                    "study_hours": ...,
                    "resources": ["..."],
                    "techniques": ["..."],
                    "assessments": ["..."]
                }}
            ],
            "recommendations": {{
                "optimal_times": "...",
                "additional_tips": "..."
            }}
        }}
        """
        
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": self.site_url,
                "X-Title": self.site_name,
            },
            data=json.dumps({
                "model": "openai/gpt-4",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert pharmacology tutor that creates detailed, personalized study plans."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "response_format": { "type": "json_object" }
            })
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"AI service error: {response.text}")

    def chat_assistant(self, chat_request: AIChatRequest) -> str:
        messages = [
            {
                "role": "system",
                "content": """You are a pharmacology expert AI assistant. Help students with:
                - Explaining drug mechanisms
                - Study plan recommendations
                - Answering pharmacology questions
                - Creating flashcards and quizzes
                - Providing mnemonics and memory aids
                
                Be concise but thorough. Use markdown for formatting when helpful.
                """
            }
        ]
        
        if chat_request.context:
            messages.append({
                "role": "system",
                "content": f"Context: {chat_request.context}"
            })
            
        messages.append({
            "role": "user",
            "content": chat_request.message
        })
        
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": self.site_url,
                "X-Title": self.site_name,
            },
            data=json.dumps({
                "model": "openai/gpt-4",
                "messages": messages
            })
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"AI chat error: {response.text}")

    def analyze_study_materials(self, text: str) -> dict:
        prompt = f"""
        Analyze these pharmacology study materials and extract key information:
        
        {text}
        
        Provide a structured analysis with:
        1. Main topics covered
        2. Key concepts and definitions
        3. Important drug classifications
        4. Mechanisms of action
        5. Clinical applications
        6. Potential study questions
        
        Format as JSON with this structure:
        {{
            "topics": ["..."],
            "key_concepts": ["..."],
            "drug_classifications": ["..."],
            "mechanisms": ["..."],
            "clinical_applications": ["..."],
            "study_questions": ["..."]
        }}
        """
        
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": self.site_url,
                "X-Title": self.site_name,
            },
            data=json.dumps({
                "model": "openai/gpt-4",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "response_format": { "type": "json_object" }
            })
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"Material analysis error: {response.text}")