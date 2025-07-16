from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    answer_correctness,
    answer_similarity,
    context_precision,
    context_entity_recall
)

results = evaluate(
    dataset,
    metrics=[
        faithfulness,
        answer_relevancy,
        context_recall,
        answer_correctness,
        answer_similarity,
        context_precision,
        context_entity_recall
    ]
) 