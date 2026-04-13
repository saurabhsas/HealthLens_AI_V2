🏥 HealthLens AI V2

AI-Powered Healthcare Analytics Dashboard using Natural Language Queries

HealthLens AI V2 is an intelligent healthcare analytics platform that allows users to explore structured healthcare data using natural language queries, powered by LLMs, Pandas, and interactive visualizations.

🚀 Features
🧠 AI-Powered Querying
Ask questions in plain English
Converts queries → Pandas code using LLM
📊 Smart Visualizations
Auto-selects charts:
Line (trends)
Bar (comparisons)
Pie (distribution)
Histogram
📈 Key Metrics
Total Members
Total Cost
Average Cost
ED Visits
IP Visits
🎯 Interactive Dashboard
Built with Gradio
Filter-based exploration:
Gender
Line of Business
County
⚡ UX Enhancements
Example prompts (clickable)
Auto-suggestions
Press Enter to run
Clear button
📄 PDF Export
Export:
KPIs
Charts
Data Table
Insights
Saved in temp directory
🏗️ Architecture
User → Query → LLM → Pandas → Visualization → Insights → PDF → UI
Flow:
User inputs query
Filters applied
LLM generates Pandas code
Code executed
Data visualized (Plotly)
Insights generated
Report exported
📁 Project Structure
HealthLens_AI_V2/
│── app.py
│
├── core/
│   ├── data_processing.py
│   ├── metrics.py
│   ├── executor.py
│
├── llm/
│   ├── llm_engine.py
│   ├── prompt_templates.py
│
├── data/
│   ├── healthcare_data.csv
│
├── requirements.txt
└── README.md
⚙️ Installation
git clone <repo-url>
cd HealthLens_AI_V2
Install dependencies:
pip install -r requirements.txt
Required libraries:
pandas
gradio
plotly
reportlab
kaleido
🔑 Setup LLM API

You can use:

Groq API
OpenAI-compatible API
Example (Groq):
set GROQ_API_KEY=your_api_key
▶️ Run the App
python app.py

Open in browser:

http://127.0.0.1:7860
💡 Example Queries

Try these:

“Monthly total cost trend”
“Compare cost by gender”
“ED visits by county”
“Distribution of total cost”
“Compare medical vs pharmacy cost by month”
📊 Sample Output
Interactive Plotly charts
Clean data tables
AI-generated insights
Downloadable PDF reports
⚠️ Limitations
LLM-generated code may occasionally be imperfect
Requires structured dataset
No memory across sessions
PDF formatting is basic
Depends on API latency
🚀 Future Enhancements
Chat history
RAG-based accuracy improvement
Multi-page PDF reports
Role-based access
Cloud deployment
🎯 Use Cases
Healthcare analytics
Cost optimization analysis
Claims insights
BI dashboard replacement
AI-powered reporting
🤝 Contribution

Feel free to:

Fork the repo
Create feature branches
Submit PRs
📌 Author

Saurabh Singh
AI / Data Science

⭐ Final Note

HealthLens AI V2 demonstrates how LLMs can transform traditional dashboards into conversational AI systems, combining:

👉 Data + AI + Visualization + UX