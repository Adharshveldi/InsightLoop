import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import base64
import ollama

# ---- Page Config ---- #
st.set_page_config(page_title="InsightLoop", layout="wide")

# ---- Custom CSS for animation and title style ---- #
st.markdown("""
    <style>
        body {
            animation: fadeIn 1.2s ease-in-out;
        }
        @keyframes fadeIn {
            0% {opacity: 0; transform: translateY(-10px);}
            100% {opacity: 1; transform: translateY(0);}
        }
        .app-title {
            text-align: center;
            font-size: 3em;
            font-weight: 900;
            letter-spacing: 2px;
            background: linear-gradient(to right, #00b4db, #0083b0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0;
            animation: slideIn 1s ease-out;
        }
        .subtitle {
            text-align: center;
            font-size: 1.2em;
            color: #444;
            font-style: italic;
            animation: fadeInSub 2s ease-in;
        }
        @keyframes slideIn {
            0% {opacity: 0; transform: translateY(-30px);}
            100% {opacity: 1; transform: translateY(0);}
        }
        @keyframes fadeInSub {
            0% {opacity: 0;}
            100% {opacity: 1;}
        }
    </style>
""", unsafe_allow_html=True)

# ---- Animated & Centered Title ---- #
st.markdown("<div class='app-title'>InsightLoop</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Upload. Clean. Ask. Visualize.</div>", unsafe_allow_html=True)
st.markdown("---")

# ---- Session State Setup ---- #
if 'datasets' not in st.session_state:
    st.session_state['datasets'] = {}
if 'selected_dataset_name' not in st.session_state:
    st.session_state['selected_dataset_name'] = None

# ---- Sidebar Nav ---- #
with st.sidebar:
    st.markdown("### 🚀 Navigate")
    page = st.radio("Choose a page", ["Upload & Preview", "Filter Data", "Ask AI", "Visualize", "Auto Chart Suggestion"])

# ---- Upload Page ---- #
if page == "Upload & Preview":
    st.subheader("📄 Upload Your Dataset")
    uploaded_files = st.file_uploader("Upload CSV or Excel files", type=['csv', 'xlsx'], accept_multiple_files=True)

    for uploaded_file in uploaded_files or []:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.session_state['datasets'][uploaded_file.name] = df
        except Exception as e:
            st.error(f"Failed to read {uploaded_file.name}: {e}")

    if st.session_state['datasets']:
        st.subheader("👀 Data Preview")
        dataset_name = st.selectbox("Choose a dataset to preview", list(st.session_state['datasets'].keys()))
        st.session_state['selected_dataset_name'] = dataset_name
        st.dataframe(st.session_state['datasets'][dataset_name])

# ---- Filter Page ---- #
elif page == "Filter Data":
    st.subheader("🩹 Clean & Filter Data")
    dataset_name = st.session_state.get("selected_dataset_name")
    if dataset_name:
        df = st.session_state['datasets'][dataset_name].copy()

        if st.checkbox("🧐 Remove rows with null values"):
            df = df.dropna()

        if st.checkbox("⛔ Remove outliers (IQR method)"):
            numeric_cols = df.select_dtypes(include='number')
            Q1 = numeric_cols.quantile(0.25)
            Q3 = numeric_cols.quantile(0.75)
            IQR = Q3 - Q1
            df = df[~((numeric_cols < (Q1 - 1.5 * IQR)) | (numeric_cols > (Q3 + 1.5 * IQR))).any(axis=1)]

        st.markdown("### 🔍 Filter by Columns")
        with st.expander("Click to filter columns"):
            for col in df.columns:
                if pd.api.types.is_datetime64_any_dtype(df[col]):
                    st.markdown(f"**Filter by {col} (Date Range)**")
                    start_date, end_date = st.date_input(
                        f"Select range for {col}",
                        value=[df[col].min(), df[col].max()],
                        key=col
                    )
                    if start_date and end_date:
                        df = df[(df[col] >= pd.to_datetime(start_date)) & (df[col] <= pd.to_datetime(end_date))]

                elif pd.api.types.is_numeric_dtype(df[col]):
                    st.markdown(f"**Filter by {col} (Numeric Range)**")
                    min_val, max_val = float(df[col].min()), float(df[col].max())
                    selected_range = st.slider(
                        f"Select range for {col}", min_val, max_val, (min_val, max_val), key=col
                    )
                    df = df[df[col].between(*selected_range)]

                elif df[col].nunique() <= 50:
                    st.markdown(f"**Filter by {col} (Select values)**")
                    selected_vals = st.multiselect(
                        f"Select one or more {col}", options=df[col].dropna().unique(), key=col
                    )
                    if selected_vals:
                        df = df[df[col].isin(selected_vals)]

        st.dataframe(df)
        to_download = df.to_csv(index=False).encode('utf-8')
        st.download_button("📅 Download Cleaned Dataset", to_download, f"cleaned_{dataset_name}.csv", "text/csv")

