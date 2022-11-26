import pyecharts.options as opts
from pyecharts.globals import ThemeType


def update_global_opts(chart, title_opts=None, xaxis_opts=None, yaxis_opts=None, legend_opts=None, x_rotate=None):
    # 图表类型
    chart_type = chart.get_options()['series'][0]['type']
    dic = dict(
        xaxis_opts=opts.AxisOpts(splitline_opts=opts.SplitLineOpts(is_show=False),
                                 axislabel_opts=opts.LabelOpts(rotate=x_rotate)),
        yaxis_opts=opts.AxisOpts(splitline_opts=opts.SplitLineOpts(is_show=False)),
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
        toolbox_opts=opts.ToolboxOpts(is_show=True,
                                      orient='horizontal',
                                      feature={
                                          "saveAsImage": {},
                                          "dataZoom": {"yAxisIndex": "none"},
                                          "restore": {},
                                          "magicType": {"show": True, "type": ["line", "bar"]},
                                          "dataView": {},
                                      }
                                      ),
    )

    # 标题配置
    if title_opts:
        dic['title_opts'] = opts.TitleOpts(**title_opts)
    if xaxis_opts:
        dic['xaxis_opts'] = opts.AxisOpts(splitline_opts=opts.SplitLineOpts(is_show=False),
                                          axislabel_opts=opts.LabelOpts(rotate=x_rotate), **xaxis_opts)
    if yaxis_opts:
        dic['yaxis_opts'] = opts.AxisOpts(splitline_opts=opts.SplitLineOpts(is_show=False),**yaxis_opts)
    # 图例配置
    if legend_opts:
        dic['legend_opts'] = opts.LegendOpts(**legend_opts)


    #     if chart_type == 'bar':
    #         # 视觉映射
    #         dic.update(
    #             visualmap_opts=opts.VisualMapOpts(
    #                 orient="horizontal",
    #                 pos_left="center",
    #                 range_text=["High Score", "Low Score"],
    #                 max_=10,
    #                 range_color=["#D7DA8B", "#E15457"],),
    #         )
    return dic


def update_init_opts(width="900px", height="600px", theme=None, bg_color=None):
    dic = dict(
        width=width,
        height=height,
        theme=ThemeType.CHALK,
        bg_color='rgba(246, 250, 252, 1)',
    )
    if theme:
        dic['theme'] = theme
    if bg_color:
        dic['bg_color'] = bg_color
    init_opts = opts.InitOpts(**dic)
    return init_opts
