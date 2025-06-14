# Career Preference System - Complete Implementation

import json
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import openai
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import OpenAIEmbeddings
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

@dataclass
class CareerPreferences:
    interests: List[str]
    skills: List[str]
    values: List[str]
    work_environment: List[str]
    subjects_enjoyed: List[str]
    hobbies: List[str]
    personality_traits: List[str]
    career_goals: List[str]
    dislikes: List[str]
    confidence_score: int

@dataclass
class CareerRecommendation:
    category: str
    subcategory: str
    alignment_score: int
    matching_factors: List[str]
    potential_concerns: List[str]
    explanation: str

# Career paths database
CAREER_PATHS = {
    "STEM": {
        "subcategories": [
            "Software Engineering", "Data Science", "Biomedical Research",
            "Environmental Science", "Mechanical Engineering", "Mathematics",
            "Physics Research", "Cybersecurity"
        ],
        "key_indicators": [
            "problem-solving", "analytical thinking", "mathematics", "technology",
            "research", "experimentation", "logical reasoning", "coding", "algorithms"
        ]
    },
    "Arts & Creative": {
        "subcategories": [
            "Graphic Design", "Music Production", "Writing & Literature",
            "Film & Media", "Fine Arts", "Architecture", "Fashion Design", "Game Design"
        ],
        "key_indicators": [
            "creativity", "artistic expression", "visual design", "storytelling",
            "aesthetics", "imagination", "cultural appreciation", "drawing", "music"
        ]
    },
    "Sports & Fitness": {
        "subcategories": [
            "Professional Athletics", "Sports Coaching", "Physical Therapy",
            "Sports Medicine", "Fitness Training", "Sports Management"
        ],
        "key_indicators": [
            "physical activity", "competition", "team sports", "fitness",
            "athletics", "coaching", "health and wellness", "exercise"
        ]
    },
    "Business & Entrepreneurship": {
        "subcategories": [
            "Marketing", "Finance", "Consulting", "Sales", "Operations Management",
            "Startup Founder", "Investment Banking", "Business Development"
        ],
        "key_indicators": [
            "leadership", "profit-driven", "networking", "strategic thinking",
            "risk-taking", "negotiation", "market analysis", "management"
        ]
    },
    "Healthcare & Medicine": {
        "subcategories": [
            "Medicine", "Nursing", "Psychology", "Pharmacy", "Public Health",
            "Medical Research", "Therapy", "Healthcare Administration"
        ],
        "key_indicators": [
            "helping others", "empathy", "science interest", "patient care",
            "health advocacy", "medical knowledge", "crisis management", "biology"
        ]
    },
    "Education & Social Services": {
        "subcategories": [
            "Teaching", "Social Work", "Counseling", "Educational Administration",
            "Community Development", "Non-profit Leadership", "Policy Making"
        ],
        "key_indicators": [
            "teaching", "mentoring", "social justice", "community service",
            "child development", "public service", "advocacy", "communication"
        ]
    }
}

