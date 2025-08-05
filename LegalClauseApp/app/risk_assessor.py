from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage
import json

class RiskAssessor:
    def __init__(self, model_name="mistral"):
        self.llm = ChatOllama(model=model_name)

    def assess_risk(self, clause: str, user_prompt: str) -> dict:
        """
        Assesses the legal risk of a given clause and provides reasoning.
        """
        prompt = f"""
        You are an expert legal risk assessor. Your task is to analyze the following legal clause
        that was generated based on the user's intent.

        User's original intent: "{user_prompt}"

        Generated Legal Clause:
        "{clause}"

        Assess the risk level of this clause as 'Low', 'Medium', or 'High' based on the following criteria:
        - Clarity and Ambiguity: Is the language clear, precise, and unambiguous?
        - Balance and Fairness: Is the clause reasonably balanced between parties, or does it heavily favor one side?
        - Completeness: Does it cover all necessary aspects for the given intent? Are there any critical omissions?
        - Potential Liability/Safeguards: Does it introduce undue liability or is it missing standard legal safeguards (e.g., indemnity, jurisdiction, IP ownership, warranties, limitations of liability)?

        Provide your assessment in the following JSON format:
        {{
            "risk_level": "Low" | "Medium" | "High",
            "reasoning": "Concise explanation of why this risk level was assigned, referencing the criteria above."
        }}
        """
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            # Attempt to parse the JSON response
            parsed_response = json.loads(response.content)
            return parsed_response
        except Exception as e:
            print(f"Error during risk assessment or JSON parsing: {e}")
            print(f"LLM Raw Response: {response.content}")
            return {"risk_level": "Unknown", "reasoning": f"Failed to assess risk: {e}. Raw LLM response: {response.content}"}
