from typing import List, Dict

# Import Security Modules
from backend.api_security.rbac_policy import RBACPolicy
from backend.data_security.pii_masking import RegexPIIMaskingStrategy

class SecureRetriever:
    """
    Retrieves documents with security checks:
    1. Enforces RBAC on document access.
    2. Masks PII in returned chunks.
    """

    def __init__(self):
        # Demo RBAC Role definitions
        self.rbac = RBACPolicy({
            "admin": ["*"],
            "analyst": ["read_public", "read_internal"],
            "intern": ["read_public"]
        })
        self.pii_masker = RegexPIIMaskingStrategy()

    def retrieve_documents(self, query: str, user_role: str) -> List[str]:
        # Mock Vector Search Results
        raw_docs = [
            {"content": "Public Report: 2024 Trends", "classification": "read_public"},
            {"content": "Internal Memo: Contact ceo@company.com", "classification": "read_internal"},
            {"content": "Secret Project X", "classification": "read_secret"}
        ]

        safe_docs = []
        for doc in raw_docs:
            # 1. RBAC Check
            required_permission = doc["classification"]
            if not self.rbac.has_permission(user_role, required_permission):
                print(f"RBAC Blocked: User '{user_role}' cannot access '{required_permission}'")
                continue

            # 2. PII Masking (On Read)
            # In some designs you mask on Write, but Read-masking is also valid for dynamism
            scan_res = self.pii_masker.scan(doc["content"])
            masked_content = self.pii_masker.mask(doc["content"], scan_res)
            safe_docs.append(masked_content)

        return safe_docs

# Demo Usage
if __name__ == "__main__":
    retriever = SecureRetriever()
    print("Analyst sees:", retriever.retrieve_documents("query", "analyst"))
    print("Intern sees:", retriever.retrieve_documents("query", "intern"))