class CareerPreferenceExtractor:
    def __init__(self, api_key: str = None): # type: ignore
        """Initialize the career preference extractor"""
        if api_key:
            openai.api_key = api_key
        else:
            # Load from environment
            from dotenv import load_dotenv
            load_dotenv()
            openai.api_key = os.getenv('OPENAI_API_KEY')
        
        self.llm = ChatOpenAI(temperature=0.3, model="gpt-3.5-turbo")
        self.embeddings = OpenAIEmbeddings()
        
    def extract_preferences(self, conversation: str) -> CareerPreferences:
        """Extract career preferences from conversation text"""
        
        extraction_prompt = PromptTemplate(
            input_variables=["conversation_text"],
            template="""
            Analyze the following conversation and extract career-related preferences:

            Conversation: "{conversation_text}"

            Extract the following information in JSON format:
            {{
              "interests": [],
              "skills": [],
              "values": [],
              "work_environment_preferences": [],
              "subjects_enjoyed": [],
              "hobbies": [],
              "personality_traits": [],
              "career_goals": [],
              "dislikes": [],
              "confidence_score": 0-100
            }}

            Focus on explicit mentions and implied preferences. Rate confidence based on clarity of expression.
            Return ONLY the JSON, no additional text.
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=extraction_prompt)
        result = chain.run(conversation_text=conversation)
        
        try:
            # Clean the result and parse JSON
            result = result.strip()
            if result.startswith('```json'):
                result = result[7:-3]
            elif result.startswith('```'):
                result = result[3:-3]
            
            data = json.loads(result)
            
            return CareerPreferences(
                interests=data.get('interests', []),
                skills=data.get('skills', []),
                values=data.get('values', []),
                work_environment=data.get('work_environment_preferences', []),
                subjects_enjoyed=data.get('subjects_enjoyed', []),
                hobbies=data.get('hobbies', []),
                personality_traits=data.get('personality_traits', []),
                career_goals=data.get('career_goals', []),
                dislikes=data.get('dislikes', []),
                confidence_score=data.get('confidence_score', 50)
            )
        except json.JSONDecodeError:
            print(f"Error parsing JSON: {result}")
            # Return default preferences
            return CareerPreferences([], [], [], [], [], [], [], [], [], 30)
    
    def map_to_careers(self, preferences: CareerPreferences) -> List[CareerRecommendation]:
        """Map preferences to career recommendations"""
        
        mapping_prompt = PromptTemplate(
            input_variables=["preferences", "career_paths"],
            template="""
            Based on the extracted preferences, recommend the top 3 most suitable career paths:

            Preferences: {preferences}
            Available Paths: {career_paths}

            For each recommendation, provide:
            1. Category and subcategory
            2. Alignment score (0-100)
            3. Matching factors from preferences
            4. Potential concerns or gaps
            5. Brief explanation (2-3 sentences)

            Return as JSON array:
            [
              {{
                "category": "",
                "subcategory": "",
                "alignment_score": 0-100,
                "matching_factors": [],
                "potential_concerns": [],
                "explanation": ""
              }}
            ]
            
            Return ONLY the JSON array, no additional text.
            """
        )
        
        preferences_str = f"""
        Interests: {preferences.interests}
        Skills: {preferences.skills}  
        Values: {preferences.values}
        Work Environment: {preferences.work_environment}
        Subjects: {preferences.subjects_enjoyed}
        Hobbies: {preferences.hobbies}
        Personality: {preferences.personality_traits}
        Goals: {preferences.career_goals}
        Dislikes: {preferences.dislikes}
        """
        
        chain = LLMChain(llm=self.llm, prompt=mapping_prompt)
        result = chain.run(
            preferences=preferences_str,
            career_paths=json.dumps(CAREER_PATHS, indent=2)
        )
        
        try:
            # Clean and parse result
            result = result.strip()
            if result.startswith('```json'):
                result = result[7:-3]
            elif result.startswith('```'):
                result = result[3:-3]
            
            data = json.loads(result)
            
            recommendations = []
            for item in data:
                recommendations.append(CareerRecommendation(
                    category=item.get('category', ''),
                    subcategory=item.get('subcategory', ''),
                    alignment_score=item.get('alignment_score', 0),
                    matching_factors=item.get('matching_factors', []),
                    potential_concerns=item.get('potential_concerns', []),
                    explanation=item.get('explanation', '')
                ))
            
            return recommendations
            
        except json.JSONDecodeError:
            print(f"Error parsing recommendations: {result}")
            return []
    
    def generate_clarification_questions(self, preferences: CareerPreferences) -> List[str]:
        """Generate follow-up questions when confidence is low"""
        
        if preferences.confidence_score >= 70:
            return []
        
        question_prompt = PromptTemplate(
            input_variables=["preferences", "confidence"],
            template="""
            The conversation doesn't provide enough information for confident career recommendations.
            
            Current extracted info: {preferences}
            Confidence score: {confidence}
            
            Generate 2-3 specific clarifying questions that would help improve career recommendations.
            Focus on the most important missing information.
            
            Return as JSON array of strings:
            ["Question 1", "Question 2", "Question 3"]
            
            Return ONLY the JSON array.
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=question_prompt)
        result = chain.run(
            preferences=preferences.__dict__,
            confidence=preferences.confidence_score
        )
        
        try:
            result = result.strip()
            if result.startswith('```json'):
                result = result[7:-3]
            elif result.startswith('```'):
                result = result[3:-3]
            
            return json.loads(result)
        except:
            return [
                "What subjects or activities do you find most engaging?",
                "What type of work environment helps you perform your best?",
                "What does career success look like to you?"
            ]


