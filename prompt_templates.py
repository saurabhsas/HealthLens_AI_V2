def generate_code_prompt(query, columns):
    
    return f"""
You are a Python data analyst.

Dataset columns:
{columns}

STRICT RULES:
- Return ONLY pandas code
- Use df
- No markdown
- If comparing metrics, return multiple columns

Examples:
df.groupby('MONTH')[['MEDICAL_PAID','RX_PAID']].sum()
df.groupby('GENDER')[['MEDICAL_PAID','RX_PAID']].mean()

Query:
{query}
"""


def generate_chart_prompt(query, columns):

    return f"""
Decide chart type.

Return:
chart: line/bar/pie/histogram
sort_by: column
order: asc/desc

Columns: {columns}
Query: {query}
"""