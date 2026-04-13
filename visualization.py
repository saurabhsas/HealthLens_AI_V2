import matplotlib.pyplot as plt
import pandas as pd

def plot_data(result):

    fig, ax = plt.subplots()

    try:
        if isinstance(result, pd.Series):
            result = result.reset_index()

        # TIME SERIES
        if "MONTH" in result.columns:
            result.plot(x="MONTH", y=result.columns[1], kind="line", ax=ax)

        # CATEGORY
        elif result.shape[1] == 2:
            result.plot(x=result.columns[0], y=result.columns[1], kind="bar", ax=ax)

        # DISTRIBUTION
        else:
            result.plot(kind="hist", bins=10, ax=ax)

        ax.set_title("Analysis Result")

        return fig

    except Exception as e:
        print("❌ Plot Error:", e)
        return None