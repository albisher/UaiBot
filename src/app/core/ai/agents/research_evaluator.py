from uaibot.core.ai.agent import Agent

class ResearchEvaluatorAgent(Agent):
    """
    Agent that evaluates research quality and checks completeness.
    Reviews outputs and provides feedback or scores.
    """
    def evaluate(self, research_report: dict) -> dict:
        """Evaluate the research report for quality and completeness."""
        report = research_report.get("report", "")
        raw = research_report.get("raw", {})
        score = 0
        feedback = []
        # Check for key sections
        for section in ["system", "web_search", "files"]:
            if section in raw and raw[section]:
                score += 1
            else:
                feedback.append(f"Missing or empty section: {section}")
        # Simple quality check
        if len(report) > 100:
            score += 1
        else:
            feedback.append("Report is too short.")
        return {"score": score, "feedback": feedback, "summary": report[:200]} 