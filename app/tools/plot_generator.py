import seaborn as sns
import pandas as pd
from matplotlib.figure import Figure
from typing import Optional, Dict


class PlotGenerator:
    @staticmethod
    def generate(
            data: pd.DataFrame,
            plttype: str = 'bar',
            x: Optional[str] = None,
            y: Optional[str] = None,
            hue: Optional[str] = None,
            row: Optional[str] = None,
            col: Optional[str] = None,
            filters: Optional[Dict[str, str]] = None,
            aggregation: Optional[str] = None,
            sort: Optional[str] = None,
            palette: str = 'viridis',
            title: Optional[str] = None,
            figsize: tuple = (10, 6)
    ) -> Figure:
        df = data.copy()

        # Filter data
        if filters:
            for column, value in filters.items():
                if isinstance(value, list):
                    df = df[df[column].isin(value)]
                else:
                    df = df[df[column] == value]

        # Data aggregation if required
        if aggregation and x and y:
            df_agg = df.groupby(x)[y].agg(aggregation).reset_index()
            df = df_agg

        # Sort data
        if sort:
            if sort.lower() == 'asc':
                df = df.sort_values(by=x if x else y, ascending=True)
            elif sort.lower() == 'desc':
                df = df.sort_values(by=x if x else y, ascending=False)

        fig = Figure(figsize=figsize)
        ax = fig.add_subplot(111)

        try:
            # Plot type selection
            if plttype == 'bar':
                if row or col:
                    fig.clf()
                    g = sns.catplot(data=df, x=x, y=y, hue=hue,
                                    row=row, col=col, kind='bar',
                                    palette=palette, height=figsize[1])
                    fig = g.fig
                    if hue:
                        g.add_legend()
                else:
                    sns.barplot(data=df, x=x, y=y, hue=hue, palette=palette, ax=ax)
                    if hue:
                        ax.legend(title=hue)

            elif plttype == 'line':
                if row or col:
                    fig.clf()
                    g = sns.relplot(data=df, x=x, y=y, hue=hue,
                                    row=row, col=col, kind='line',
                                    palette=palette, height=figsize[1])
                    fig = g.fig
                    if hue:
                        g.add_legend()
                else:
                    sns.lineplot(data=df, x=x, y=y, hue=hue, palette=palette, ax=ax)
                    if hue:
                        ax.legend(title=hue)

            elif plttype == 'scatter':
                if row or col:
                    fig.clf()
                    g = sns.relplot(data=df, x=x, y=y, hue=hue,
                                    row=row, col=col, kind='scatter',
                                    palette=palette, height=figsize[1])
                    fig = g.fig
                    if hue:
                        g.add_legend()
                else:
                    sns.scatterplot(data=df, x=x, y=y, hue=hue, palette=palette, ax=ax)
                    if hue:
                        ax.legend(title=hue)

            elif plttype == 'box':
                sns.boxplot(data=df, x=x, y=y, hue=hue, palette=palette, ax=ax)
                if hue:
                    ax.legend(title=hue)

            elif plttype == 'violin':
                sns.violinplot(data=df, x=x, y=y, hue=hue, palette=palette, ax=ax)
                if hue:
                    ax.legend(title=hue)

            elif plttype == 'hist':
                sns.histplot(data=df, x=x, y=y, hue=hue, palette=palette, ax=ax)
                if hue:
                    ax.legend(title=hue)

            elif plttype == 'kde':
                sns.kdeplot(data=df, x=x, y=y, hue=hue, palette=palette, ax=ax)
                if hue:
                    ax.legend(title=hue)

            elif plttype == 'heatmap':
                if x and y and aggregation:
                    pivot = df.pivot_table(index=x, columns=y, aggfunc=aggregation)
                    sns.heatmap(pivot, annot=True, fmt='g', ax=ax)
                else:
                    raise ValueError("To generate Heatmap plot, aggregation is required")

            elif plttype == 'pie':
                if x and y:
                    df_agg = df.groupby(x)[y].sum()
                    df_agg.plot.pie(ax=ax, autopct='%1.1f%%')
                else:
                    raise ValueError("Pie chart requires x and y parameters")

            elif plttype == 'area':
                if x and y:
                    if hue:
                        df_pivot = df.pivot(index=x, columns=hue, values=y)
                        df_pivot.plot.area(ax=ax, stacked=True)
                    else:
                        df.plot.area(x=x, y=y, ax=ax)
                else:
                    raise ValueError("Area chart requires x and y parameters")

            else:
                raise ValueError(f"Unknown plot type: {plttype}")

            if title:
                ax.set_title(title)

            if x and len(df[x].unique()) > 5:
                ax.tick_params(axis='x', rotation=45)

            fig.tight_layout()
            return fig

        except Exception as e:
            print(f"Error generating plot: {e}")
            return None