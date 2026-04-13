import re

def clean_code(code):

    code = re.sub(r"```python", "", code)
    code = re.sub(r"```", "", code)

    return code.strip()


def execute_query(code, df):

    try:
        code = clean_code(code)

        print("✅ Cleaned Code:", code)

        if "df" not in code:
            return "❌ Invalid code generated"

        result = eval(code, {"__builtins__": {}}, {"df": df})

        return result

    except Exception as e:
        print("❌ Execution Error:", e)
        return f"❌ Execution Error: {str(e)}"