import json
import numpy as np

def calculate_averages(file_path):
    """Calculate average scores from evaluation results"""
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    metrics = data['metrics']
    
    # Calculate averages for each metric
    averages = {}
    for metric in ['faithfulness', 'answer_relevancy', 'context_recall', 'answer_correctness', 'semantic_similarity', 'context_precision', 'context_entity_recall']:
        values = [item[metric] for item in metrics]
        averages[metric] = np.mean(values)
    
    return averages

def main():
    print("="*60)
    print("RAGAS EVALUATION SUMMARY COMPARISON")
    print("="*60)
    
    # Calculate averages for both methods
    map_reduce_avg = calculate_averages('map_reduce_evaluation_results.json')
    refine_avg = calculate_averages('refine_evaluation_results.json')
    
    print("\n📊 MAP-REDUCE TIMELINE RESULTS:")
    print("-" * 40)
    for metric, score in map_reduce_avg.items():
        print(f"{metric.replace('_', ' ').title()}: {score:.4f}")
    
    print("\n📊 REFINE TIMELINE RESULTS:")
    print("-" * 40)
    for metric, score in refine_avg.items():
        print(f"{metric.replace('_', ' ').title()}: {score:.4f}")
    
    print("\n🏆 COMPARISON:")
    print("-" * 40)
    
    # Compare each metric
    for metric in map_reduce_avg.keys():
        map_score = map_reduce_avg[metric]
        refine_score = refine_avg[metric]
        
        if map_score > refine_score:
            winner = "MAP-REDUCE"
            diff = map_score - refine_score
        elif refine_score > map_score:
            winner = "REFINE"
            diff = refine_score - map_score
        else:
            winner = "TIE"
            diff = 0
        
        print(f"{metric.replace('_', ' ').title()}:")
        print(f"  Map-Reduce: {map_score:.4f}")
        print(f"  Refine:     {refine_score:.4f}")
        print(f"  Winner:     {winner} (+{diff:.4f})")
        print()
    
    # Overall winner
    map_total = sum(map_reduce_avg.values())
    refine_total = sum(refine_avg.values())
    
    print("🎯 OVERALL PERFORMANCE:")
    print(f"Map-Reduce Total Score: {map_total:.4f}")
    print(f"Refine Total Score:     {refine_total:.4f}")
    
    if map_total > refine_total:
        print("🏆 WINNER: MAP-REDUCE METHOD")
    elif refine_total > map_total:
        print("🏆 WINNER: REFINE METHOD")
    else:
        print("🏆 RESULT: TIE")

if __name__ == "__main__":
    main() 