# RAGAS Evaluation for Timeline System

This folder contains all the files needed to evaluate your timeline extraction system using RAGAS metrics.

## 📁 Files in this folder:

- **`ground_truth_dataset.json`** - Ground truth questions, answers, and context from the house break-in story
- **`ragas_evaluation.py`** - Main evaluation script for RAGAS metrics
- **`ragas_requirements.txt`** - Python dependencies for RAGAS evaluation
- **`RAGAS_EVALUATION_GUIDE.md`** - Comprehensive guide for using RAGAS evaluation

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r ragas_requirements.txt
   ```

2. **Run the evaluation:**
   ```bash
   python ragas_evaluation.py
   ```

3. **View results:**
   - Check `evaluation_results.json` for detailed metrics
   - Review the console output for summary

## 📊 What you'll get:

- **Faithfulness** - Does the answer match the context?
- **Answer Relevancy** - Is the answer relevant to the question?
- **Context Relevancy** - Is the right context selected?
- **Context Recall** - Does the context have complete information?
- **Answer Correctness** - Is the answer factually correct?
- **Answer Similarity** - How similar is the answer to ground truth?

## 🔧 Integration with Timeline System

To evaluate your actual timeline system:

1. **Update the evaluation script** to use your system's outputs
2. **Run evaluation** on both map-reduce and refine methods
3. **Compare results** to see which method performs better

## 📈 Ground Truth Dataset

The ground truth includes 20 questions across 3 categories:
- **Timeline Extraction** (11 questions) - Specific times and dates
- **Information Extraction** (8 questions) - Events and details  
- **Sequence Extraction** (2 questions) - Chronological sequences

## 📝 Next Steps

1. Test with sample data first
2. Integrate your timeline system outputs
3. Compare different methods
4. Create ground truth for other documents
5. Iterate and improve based on metrics

For detailed instructions, see `RAGAS_EVALUATION_GUIDE.md`. 