import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import squarify


class Chart:
    def __init__(self, output_folder: str):
        self.output_folder = output_folder

    @staticmethod
    def add_data_labels(ax, params: {}):
        """

        :param ax:
        :param params:
        :return:
        """
        is_percentage = (
            params["is_percentage"]
            if (
                "is_percentage" in params.keys()
                and isinstance(params["is_percentage"], bool)
            )
            else False
        )
        fmt = (
            params["fmt"]
            if ("fmt" in params.keys() and isinstance(params["fmt"], str))
            else ".2f%"
        )
        round_number = (
            params["round_number"]
            if (
                "round_number" in params.keys()
                and isinstance(params["round_number"], int)
            )
            else 2
        )

        percentage_sign = "%" if is_percentage else ""
        for p in ax.containers:
            labels = [
                f"{h:{fmt}}{percentage_sign}"
                if round((h := v.get_width()), round_number) != 0
                else ""
                for v in p
            ]
            ax.bar_label(p, labels=labels, label_type="edge", size=9)

    def total_count_per_date_line_chart(
        self,
        data: pd.DataFrame,
        index_date_column: str,
        title: str,
        line_legend_title: str,
        filename: str,
        rule: str = "M",
        xlabel_title: str = "",
    ) -> None:
        """

        :param data:
        :param index_date_column:
        :param title:
        :param line_legend_title:
        :param xlabel_title:
        :param filename:
        :param rule:
        :return:
        """
        sns.set_style("white")
        fig, ax = plt.subplots(figsize=(15, 6))

        # Downsampling series to 1 month data and get size
        data.set_index(index_date_column).resample(rule).size().plot(
            label=line_legend_title, color="lightgrey", ax=ax
        )

        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.set(ylabel="Total Count\n", xlabel=xlabel_title)
        ax.legend(bbox_to_anchor=(1.1, 1.1), frameon=False)

        # remove all spines
        sns.despine(ax=ax, top=True, right=True, left=False, bottom=False)

        plt.savefig(os.path.join(self.output_folder, filename))

    def pie_share_chart(
        self, data_list: [], names_list: [], chart_title: str, filename: str
    ) -> None:
        """

        :param data_list:
        :param names_list:
        :param chart_title:
        :param filename:
        :return:
        """
        theme = plt.get_cmap("Set3")
        colors = [theme(1.0 * i / 3) for i in range(3)]
        # create a pie chart
        plt.pie(
            x=data_list,
            labels=names_list,
            colors=colors,
            autopct="%1.2f%%",
            pctdistance=0.6,
            textprops=dict(fontweight="normal"),
            wedgeprops={"linewidth": 6, "edgecolor": "white"},
        )

        # plot the donut chart
        fig = plt.gcf()
        fig.set_size_inches(15, 15)
        plt.title(chart_title, fontsize=14, fontweight="bold")
        plt.savefig(os.path.join(self.output_folder, filename))

    def stacked_bar_chart(
        self,
        data: pd.DataFrame,
        yaxis_values: [],
        chart_title: str,
        xlabel: str,
        ylabel: str,
        legend_title: str,
        filename: str,
    ) -> None:
        """

        :param data:
        :param yaxis_values:
        :param chart_title:
        :param xlabel:
        :param ylabel:
        :param legend_title:
        :param filename:
        :return:
        """
        # prepare barplot
        fig, ax = plt.subplots(figsize=(20, 10))

        # plot
        data.reindex(yaxis_values).plot(kind="barh", ax=ax, stacked=True, cmap="Set3")
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.9, box.height])
        ax.set_title(chart_title, fontsize=14, fontweight="bold")
        ax.set(xlabel=xlabel, ylabel=ylabel)
        ax.legend(loc="center left", bbox_to_anchor=(1, 0.5), title=legend_title)

        for i, p in enumerate(ax.containers):
            labels = [
                f"{round((h * 100), 2)}%" if round(h := v.get_width(), 3) != 0 else ""
                for v in p
            ]
            ax.bar_label(
                p,
                labels=labels,
                label_type="center",
                color="black",
                size=12,
                rotation="vertical",
            )

        # remove all spines
        sns.despine(top=True, right=True, left=True, bottom=True)
        plt.savefig(os.path.join(self.output_folder, filename))

    def grouped_bar_char(
        self,
        data: pd.DataFrame,
        yaxis_variable: str,
        xaxis_variable: str,
        hue_variable: str,
        chart_title: str,
        xlabel: str,
        ylabel: str,
        filename: str,
        data_labels_params: {} = None,
    ) -> None:
        """

        :param data:
        :param yaxis_variable:
        :param xaxis_variable:
        :param hue_variable:
        :param chart_title:
        :param xlabel:
        :param ylabel:
        :param filename:
        :param data_labels_params:
        :return:
        """
        # seaborn barplot
        fig, ax = plt.subplots(figsize=(16, 9))
        sns.barplot(
            y=yaxis_variable,
            x=xaxis_variable,
            hue=hue_variable,
            data=data,
            palette="Set3",
        )
        ax.set_title(chart_title, fontsize=13, fontweight="bold")
        ax.set(xlabel=xlabel, ylabel=ylabel)
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        ax.legend(
            bbox_to_anchor=(1.1, 0.9),
            borderaxespad=0.0,
            frameon=False,
            fontsize=10,
        )

        if (
            data_labels_params is not None
            and isinstance(data_labels_params, dict)
            and len(data_labels_params.keys()) > 0
        ):
            self.add_data_labels(ax=ax, params=data_labels_params)

        # remove all spines
        sns.despine(top=True, right=True, left=True, bottom=True)
        plt.savefig(os.path.join(self.output_folder, filename))

    def bar_chart(
        self, data: pd.Series, graph_title: str, ylabel: str, filename: str
    ) -> None:
        """

        :param data:
        :param graph_title:
        :param ylabel:
        :param filename:
        :return:
        """
        colors = ["red" if c == max(data.values) else "grey" for c in data.values]

        # prepare plot
        sns.set_style("white")
        fig, ax = plt.subplots(figsize=(12, 5))
        # plot
        ax.bar(data.index, data.values, color=colors)
        ax.plot(data, linestyle="dashed", color="black")
        ax.set_title(graph_title, fontsize=14, fontweight="bold")
        ax.set(ylabel=ylabel)

        # remove all spines
        sns.despine(ax=ax, top=True, right=True, left=True, bottom=True)
        plt.savefig(os.path.join(self.output_folder, filename))

    def heatmap_chart(
        self,
        data: pd.DataFrame,
        graph_title: str,
        filename: str,
        xlabel: str = "",
        ylabel: str = "",
    ):
        plt.figure(figsize=(10, 6))
        sns.heatmap(data, cmap="Greys")
        plt.title(graph_title, fontsize=14, fontweight="bold")
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.savefig(os.path.join(self.output_folder, filename))

    def treemap_chart(self, labels: pd.DataFrame, sizes: list, filename: str):
        colors = [plt.cm.Pastel1(i / float(len(labels))) for i in range(len(labels))]

        # plot
        plt.figure(figsize=(8, 6), dpi=80)
        squarify.plot(sizes=sizes, label=labels, color=colors, alpha=0.8)

        # Decorate
        plt.title("\nTreemap of Vehicle Manoeuvre\n", fontsize=14, fontweight="bold")
        plt.axis("off")
        plt.savefig(os.path.join(self.output_folder, filename))
