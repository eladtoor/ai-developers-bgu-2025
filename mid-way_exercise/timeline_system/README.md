# Timeline Summarization System

This folder contains a complete timeline summarization system that can extract chronological events from text documents and organize them into bullet-point timelines.

## 📁 File Structure

### **Core Components:**
- **`timeline_prompts.py`** - Timeline-specific prompts for AI
- **`timeline_map_reduce.py`** - Map-Reduce timeline processing
- **`timeline_refine.py`** - Refine timeline processing
- **`file_utils.py`** - File handling utilities
- **`timeline_tools_simple.py`** - LangChain tools wrapper
- **`simple_timeline_agent.py`** - Interactive agent

### **Test Documents:**
- **`house_break_in_story.txt`** - Story with specific times
- **`car_insurance_document.txt`** - Insurance process timeline

## 🚀 How to Use

### **1. Run the Agent:**
```bash
cd mid-way_exercise/timeline_system
python simple_timeline_agent.py
```

### **2. Example Usage:**
```
You: Process house_break_in_story.txt
You: Create timelines from car_insurance_document.txt
```

### **3. Output Files:**
- `map_reduce_timeline_[filename].txt`
- `refine_timeline_[filename].txt`

## 🔧 How It Works

### **Map-Reduce Method:**
1. Split document into chunks
2. Extract timeline from each chunk
3. Combine all timelines into one

### **Refine Method:**
1. Start with first chunk as timeline
2. Keep improving timeline with each new chunk
3. End with final refined timeline

### **Timeline Format:**
```
• [Time] - [Event/Action]
• [Time] - [Event/Action]
• [Time] - [Event/Action]
```

## 📊 File Purposes

| File | Purpose | Lines |
|------|---------|-------|
| `timeline_prompts.py` | AI prompts for timeline extraction | 45 |
| `timeline_map_reduce.py` | Map-Reduce timeline logic | 50 |
| `timeline_refine.py` | Refine timeline logic | 45 |
| `file_utils.py` | File handling utilities | 34 |
| `timeline_tools_simple.py` | LangChain tools wrapper | 75 |
| `simple_timeline_agent.py` | Interactive agent | 93 |

## 🎯 Key Features

- ✅ **Organized Structure** - Each file has one clear purpose
- ✅ **Easy to Understand** - Small, focused functions
- ✅ **Auto-Save** - Results automatically saved to files
- ✅ **Bullet-Point Format** - Clear chronological organization
- ✅ **Two Methods** - Map-Reduce and Refine approaches

## 🔄 Process Flow

```
Text Document → Agent → Timeline Tools → Timeline Processing → Output Files
```

The system is designed to be simple, organized, and easy to understand! 🎉 