# Lecture 9: Document Summarization with LangChain

This project demonstrates two different approaches to document summarization using LangChain, applied to the LLM-powered autonomous agents document by Lilian Weng.

## 📄 Document Source
- **URL**: https://lilianweng.github.io/posts/2023-06-23-agent/
- **Topic**: LLM-Powered Autonomous Agents
- **Author**: Lilian Weng

## 🗂️ Files

### Core Implementation
- `stuff_summarization.py` - Implements the "stuff" approach
- `map_reduce_summarization.py` - Implements the "map-reduce" approach
- `compare_summarizations.py` - Compares both approaches

### Output Files
- `stuff_summary.txt` - Summary using stuff approach
- `map_reduce_summary.txt` - Summary using map-reduce approach
- `comparison_report.txt` - Detailed comparison report

## 🚀 How to Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up Environment Variables
Create a `.env` file in the parent directory with:
```
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Run Individual Approaches

**Stuff Summarization:**
```bash
python stuff_summarization.py
```

**Map-Reduce Summarization:**
```bash
python map_reduce_summarization.py
```

### 4. Run Comparison
```bash
python compare_summarizations.py
```

## 📊 Approaches Explained

### 1. Stuff Summarization
- **Method**: Puts entire document in one prompt
- **Pros**: Simple, fast, single API call
- **Cons**: Limited by token context, may lose detail
- **Best for**: Short to medium documents

### 2. Map-Reduce Summarization
- **Method**: 
  - **Map**: Split document into chunks, summarize each
  - **Reduce**: Combine all summaries into final summary
- **Pros**: Handles long documents, scalable, better detail preservation
- **Cons**: More complex, multiple API calls, slower for short docs
- **Best for**: Long documents

## 🔍 Key Features

### Web Scraping
- Automatically fetches content from the target URL
- Cleans and processes HTML content
- Handles different page structures

### Text Processing
- Intelligent text splitting for map-reduce
- Metadata preservation
- Content cleaning and formatting

### Quality Analysis
- Compares summary lengths
- Analyzes content coverage
- Measures key topic mentions

## 📈 Expected Results

The system will:
1. Fetch the LLM-powered autonomous agents document
2. Generate summaries using both approaches
3. Compare performance and quality
4. Save results to text files
5. Provide detailed analysis

## 🛠️ Technical Details

### Dependencies
- **LangChain**: Core framework for LLM interactions
- **OpenAI**: GPT-3.5-turbo for text generation
- **BeautifulSoup**: Web scraping
- **Requests**: HTTP requests
- **Text Splitters**: Document chunking

### Architecture
```
Document Fetching → Text Processing → Summarization → Analysis
```

### Token Management
- Stuff approach: Limited by model context window
- Map-reduce: Handles documents of any length
- Chunk size: 4000 characters with 200 overlap

## 📝 Output Files

1. **stuff_summary.txt**: Complete summary using stuff approach
2. **map_reduce_summary.txt**: Complete summary using map-reduce approach
3. **comparison_report.txt**: Detailed comparison with metrics

## 🎯 Use Cases

- **Research**: Summarize academic papers
- **Content Analysis**: Process long articles
- **Documentation**: Create executive summaries
- **Learning**: Understand complex topics quickly

## 🔧 Customization

To use with different documents:
1. Change the URL in the fetch methods
2. Adjust chunk sizes for map-reduce
3. Modify prompts for different content types
4. Update key topics for analysis

## 📚 References

- [LangChain Summarization Tutorial](https://python.langchain.com/docs/tutorials/summarization/)
- [LLM-Powered Autonomous Agents](https://lilianweng.github.io/posts/2023-06-23-agent/) 