# ---- Ask AI ---- #
elif page == "Ask AI":
    st.subheader("💬 Ask the AI About Your Data")
    dataset_name = st.session_state.get("selected_dataset_name")
    if dataset_name:
        df = st.session_state['datasets'][dataset_name]
        st.dataframe(df.head(5))
        question = st.text_input("Ask a question about your data:")
        if question:
            prompt = f"""
Answer this question based only on the data:
{question}
Here is the data:
{df.head(20).to_csv(index=False)}
Only give the answer. Do not generate code.
"""
            with st.spinner("🧠 Thinking..."):
                response = ollama.chat(
                    model="mistral",
                    messages=[{"role": "user", "content": prompt}]
                )
                st.success("AI Response:")
                st.markdown(response['message']['content'])

# ---- Visualize ---- #
elif page == "Visualize":
    st.subheader("📊 Visualize Your Data")
    dataset_name = st.session_state.get("selected_dataset_name")
    if dataset_name:
        df = st.session_state['datasets'][dataset_name]

        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        numeric_cols = df.select_dtypes(include='number').columns.tolist()
        datetime_cols = df.select_dtypes(include='datetime64[ns]').columns.tolist()

        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_datetime(df[col])
                except:
                    pass

        chart_type = st.selectbox("Choose chart type", ["Bar", "Line", "Scatter", "Pie", "Heatmap"])
        x_col = st.selectbox("X-axis", df.columns)
        y_col = st.selectbox("Y-axis", numeric_cols)

        fig = None
        if chart_type == "Bar":
            fig = px.bar(df, x=x_col, y=y_col)
        elif chart_type == "Line":
            fig = px.line(df, x=x_col, y=y_col)
        elif chart_type == "Scatter":
            fig = px.scatter(df, x=x_col, y=y_col)
        elif chart_type == "Pie":
            if x_col in categorical_cols and y_col in numeric_cols:
                fig = px.pie(df, values=y_col, names=x_col)
            else:
                st.warning("Pie chart requires categorical x and numeric y.")
        elif chart_type == "Heatmap":
            if len(numeric_cols) >= 2:
                corr = df[numeric_cols].corr()
                fig = px.imshow(corr, text_auto=True, color_continuous_scale='Viridis')
            else:
                st.warning("Need 2+ numeric columns for heatmap.")

        if fig:
            st.plotly_chart(fig, use_container_width=True)
            try:
                img_bytes = fig.to_image(format="png")
                b64 = base64.b64encode(img_bytes).decode()
                href = f'<a href="data:image/png;base64,{b64}" download="chart.png">📅 Download Chart as Image</a>'
                st.markdown(href, unsafe_allow_html=True)
            except Exception:
                st.warning("Install kaleido: pip install -U kaleido")

# ---- Auto Chart Suggestion ---- #
elif page == "Auto Chart Suggestion":
    st.subheader("🤖 Auto Chart Suggestion")
    dataset_name = st.session_state.get("selected_dataset_name")
    if dataset_name:
        df = st.session_state['datasets'][dataset_name]

        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_datetime(df[col])
                except:
                    pass

        numeric_cols = df.select_dtypes(include='number').columns.tolist()
        datetime_cols = df.select_dtypes(include='datetime64[ns]').columns.tolist()
        categorical_cols = df.select_dtypes(include='object').columns.tolist()

        def suggest_chart(df):
            if len(datetime_cols) > 0 and len(numeric_cols) > 0:
                return "Line"
            elif len(categorical_cols) > 0 and len(numeric_cols) == 1:
                return "Bar"
            elif len(numeric_cols) >= 2:
                return "Scatter"
            elif len(numeric_cols) >= 5:
                return "Heatmap"
            else:
                return "Bar"

        chart_type = suggest_chart(df)
        st.markdown(f"### ✅ Suggested Chart Type: **{chart_type} Plot**")
        st.dataframe(df.head())

        x_col = df.columns[0]
        y_col = numeric_cols[0] if numeric_cols else None
        fig = None

        if chart_type == "Bar":
            fig = px.bar(df, x=x_col, y=y_col)
        elif chart_type == "Line":
            fig = px.line(df, x=x_col, y=y_col)
        elif chart_type == "Scatter":
            if len(numeric_cols) >= 2:
                fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1])
        elif chart_type == "Heatmap":
            if len(numeric_cols) >= 2:
                fig = px.imshow(df[numeric_cols].corr(), text_auto=True)

        if fig:
            st.plotly_chart(fig, use_container_width=True)