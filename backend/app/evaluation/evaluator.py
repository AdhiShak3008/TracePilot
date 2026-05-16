from app.evaluation.groundedness import check_groundedness
from app.evaluation.hallucination import detect_hallucination, detect_abstention
from app.evaluation.faithfulness import compute_faithfulness


class Evaluator:

    def evaluate(self, query, response, retrieved_chunks):

        abstained = detect_abstention(response)

        if abstained:
            return {
                "grounded": True,
                "hallucination_score": 0.0,
                "faithfulness_score": 1.0,
                "abstained": True
            }

        grounded = check_groundedness(response, retrieved_chunks)

        hallucination_score = detect_hallucination(response, retrieved_chunks)

        faithfulness_score = compute_faithfulness(response, retrieved_chunks)

        return {
            "grounded": grounded,
            "hallucination_score": hallucination_score,
            "faithfulness_score": faithfulness_score,
            "abstained": False
        }
