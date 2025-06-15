import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
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
    ) -> None:
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

        # Plot initialization
        plt.figure(figsize=figsize)

        # Plot type selection
        if plttype == 'bar':
            if row or col:
                g = sns.catplot(data=df, x=x, y=y, hue=hue,
                                row=row, col=col, kind='bar',
                                palette=palette, height=figsize[1])
            else:
                sns.barplot(data=df, x=x, y=y, hue=hue, palette=palette)

        elif plttype == 'line':
            sns.lineplot(data=df, x=x, y=y, hue=hue, palette=palette)

        elif plttype == 'scatter':
            sns.scatterplot(data=df, x=x, y=y, hue=hue, palette=palette)

        elif plttype == 'box':
            sns.boxplot(data=df, x=x, y=y, hue=hue, palette=palette)

        elif plttype == 'violin':
            sns.violinplot(data=df, x=x, y=y, hue=hue, palette=palette)

        elif plttype == 'hist':
            sns.histplot(data=df, x=x, y=y, hue=hue, palette=palette)

        elif plttype == 'heatmap':
            if x and y and aggregation:
                pivot = df.pivot_table(index=x, columns=y, aggfunc=aggregation)
                sns.heatmap(pivot, annot=True, fmt='g')
            else:
                raise ValueError("To generate Heatmap plot, aggregation is required")

        else:
            raise ValueError(f"Unknown plot type: {plttype}")

        if title:
            plt.title(title)

        if x and len(df[x].unique()) > 5:
            plt.xticks(rotation=45)

        plt.tight_layout()
        plt.show()