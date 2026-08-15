from typing import Dict, List

class MetadataFilter:
    """
    Filters vector search results based on document metadata (e.g., access_level).
    """

    def apply_filters(self, results: List[Dict], user_permissions: List[str]) -> List[Dict]:
        """
        Removes results that the user is not permitted to see.
        """
        filtered = []
        for doc in results:
            doc_level = doc.get("metadata", {}).get("access_level", "public")
            if doc_level == "public" or f"read:{doc_level}" in user_permissions:
                filtered.append(doc)
        return filtered
