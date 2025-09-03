import os
import re
import json
from typing import List, Dict, Any, Optional
from prompts import INFO_GATHERING_PROMPT, QUESTION_GEN_PROMPT, FALLBACK_PROMPT

END_KEYWORDS = {"bye", "exit", "quit", "goodbye", "stop", "end"}

def detect_end_keywords(text: str) -> bool:
    return any(k in text.lower() for k in END_KEYWORDS)

def split_tech_stack(tech_stack: Optional[str]) -> List[str]:
    if not tech_stack:
        return []
    parts = [p.strip() for p in re.split(r"[,\n/;]+", tech_stack) if p.strip()]
    # normalize common variants
    norm = []
    for p in parts:
        lp = p.lower()
        synonyms = {
            "node": "node.js",
            "nodejs": "node.js",
            "postgres": "postgresql",
            "ts": "typescript",
            "py": "python",
        }
        norm.append(synonyms.get(lp, p))
    return norm

class OpenAIClient:
    def __init__(self, model: str, api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        from openai import OpenAI  # lazy import
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def available(self) -> bool:
        return self.client is not None

    def chat(self, system: str, user: str) -> str:
        if not self.client:
            raise RuntimeError("OpenAI client not configured.")
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.2,
        )
        return resp.choices[0].message.content.strip()

class MockLLM:
    """Offline fallback with rule-based question generation."""
    RULES = {
        "python": [
            "Explain list vs tuple and when you'd use each.",
            "What are decorators and give a practical use case.",
            "How does virtualenv/venv help manage dependencies?",
            "Describe list/dict comprehensions and a scenario to use them.",
        ],
        "django": [
            "How does Django ORM translate to SQL? Provide an example query.",
            "Explain migrations and how to create/apply them.",
            "What are middlewares? Give a real-world use case.",
        ],
        "react": [
            "What are hooks and how do useEffect and useMemo differ?",
            "Explain reconciliation and keys in lists.",
            "How would you manage state across components (Context vs Redux)?",
        ],
        "postgresql": [
            "What are indexes and when can they hurt performance?",
            "Explain transactions and isolation levels.",
            "How do you design a schema for many-to-many relationships?",
        ],
        "node.js": [
            "Explain the event loop and its phases.",
            "How do streams differ from buffers? Provide a use case.",
            "How would you structure a REST API with Express for scalability?",
        ],
        "aws": [
            "When would you choose S3 + CloudFront vs EFS?",
            "Explain IAM roles vs policies with an example.",
            "How do you design a fault-tolerant architecture on EC2 + ALB?",
        ],
    }

    def chat(self, system: str, user: str) -> str:
        # A very basic mock that echoes purpose and routes.
        if "generate 3-5 technical interview questions" in user.lower():
            # naive extraction
            m = re.search(r"tech stack:\s*(.*)", user, re.IGNORECASE | re.DOTALL)
            stack = split_tech_stack(m.group(1) if m else "")
            qs = []
            for s in stack:
                key = s.lower()
                if key in self.RULES:
                    qs.extend(self.RULES[key][:2])
            if not qs:
                qs = ["Explain a challenging project you built with your primary stack.",
                      "How do you ensure code reliability, testing, and deployment?"]
            return "\n".join(qs[:5])
        # Fallback for info gathering and general replies
        if "ask the candidate step-by-step" in system.lower():
            return "Thanks! I've recorded your details. I will now prepare tailored technical questions."
        return "Could you please clarify your last message? Let's focus on your profile and tech stack."

class TalentScoutBot:
    def __init__(self, provider: str = "openai", model: str = "gpt-4o-mini", api_key: Optional[str] = None):
        self.provider = provider
        self.model = model
        self.api_key = api_key
        self.openai = None
        if self.provider == "openai":
            try:
                self.openai = OpenAIClient(model=self.model, api_key=self.api_key)
                if not self.openai.available():
                    self.provider = "mock"
            except Exception:
                self.provider = "mock"
        self.mock = MockLLM()

    def _chat(self, system: str, user: str) -> str:
        if self.provider == "openai" and self.openai and self.openai.available():
            try:
                return self.openai.chat(system, user)
            except Exception as e:
                return f"(Note: OpenAI call failed, switching to safe reply.) {self.mock.chat(system, user)}"
        return self.mock.chat(system, user)

    def reply(self, user_msg: str, candidate: Dict[str, Any]) -> str:
        if detect_end_keywords(user_msg):
            return "Thanks for your time! We'll review your responses and get back to you with next steps. 👋"

        # minimal context-aware guidance
        missing = []
        required = ["full_name", "email", "phone", "years_experience", "desired_position", "location", "tech_stack"]
        for k in required:
            if not candidate.get(k):
                missing.append(k.replace("_", " ").title())

        if missing:
            return f"Before we proceed, please provide: **{', '.join(missing)}** in the Candidate Details above."

        # Otherwise, do an info-gathering/clarification turn via LLM
        system = INFO_GATHERING_PROMPT.strip()
        user = f"Candidate profile:\n{json.dumps(candidate, indent=2)}\nUser said: {user_msg}\nRespond politely and keep the flow."
        return self._chat(system, user)

    def generate_tech_questions(self, candidate: Dict[str, Any]) -> List[str]:
        stack = candidate.get("tech_stack")
        if not stack:
            return []
        system = "You are an expert technical interviewer."
        user = QUESTION_GEN_PROMPT.format(tech_stack=stack)
        raw = self._chat(system, user)
        # Split into lines, strip bullets/numbers
        lines = [re.sub(r"^[\-\*\d\.\)\s]+", "", ln).strip() for ln in raw.splitlines() if ln.strip()]
        # Return 3-5
        out = [ln for ln in lines if len(ln) > 5][:5]
        if len(out) < 3:
            # augment with mock as needed
            extra = self.mock.chat(system, user).splitlines()
            extra = [e.strip() for e in extra if e.strip()]
            for e in extra:
                if len(out) >= 5: break
                if e not in out:
                    out.append(e)
        return out
