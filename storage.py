import os, json, hashlib, time
from typing import List, Dict, Any

def _mask(value: str) -> str:
    """Hash/mask PII using sha256 (simulated anonymization)."""
    if not value:
        return ""
    h = hashlib.sha256(value.encode("utf-8")).hexdigest()[:10]
    return f"anon_{h}"

class CandidateStore:
    def __init__(self, path: str = "storage/candidates.json"):
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if not os.path.exists(self.path):
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump({"sessions": []}, f, indent=2)

    def save(self, candidate: Dict[str, Any], chat: List[Dict[str, str]]) -> str:
        record = {
            "id": f"sess_{int(time.time())}",
            "created_at": int(time.time()),
            "candidate": {
                "full_name": candidate.get("full_name"),
                # mask PII fields
                "email": _mask(candidate.get("email", "")),
                "phone": _mask(candidate.get("phone", "")),
                "years_experience": candidate.get("years_experience"),
                "desired_position": candidate.get("desired_position"),
                "location": candidate.get("location"),
                "tech_stack": candidate.get("tech_stack"),
            },
            "chat": chat[-50:],  # limit stored history
        }
        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["sessions"].append(record)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return record["id"]
