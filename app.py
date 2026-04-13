import pandas as pd
import gradio as gr
import plotly.express as px
import os
import tempfile
import uuid

from core.data_processing import preprocess_data
from core.metrics import get_kpis
from core.executor import execute_query

from llm.llm_engine import ask_llm
from llm.prompt_templates import generate_code_prompt, generate_chart_prompt

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table as PDFTable
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter


# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv("data/healthcare_data.csv")
df = preprocess_data(df)


# -----------------------------
# HELPERS
# -----------------------------
def apply_filters(df, gender, lob, county):

    filtered = df.copy()

    if gender != "All":
        filtered = filtered[filtered["GENDER"] == gender]

    if lob != "All":
        filtered = filtered[filtered["LINEOFBUSINESS"] == lob]

    if county != "All":
        filtered = filtered[filtered["COUNTY"] == county]

    return filtered


def rename_columns(df):
    return df.rename(columns={
        "MEDICAL_PAID": "Medical Cost",
        "RX_PAID": "Pharmacy Cost",
        "PAID": "Total Cost"
    })


def format_currency_columns(df):
    
    cost_columns = ["MEDICAL_PAID", "RX_PAID", "PAID",
                    "Medical Cost", "Pharmacy Cost", "Total Cost"]

    for col in df.columns:
        if col in cost_columns:
            df[col] = df[col].apply(
                lambda x: f"${int(x):,}" if pd.notnull(x) else x
            )

    return df


def parse_chart_decision(text):

    chart = "bar"
    sort_by = None
    order = "desc"

    for line in text.split("\n"):
        if "chart:" in line:
            chart = line.split(":")[1].strip()
        elif "sort_by:" in line:
            sort_by = line.split(":")[1].strip()
        elif "order:" in line:
            order = line.split(":")[1].strip()

    return chart, sort_by, order


