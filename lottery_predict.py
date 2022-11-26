from typing import List

import pandas as pd

import pyecharts.options as opts
from pyecharts.charts import Bar, Line, Grid, Page, Tab
from pyecharts.globals import ThemeType, CurrentConfig, NotebookType
from chart_opts import update_init_opts, update_global_opts


from jinja2 import Environment, FileSystemLoader
# 必须声明环境类型
# CurrentConfig.NOTEBOOK_TYPE = NotebookType.JUPYTER_NOTEBOOK
CurrentConfig.GLOBAL_ENV = Environment(loader=FileSystemLoader("./templates"))


class Lottery:

    cols = ['red1', 'red2', 'red3', 'red4', 'red5', 'red6', 'blue']

    def __init__(self, data):
        self.data = self.data_processing(data)

    def __str__(self):
        return self.data.info()

    @classmethod
    def data_processing(cls, data: List[list]) -> pd.DataFrame:
        df = pd.DataFrame(data, columns=['period'] + cls.cols + ['date']).sort_values('date')
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        df.set_index('date', inplace=True)
        # 转换为int类型
        df = df.astype({i: int for i in cls.cols})
        return cls.build_feature(df)

    @classmethod
    def build_feature(cls, data: pd.DataFrame) -> pd.DataFrame:
        """构建特征：奇偶个数、连号个数"""
        def is_odd(x):
            count = 0
            for i in x:
                if i & 1 == 1:
                    count += 1
            return count

        def is_continuous(x):
            count = 1
            q = [x[0]]
            for i in range(1, len(x)):
                if q and x[i] - q[-1] != 1:
                    count = max(len(q), count)
                    q.clear()
                q.append(x[i])
            return max(len(q), count)

        data['odd'] = data[cls.cols].apply(lambda x: is_odd(x), axis=1)
        data['continuous'] = data[cls.cols].apply(lambda x: is_continuous(x), axis=1)

        return data

    def draw_trend(self, col: str) -> Grid:
        """绘制各号码走势曲线及出现次数分析"""
        data = self.data
        page = Page(layout=Page.DraggablePageLayout, page_title='实时彩票分析平台')
        tab = Tab()
        start, end = data.index[0].strftime("%Y-%m-%d"), data.index[-1].strftime("%Y-%m-%d")

        color = '#588dd5' if col == 'blue' else '#d0648a'



        count = data[col].value_counts().sort_index()
        bar = (
            Bar(init_opts=update_init_opts())
                .add_yaxis('出现次数', count.values.tolist(), itemstyle_opts=opts.ItemStyleOpts(color=color))
                .add_xaxis(count.index.tolist())
                .reversal_axis()
        )

        line = (
            Line(init_opts=update_init_opts())
                .add_xaxis(data.index.strftime("%m-%d").tolist())
                .add_yaxis(
                '号码',
                data[col].values.tolist(),
                linestyle_opts=opts.LineStyleOpts(width=2, color=color,),
                markpoint_opts=opts.MarkPointOpts(
                    data=[
                        opts.MarkPointItem(type_="max", name="最大值"),
                        opts.MarkPointItem(type_="min", name="最小值"),
                    ]
                ),
                markline_opts=opts.MarkLineOpts(
                    data=[
                        opts.MarkLineItem(type_="average", name="平均值"),
                    ]
                ),
            )
        )

        # 'pos_left': '2%'表示右边留白2%
        global_opts_bar = update_global_opts(bar,
                                             yaxis_opts={'type_': 'category'},
                                             title_opts={'title': f'{col} count&tendency', 'pos_left': '2%'},
                                             legend_opts={'pos_left': '25%', 'is_show': False})
        global_opts_line = update_global_opts(line,
                                              x_rotate=45,
                                              title_opts={ 'pos_left': '35%'},
                                              legend_opts={'pos_right': '25%', 'is_show': False}, )

        line.set_global_opts(**global_opts_line)
        bar.set_global_opts(**global_opts_bar)

        grid = (
            Grid(init_opts=update_init_opts(width='100%'))
                .add(bar, grid_opts=opts.GridOpts(pos_right="80%"))
                .add(line, grid_opts=opts.GridOpts(pos_left="30%"))
        )

        # tab.add(grid, col)
        return grid

    def draw_features(self) -> Line:
        data = self.data
        start, end = data.index[0].strftime("%Y-%m-%d"), data.index[-1].strftime("%Y-%m-%d")
        line = (
            Line(init_opts=update_init_opts(width='100%'))
                .add_xaxis(data.index.strftime("%m-%d").tolist())
                .add_yaxis('odd', data['odd'].values.tolist())
                .add_yaxis('continuous', data['continuous'].values.tolist())
        )

        global_opts = update_global_opts(line, x_rotate=30)
        line.set_global_opts(**global_opts)
        # todo tab组件宽度设置显示不正常，这里直接使用line cls.tab.add(line, f'【{start}至{end}】')
        # cls.line = line
        return line

    # def draw_charts(self):
    #     """绘制所有图表"""
    #     # data = self.data_processing()
    #     # self.draw_trend(data)
    #     # self.draw_features(data)
    #
    #     # Lottery.tab.render("tab.html")
    #     # Lottery.page.render("page_draggable_layout.html")
    #
    #     return Lottery.page, Lottery.line








