import re

class RiskAssessor:
    def assess_risk(self, clause: str) -> str:
        """
        Assesses the risk of a clause based on keywords.
        This is a simplified model and should be expanded for real-world use.
        """
        high_risk_keywords = ['termination for convenience', 'unlimited liability', 'indemnify', 'liquidated damages']
        medium_risk_keywords = ['confidentiality', 'non-disclosure', 'warranty', 'limitation of liability']
        
        clause_lower = clause.lower()
        
        if any(re.search(r'\b' + keyword + r'\b', clause_lower) for keyword in high_risk_keywords):
            return "High"
        elif any(re.search(r'\b' + keyword + r'\b', clause_lower) for keyword in medium_risk_keywords):
            return "Medium"
        else:
            return "Low"

    def classify_clause(self, clause: str) -> str:
        """
        Classifies a clause based on keywords.
        This is a simplified model and should be expanded for real-world use.
        """
        classification_keywords = {
            "Termination": ['terminate', 'termination'],
            "Confidentiality": ['confidential', 'non-disclosure'],
            "Liability": ['liability', 'indemnify'],
            "Payment": ['payment', 'fee', 'invoice']
        }
        
        clause_lower = clause.lower()
        
        for classification, keywords in classification_keywords.items():
            if any(re.search(r'\b' + keyword + r'\b', clause_lower) for keyword in keywords):
                return classification
        
        return "General"

    def get_risk_level_value(self, risk: str) -> int:
        """
        Returns a numerical value for a given risk level for comparison.
        """
        risk_map = {
            "Low": 1,
            "Medium": 2,
            "High": 3,
            "Very High": 4 # Added Very High for completeness, though not explicitly used in assess_risk yet
        }
        return risk_map.get(risk, 99) # Default to a high value for unknown risks