class CareerGuidanceApp:
    def __init__(self, api_key: str = None): # type: ignore
        self.extractor = CareerPreferenceExtractor(api_key)
        
    def process_conversation(self, conversation: str) -> Dict:
        """Main method to process a conversation and return career guidance"""
        
        print("🔍 Extracting preferences from conversation...")
        preferences = self.extractor.extract_preferences(conversation)
        
        print(f"✅ Extracted preferences (confidence: {preferences.confidence_score}%)")
        
        if preferences.confidence_score < 50:
            print("❓ Low confidence - generating clarification questions...")
            questions = self.extractor.generate_clarification_questions(preferences)
            return {
                "status": "needs_clarification",
                "preferences": preferences.__dict__,
                "questions": questions,
                "recommendations": []
            }
        
        print("🎯 Mapping to career recommendations...")
        recommendations = self.extractor.map_to_careers(preferences)
        
        result = {
            "status": "success",
            "preferences": preferences.__dict__,
            "recommendations": [rec.__dict__ for rec in recommendations],
            "questions": []
        }
        
        if preferences.confidence_score < 70:
            result["questions"] = self.extractor.generate_clarification_questions(preferences)
        
        return result
    
    def print_results(self, results: Dict):
        """Pretty print the results"""
        print("\n" + "="*50)
        print("🎯 CAREER GUIDANCE RESULTS")
        print("="*50)
        
        if results["status"] == "needs_clarification":
            print("\n❓ Need more information. Please answer these questions:")
            for i, question in enumerate(results["questions"], 1):
                print(f"{i}. {question}")
        else:
            print(f"\n📊 Confidence Score: {results['preferences']['confidence_score']}%")
            
            print(f"\n🎨 Interests: {', '.join(results['preferences']['interests'])}")
            print(f"💪 Skills: {', '.join(results['preferences']['skills'])}")
            print(f"⭐ Values: {', '.join(results['preferences']['values'])}")
            
            print(f"\n🚀 TOP CAREER RECOMMENDATIONS:")
            for i, rec in enumerate(results["recommendations"], 1):
                print(f"\n{i}. {rec['category']} - {rec['subcategory']}")
                print(f"   📈 Match Score: {rec['alignment_score']}%")
                print(f"   ✅ Why it fits: {', '.join(rec['matching_factors'])}")
                print(f"   💡 {rec['explanation']}")
                if rec['potential_concerns']:
                    print(f"   ⚠️  Consider: {', '.join(rec['potential_concerns'])}")
            
            if results["questions"]:
                print(f"\n❓ For better recommendations, consider:")
                for question in results["questions"]:
                    print(f"   • {question}")
def main():
    """Example usage of the career guidance system"""
    
    # Initialize the app
    app = CareerGuidanceApp()
    
    # Example conversation
    sample_conversation = """
    I really love working with computers and solving complex problems. 
    In school, I was always good at math and physics. I enjoy coding in my free time 
    and have built a few web applications. I like working independently but also 
    enjoy collaborating with smart people. I want a career where I can keep learning 
    new technologies and maybe eventually start my own company. I don't like routine 
    work or micromanagement. Money is important but I also want to work on something 
    meaningful that could impact many people.
    """
    
    print("🚀 Starting Career Guidance System...")
    print(f"📝 Processing conversation: {sample_conversation[:100]}...")
    
    # Process the conversation
    results = app.process_conversation(sample_conversation)
    
    # Display results
    app.print_results(results)


def interactive_mode():
    """Run the system in interactive mode"""
    
    app = CareerGuidanceApp()
    
    print("🎯 Welcome to Career Guidance System!")
    print("Tell me about your interests, skills, and career goals...")
    print("(Type 'quit' to exit)\n")
    
    conversation = ""
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("👋 Goodbye! Good luck with your career journey!")
            break
        
        conversation += " " + user_input
        
        if len(conversation.split()) > 20:  # Process after sufficient input
            results = app.process_conversation(conversation)
            app.print_results(results)
            
            if results["status"] == "needs_clarification":
                print("\nPlease provide more details...")
                conversation = ""  # Reset for more input
            else:
                print("\n✨ Analysis complete! Start a new conversation or type 'quit'")
                conversation = ""

if __name__ == "__main__":
    print("Choose mode:")
    print("1. Example demo")
    print("2. Interactive mode")
    
    choice = input("Enter choice (1 or 2): ")
    
    if choice == "1":
        main()
    elif choice == "2":
        interactive_mode()
    else:
        print("Invalid choice. Running example demo...")
        main()