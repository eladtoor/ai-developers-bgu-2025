# RAGAS Evaluation Guide for Timeline System

This guide explains how to use RAGAS to evaluate your timeline extraction system using the ground truth dataset.

## 📋 What is Ground Truth?

Ground truth is a dataset of questions and their correct answers based on your source document. For timeline extraction, we need:

1. **Questions** - What users might ask about the timeline
2. **Correct Answers** - The accurate answers from the story
3. **Context** - The relevant parts of the story that answer each question

## 🎯 Ground Truth Categories

Our ground truth dataset includes three types of questions:

### 1. Timeline Extraction (11 questions)
- Focus on specific times and dates
- Example: "What time did Sarah first hear suspicious sounds?"
- Answer: "8:15 PM"

### 2. Information Extraction (8 questions)
- Focus on events, actions, and details
- Example: "What items were stolen from Sarah's house?"
- Answer: "Sarah's grandmother's jewelry box, some cash from her bedroom drawer, and her laptop computer"

### 3. Sequence Extraction (2 questions)
- Focus on chronological sequences of events
- Example: "What was the sequence of events from 8:15 PM to 9:22 PM?"
- Answer: Detailed timeline of events

## 🚀 How to Use RAGAS Evaluation

### Step 1: Install Dependencies
```bash
pip install -r ragas_requirements.txt
```

### Step 2: Run the Evaluation
```bash
python ragas_evaluation.py
```

### Step 3: Integrate with Your Timeline System

Replace the sample answers in `ragas_evaluation.py` with actual outputs from your timeline system:

```python
# In ragas_evaluation.py, replace this function:
def create_sample_answers_for_testing():
    # Replace with actual outputs from your timeline system
    return your_timeline_system_answers
```

## 📊 RAGAS Metrics Explained

### 1. **Faithfulness**
- Measures if the answer is faithful to the provided context
- High score = answer doesn't contradict the context

### 2. **Answer Relevancy**
- Measures if the answer is relevant to the question
- High score = answer directly addresses the question

### 3. **Context Relevancy**
- Measures if the provided context is relevant to the question
- High score = context contains information needed to answer

### 4. **Context Recall**
- Measures if the context contains all necessary information
- High score = context has complete information needed

### 5. **Answer Correctness**
- Measures if the answer matches the ground truth
- High score = answer is factually correct

### 6. **Answer Similarity**
- Measures semantic similarity between generated and ground truth answers
- High score = answers are semantically similar

## 🔧 Customizing the Evaluation

### Adding New Questions
1. Edit `ground_truth_dataset.json`
2. Add new question-answer pairs
3. Update the metadata counts

### Testing Different Methods
Compare your map-reduce vs refine methods:

```python
# Test map-reduce method
map_reduce_answers = your_map_reduce_system(questions)
map_reduce_results = evaluator.evaluate_system(map_reduce_answers, "map_reduce_results.json")

# Test refine method  
refine_answers = your_refine_system(questions)
refine_results = evaluator.evaluate_system(refine_answers, "refine_results.json")
```

### Category-Specific Analysis
```python
# Filter by category for detailed analysis
timeline_questions = [q for q in ground_truth if q["category"] == "timeline_extraction"]
information_questions = [q for q in ground_truth if q["category"] == "information_extraction"]
```

## 📈 Interpreting Results

### Good Scores (>0.7)
- **Faithfulness**: System doesn't hallucinate
- **Answer Relevancy**: Answers are on-topic
- **Context Relevancy**: Right context is selected
- **Context Recall**: Complete information is provided
- **Answer Correctness**: Factually accurate
- **Answer Similarity**: Semantically similar to ground truth

### Areas for Improvement
- **Low Faithfulness**: System hallucinates information
- **Low Answer Relevancy**: Answers are off-topic
- **Low Context Relevancy**: Wrong context is selected
- **Low Context Recall**: Missing important information
- **Low Answer Correctness**: Factual errors
- **Low Answer Similarity**: Different meaning than expected

## 🎯 Best Practices

### 1. **Comprehensive Ground Truth**
- Include various question types
- Cover different time periods
- Include edge cases and complex scenarios

### 2. **Consistent Evaluation**
- Use same ground truth for all methods
- Run multiple evaluations for reliability
- Document any changes to the dataset

### 3. **Iterative Improvement**
- Identify weak areas from metrics
- Improve prompts or methods
- Re-evaluate after changes

### 4. **Documentation**
- Keep track of evaluation results
- Note any changes to the system
- Compare results over time

## 🔍 Example Output

```
==================================================
RAGAS EVALUATION SUMMARY
==================================================

Dataset: house_break_in_story.txt
Total Questions: 20
Categories: {'timeline_extraction': 11, 'information_extraction': 8, 'sequence_extraction': 2}

Metrics:
------------------------------
Faithfulness: 0.8500
Answer Relevancy: 0.9200
Context Relevancy: 0.8800
Context Recall: 0.7600
Answer Correctness: 0.8100
Answer Similarity: 0.8900
==================================================
```

## 📝 Next Steps

1. **Run the evaluation** with your actual timeline system
2. **Analyze the results** to identify areas for improvement
3. **Iterate on your system** based on the metrics
4. **Create more ground truth** for other documents
5. **Compare different approaches** (map-reduce vs refine)

## 🆘 Troubleshooting

### Common Issues:
- **Import errors**: Install all requirements
- **Dataset size mismatch**: Ensure answers match questions
- **Low scores**: Check ground truth quality and system outputs
- **Memory issues**: Use smaller batches for large datasets

### Getting Help:
- Check RAGAS documentation: https://docs.ragas.io/
- Review the ground truth dataset structure
- Test with sample data first 