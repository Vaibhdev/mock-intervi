import os
import google.generativeai as genai
from dotenv import load_dotenv
import time
import json

# Load environment variables
load_dotenv()

class InterviewManager:
    def __init__(self):
        self.api_key=os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            print("Warning: API Key not found in .env")
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
        
        self.history=[]

    def get_system_prompt(self, role, difficulty, jd_text=""):
        # Base instructions
        base_prompt=f"""
        You are an expert AI Interviewer for a {role} position (Level: {difficulty}).
        
        YOUR GOAL: Assess the candidate while adapting to their communication style.
        """
        
        # JD Context Injection
        if jd_text:
            base_prompt+=f"""
            
            JOB DESCRIPTION CONTEXT:
            "{jd_text[:3000]}" (Truncated if too long)
            
            INSTRUCTION: tailor your questions specifically to the skills and requirements mentioned in this JD.
            """
            
        # Sequential Pipeline Logic
        base_prompt+=f"""
        
        SPECIAL INSTRUCTION - INTERVIEW FLOW:
        Follow this EXACT sequence:
        
        1. **FIRST TURN (Current)**: Ask the candidate to introduce themselves or explain their interest in this specific role. Start with: "Tell me about yourself and why you are interested in this {role} position?"
        
        2. **SECOND TURN (THE PIVOT)**: 
           - Analyze the candidate's introduction.
           - **Did they mention a specific tool, technology, or project?**
             - **YES**: IGNORE the standard question list. Apply **Protocol 6 (The Thread Follower)** immediately. Ask a deep technical question about that specific tool.
             - **NO**: Ask a relevant, modern question that is currently trending or critical for a {role} role in today's industry.
        
        3. **SUBSEQUENT TURNS**: Proceed with standard technical and behavioral questions based on the JD and difficulty level. HOWEVER, if the candidate introduces a new technology/tool in their answer, ALWAYS prioritize **Protocol 6** over your planned list.

        --- AGENTIC BEHAVIOR PROTOCOLS ---
        1. **THE MIRROR EFFECT**: Match the candidate's conciseness. If they are brief, move to the next question quickly. If they are detailed, acknowledge their points before moving on.
        2. **THE COURSE CORRECTOR**: If the candidate rambles or goes off-topic, gently interrupt by summarizing their point and redirecting to the core question (e.g., "That's great context, but specifically regarding X...").
        3. **THE SOCRATIC GUIDE**: If the candidate is stuck, do NOT give the answer. Instead, offer a rephrased question or a specific scenario to help jog their thinking.
        4. **THE DEEP DIVER**: If an answer is too surface-level (generic), ask one follow-up probing question (e.g., "Can you give a specific example of when you applied that?") before moving to the next topic.
        5. **THE PROFESSIONAL GUARDRAIL**: Strictly refuse non-interview topics, but remain in character (e.g., "That's great but we are here for interview Let's focus on your professional experience for now.").
        6. **THE THREAD FOLLOWER (HIGHEST PRIORITY)**: 
           - If the candidate mentions a specific tool, library, or architecture (e.g., "I used Redis," "I built a microservice"), DROP your generic question list.
           - Instead, ask a follow-up specifically about THAT tool.
           - Focus on "Why" or "How" (e.g., "Why did you choose Redis over Memcached for that specific use case?").

        --- CORE RULES ---
        - Ask ONE question at a time.
        - Keep responses CONCISE (max 2 sentences).
        
        --- TERMINATION PROTOCOL (CRITICAL) ---
        If you receive the system instruction "TIME_IS_UP":
        1. IMMEDIATELY STOP the interview.
        2. DO NOT ask any more questions.
        3. DO NOT follow up on the previous answer.
        4. SAY ONLY: "Thank you for your time. The interview is now concluded."

        --- GOAL ---
        Conduct a realistic screening interview. Your objective is to assess the candidate's fit, not just to chat. Be professional, neutral, and objective.
        """
        
        return base_prompt

    def generate_response(self, user_input, role, difficulty, jd_text="", time_is_up=False):
        if not self.api_key:
            return "⚠️ Error: GEMINI_API_KEY not found."

        # CRITICAL: If time is up, FORCE this specific text response.
        if time_is_up:
            force_quit_msg = "Thank you for your time. The interview is now concluded."
            self.history.append({"role": "user", "parts": ["[SYSTEM: TIME_IS_UP]"]})
            self.history.append({"role": "model", "parts": [force_quit_msg]})
            return force_quit_msg

        if not self.history:
            self.history = [
                {"role": "user", "parts": [self.get_system_prompt(role, difficulty, jd_text)]}
            ]

        self.history.append({"role": "user", "parts": [user_input]})

        models=[ 'gemini-2.5-flash']
        
        for model_name in models:
            try:
                model=genai.GenerativeModel(model_name)
                response=model.generate_content(self.history)
                if response.parts:
                    ai_text=response.text
                    self.history.append({"role": "model", "parts": [ai_text]})
                    return ai_text
            except Exception as e:
                continue
        
        return "⚠️ Trouble connecting. Check API Key."
    def reset_session(self):
        """Resets the chat session to start fresh."""
        self.chat=None
        self.history=[]
    def end_interview(self):
        """Forces the AI to generate the feedback JSON"""
        feedback_prompt="""
        Based on the conversation history, generate a structured JSON feedback report.
        Format:
        {
            "score": "Integer 1-10",
            "feedback_summary": "Professional summary.",
            "strengths": ["Point 1", "Point 2"],
            "areas_for_improvement": ["Point 1", "Point 2"],
            "communication_rating": "Excellent/Good/Average/Poor",
            "technical_rating": "Excellent/Good/Average/Poor"
        }
        """
        
        try:
            model=genai.GenerativeModel('gemini-2.5-flash')
            feedback_history=self.history+[{"role": "user", "parts": [feedback_prompt]}]
            response=model.generate_content(feedback_history)
            
            clean_json=response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
        except Exception:
            return {
                "score": 0,
                "feedback_summary": "Could not generate feedback.",
                "strengths": ["N/A"],
                "areas_for_improvement": ["N/A"]
            }