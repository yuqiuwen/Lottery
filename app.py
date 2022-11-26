import datetime
from typing import List
import requests
import numpy as np

from flask import Flask, request, redirect, url_for, render_template, make_response
from jinja2.utils import markupsafe
from jinja2 import Environment, FileSystemLoader
from lxml import etree
import platform
from scipy.stats import truncnorm

from pyecharts.globals import CurrentConfig
CurrentConfig.GLOBAL_ENV = Environment(loader=FileSystemLoader("./templates"))

from flask_bootstrap import Bootstrap4

from lottery_predict import Lottery


app = Flask(__name__, static_folder="templates")
bootstrap = Bootstrap4()
bootstrap.init_app(app)

HOST = "http://47.98.97.198:5000/"
if platform.system() == 'Windows':
    HOST = "http://127.0.0.1:5000/"


@app.route('/')
def index():
    cur_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    limit = request.args.get('limit')
    menu_id = request.args.get('menu_id')
    col = request.args.get('col')
    url = HOST + "trend"
    if not limit:
        limit = 50
    if not col:
        col = 'red1'
    if menu_id and int(menu_id) == 1:
        url = HOST + "features"

    return render_template("./html/index.html", cur_time=cur_time, limit=limit, menu_id=url, col=col)


@app.route('/trend')
def trend():
    limit = request.args.get('limit')
    col = request.args.get('col')
    if not limit:
        limit = 50

    data = fetch_data(limit=int(limit))
    chart = Lottery(data).draw_trend(col)
    # return markupsafe.Markup(chart.render_embed())
    return chart.dump_options_with_quotes()


@app.route('/features')
def draw_charts():
    limit = request.args.get('limit')
    if not limit:
        limit = 30
    data = fetch_data(limit=int(limit))
    chart = Lottery(data).draw_features()
    return chart.dump_options_with_quotes()


def fetch_data(start: int = None, end: int = '', limit: int = None) -> List[list]:
    """抓取并解析数据"""
    base_url = "http://datachart.500.com/ssq/history/newinc/history.php"
    url = f"{base_url}?start={start}&end={end}"
    if limit:
        url = f"{base_url}?limit={limit}&sort=0"

    res = requests.get(url)
    html = etree.HTML(res.content.decode("utf-8"))
    # 解析为字符串，并按照utf8解码
    # doc = etree.tostring(html, pretty_print=True, encoding="utf-8").decode('utf-8')
    el = html.xpath("//tbody[@id='tdata']/tr[@class='t_tr1']")
    result = []
    for e in el:
        # 提取指定位置的td
        # 用这种方式也可：e.xpath("./td[not(text()='\xa0')]/text()")，其中\xa0表示不间断空白符，即&nbsp;
        temp = e.xpath("./td[not(position()>=9 and position()<=last()-1)]/text()")
        # 提取出来的文本类型为lxml.etree._ElementUnicodeResult，需要转换为字符串
        result.append(list(map(str, temp)))
    return result


@app.route('/latest', methods=['GET'])
@app.context_processor
def get_latest():
    res = fetch_data(limit=1)[0]
    return {"latest": res[1:-1], "date": res[-1]}


@app.route('/predict', methods=['GET'], endpoint='predict')
# @app.context_processor
def auto_predict():
    df = Lottery.data_processing(fetch_data(limit=100))
    cols = [col for col in df.columns if 'red' in col]
    low, high, sd = 1, 33, 1
    random_numbers = []
    for col in cols:
        mod = df[col].mode()[0]
        random_numbers.append(round(truncnorm((low - mod) / sd, (high - mod) / sd, loc=mod, scale=sd).rvs(size=1)[0]))
    blue_mod = df['blue'].mode()[0]
    random_numbers.append(round(truncnorm((1 - blue_mod) / sd, (15 - blue_mod) / sd, loc=blue_mod, scale=sd).rvs(size=1)[0]))
    return {"predict_res": random_numbers}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
