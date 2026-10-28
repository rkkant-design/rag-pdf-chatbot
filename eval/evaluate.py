"""Lightweight evaluation harness.

Runs a set of questions and checks the two behaviours that matter for a grounded
RAG bot: it answers in-corpus questions, and it refuses out-of-corpus ones.

Run:  python -m eval.evaluate

For deeper, metric-based evaluation (faithfulness, answer relevancy, context
precision/recall) add RAGAS. See the note at the bottom and the README.
"""
import json
import os

from app.prompts import REFUSAL
from app.rag import answer

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    with open(os.path.join(HERE, "questions.json"), encoding="utf-8") as fh:
        questions = json.load(fh)

    passed = 0
    for item in questions:
        result = answer(item["question"])
        refused = REFUSAL.lower() in result["answer"].lower()
        ok = (item["expect"] == "refuse" and refused) or (
            item["expect"] == "in_docs" and not refused
        )
        passed += ok
        print(f"[{'PASS' if ok else 'FAIL'}] ({item['expect']}) {item['question']}")
        print(f"    -> {result['answer']}")
        if result["sources"]:
            print(
                "    sources: "
                + ", ".join(f"{s['document']} p.{s['page']}" for s in result["sources"])
            )
        print()

    print(f"{passed}/{len(questions)} behaved as expected.")


# --- Optional: RAGAS metrics -------------------------------------------------
# pip install ragas datasets
# RAGAS scores faithfulness (does the answer stay within the retrieved context?),
# answer_relevancy, and context_precision/recall. Build a dataset of
# {question, answer, contexts, ground_truth} by calling app.rag.retrieve + answer,
# then:
#   from ragas import evaluate
#   from ragas.metrics import faithfulness, answer_relevancy, context_precision
#   evaluate(dataset, metrics=[faithfulness, answer_relevancy, context_precision])

if __name__ == "__main__":
    main()
