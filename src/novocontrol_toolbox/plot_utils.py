import pandas as pd

def plot_mean_bounds(df, ax, parameter_to_plot, label, color="#3070b3"):
    dfmb = pd.DataFrame({"mean": df.groupby(by="Freq.")[parameter_to_plot].mean(),
                            "ub":df.groupby(by="Freq.")[parameter_to_plot].max(),
                            "lb":df.groupby(by="Freq.")[parameter_to_plot].min()})
    ax.plot(dfmb.index, dfmb["mean"], color=color, label=label)
    ax.plot(dfmb.index, dfmb["ub"], color=color, lw=0.8)
    ax.plot(dfmb.index, dfmb["lb"], color=color, lw=0.8)
    ax.fill_between(dfmb.index, dfmb["ub"], dfmb["lb"], color=color, alpha=.2)