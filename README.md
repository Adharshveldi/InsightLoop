🎯 InsightLoop
Upload. Clean. Ask. Visualize.

InsightLoop is an AI-powered business intelligence assistant built with Streamlit. It empowers users—especially non-tech users—to upload datasets, clean/filter data, ask AI questions, and visualize insights interactively.


🚀 Features

- Upload CSV or Excel files effortlessly
- Clean & Filter datasets with:
  - Null value removal
  - Outlier removal (IQR method)
  - Smart column filtering (text, number, date)
- Ask AI natural language questions about your data
- Visualize data using:
  - Bar, Line, Scatter, Pie, Heatmap charts
- Auto Chart Suggestion based on data types
- Chart Downloads as PNG 


🧠 Built With

- Python + Streamlit – Interactive UI
- Pandas – Data manipulation
- Plotly – Visualizations
- Ollama + Mistral – LLM-powered Q&A


🛠 How It Works

1. Upload: Select and upload `.csv` or `.xlsx` datasets.
2. Clean: Remove missing values and outliers.
3. Filter: Slice data with interactive controls.
4. Ask: Type questions like _"What is the average price?"_
5. Visualize: Pick chart types or let the system suggest one.


🧪 Example Questions

- What’s the highest rated product?
- Which category has the most stock?
- Show me trends over time.


📸 Screenshots

> Included in the `/images` folder of the repo. You’ll see:
Upload & Preview
![image alt](https://github.com/Adharshveldi/InsightLoop/blob/95b9aac9ad10937ec88ee0460934faa143f90ac6/Upload%26Preview.jpg)
Filter and Clean
![image alt](https://github.com/Adharshveldi/InsightLoop/blob/95b9aac9ad10937ec88ee0460934faa143f90ac6/Filter%20Data.jpg)
Ask AI
![image alt](https://github.com/Adharshveldi/InsightLoop/blob/95b9aac9ad10937ec88ee0460934faa143f90ac6/Ask%20AI.jpg)
Visualize
![image alt](https://github.com/Adharshveldi/InsightLoop/blob/95b9aac9ad10937ec88ee0460934faa143f90ac6/Visualize.jpg)
Auto Chart Suggestion
![image alt](https://github.com/Adharshveldi/InsightLoop/blob/95b9aac9ad10937ec88ee0460934faa143f90ac6/Auto%20Chart%20Suggestion.jpg)


📦 Setup Locally

```bash
git clone https://github.com/Adharshveldi/InsightLoop.git
cd InsightLoop
pip install -r requirements.txt
streamlit run app.py