# -----------------------------
# PDF GENERATOR
# -----------------------------
def generate_pdf(kpis, fig, table, insights):

    temp_dir = tempfile.gettempdir()
    file_name = f"healthlens_{uuid.uuid4().hex}.pdf"
    file_path = os.path.join(temp_dir, file_name)

    doc = SimpleDocTemplate(file_path, pagesize=letter)
    styles = getSampleStyleSheet()

    elements = []

    elements.append(Paragraph("HealthLens AI Report", styles["Title"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Key Metrics", styles["Heading2"]))
    for k, v in kpis.items():
        elements.append(Paragraph(f"{k}: {v}", styles["Normal"]))

    elements.append(Spacer(1, 12))

    if fig:
        chart_path = os.path.join(temp_dir, f"chart_{uuid.uuid4().hex}.png")
        fig.write_image(chart_path)

        elements.append(Paragraph("Visualization", styles["Heading2"]))
        elements.append(Image(chart_path, width=400, height=250))
        elements.append(Spacer(1, 12))

    if table is not None and not table.empty:
        elements.append(Paragraph("Data Table", styles["Heading2"]))
        data = [table.columns.tolist()] + table.values.tolist()
        elements.append(PDFTable(data))
        elements.append(Spacer(1, 12))

    elements.append(Paragraph("Insights", styles["Heading2"]))
    elements.append(Paragraph(insights.replace("\n", "<br/>"), styles["Normal"]))

    doc.build(elements)

    return file_path


# -----------------------------
# CLEAR FUNCTION 🧹
# -----------------------------
def clear_dashboard():
    return [
        "",  # query
        "", "", "", "", "",  # KPIs
        None,  # chart
        None,  # table
        "",  # insights
        None  # pdf
    ]


# -----------------------------
# MAIN FUNCTION
# -----------------------------
def run_dashboard(query, gender, lob, county):

    filtered_df = apply_filters(df, gender, lob, county)
    kpis = get_kpis(filtered_df)

    if not query or query.strip() == "":
        result = filtered_df.groupby("MONTH")[["MEDICAL_PAID", "RX_PAID"]].sum()
    else:
        code = ask_llm(generate_code_prompt(query, filtered_df.columns.tolist()))
        result = execute_query(code, filtered_df)

    if isinstance(result, str):
        result = filtered_df.groupby("MONTH")[["MEDICAL_PAID", "RX_PAID"]].sum()

    try:
        table_raw = result.reset_index()
    except:
        table_raw = pd.DataFrame(result)

    decision = ask_llm(generate_chart_prompt(query, table_raw.columns.tolist()))
    chart_type, sort_by, order = parse_chart_decision(decision)

    if sort_by in table_raw.columns:
        table_raw = table_raw.sort_values(by=sort_by, ascending=(order == "asc"))

    numeric_cols = table_raw.select_dtypes(include="number").columns.tolist()
    is_time_series = "MONTH" in table_raw.columns or "DATE" in table_raw.columns

    # -----------------------------
    # PLOTLY CHARTS
    # -----------------------------
    fig = None

    try:
        if is_time_series:
            fig = px.line(
                table_raw,
                x=table_raw.columns[0],
                y=numeric_cols,
                markers=True,
                title="Trend Analysis"
            )

        elif len(numeric_cols) > 1:
            fig = px.bar(
                table_raw,
                x=table_raw.columns[0],
                y=numeric_cols,
                barmode="group",
                title="Comparison Analysis"
            )

        else:
            if chart_type == "pie":
                fig = px.pie(
                    table_raw,
                    names=table_raw.columns[0],
                    values=table_raw.columns[1]
                )

            elif chart_type == "histogram":
                fig = px.histogram(
                    table_raw,
                    x=table_raw.columns[1],
                    nbins=10
                )

            else:
                fig = px.bar(
                    table_raw,
                    x=table_raw.columns[0],
                    y=table_raw.columns[1]
                )

    except Exception as e:
        print("Plotly Error:", e)

    table = rename_columns(table_raw.copy())
    table = format_currency_columns(table)

    insights = ask_llm(f"""
Provide 3 short business insights:
{str(result.head())}
""")

    pdf_path = generate_pdf(kpis, fig, table, insights)

    return list(kpis.values()) + [fig, table, insights, pdf_path]


# -----------------------------
# UI (UNCHANGED + BUTTONS)
# -----------------------------
with gr.Blocks(title="HealthLens AI") as app:

    gr.Markdown("""
    # 🏥 HealthLens AI  
    ### Smart Healthcare Analytics Dashboard
    """)

    gr.Markdown("---")

    with gr.Row():

        with gr.Column(scale=1):

            gr.Markdown("### 🔎 Filters")

            gender = gr.Dropdown(["All"] + df["GENDER"].dropna().unique().tolist(), value="All", label="Gender")
            lob = gr.Dropdown(["All"] + df["LINEOFBUSINESS"].dropna().unique().tolist(), value="All", label="Line of Business")
            county = gr.Dropdown(["All"] + df["COUNTY"].dropna().unique().tolist(), value="All", label="County")

            gr.Markdown("---")
            gr.Markdown("💡 Tip: Apply filters before asking a question")

        with gr.Column(scale=4):

            gr.Markdown("### 💬 Ask Your Question")

            query = gr.Textbox(label="Type your question",
                               placeholder="e.g., Show monthly cost trend, Compare ED visits by gender...",
                               lines=2)

            with gr.Row():
                btn = gr.Button("🚀 Run Analysis", variant="stop", scale=1)
                clear_btn = gr.Button("🧹 Clear", variant="stop", scale=1)

            gr.Markdown("---")

            gr.Markdown("### 📈 Key Metrics")

            with gr.Row():
                k1 = gr.Textbox(label="👥 Total Members")
                k2 = gr.Textbox(label="💰 Total Cost")
                k3 = gr.Textbox(label="📊 Avg Cost")
                k4 = gr.Textbox(label="🏥 ED Visits")
                k5 = gr.Textbox(label="🛏️ IP Visits")

            gr.Markdown("---")

            gr.Markdown("### 📊 Visualization")
            chart = gr.Plot()

            gr.Markdown("---")

            gr.Markdown("### 📋 Data Table")
            table = gr.Dataframe()

            gr.Markdown("---")

            gr.Markdown("### 🧠 Insights")
            insights = gr.Textbox(lines=5)

            gr.Markdown("---")

            pdf_file = gr.File(label="📄 Download Report")


    # RUN
    btn.click(run_dashboard,
        inputs=[query, gender, lob, county],
        outputs=[k1, k2, k3, k4, k5, chart, table, insights, pdf_file]
    )

    # CLEAR
    clear_btn.click(
        clear_dashboard,
        inputs=[],
        outputs=[query, k1, k2, k3, k4, k5, chart, table, insights, pdf_file]
    )

    # FILTER AUTO UPDATE
    gender.change(run_dashboard,
        inputs=[query, gender, lob, county],
        outputs=[k1, k2, k3, k4, k5, chart, table, insights, pdf_file]
    )

    lob.change(run_dashboard,
        inputs=[query, gender, lob, county],
        outputs=[k1, k2, k3, k4, k5, chart, table, insights, pdf_file]
    )

    county.change(run_dashboard,
        inputs=[query, gender, lob, county],
        outputs=[k1, k2, k3, k4, k5, chart, table, insights, pdf_file]
    )


if __name__ == "__main__":
    app.launch(theme=gr.themes.Soft())