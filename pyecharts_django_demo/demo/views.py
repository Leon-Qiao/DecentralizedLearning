from hashlib import new
import json
from random import randrange

from django.http import HttpResponse
from rest_framework.views import APIView

from pyecharts.charts import Line
from pyecharts import options as opts

import requests

# Create your views here.
def response_as_json(data):
    json_str = json.dumps(data)
    response = HttpResponse(
        json_str,
        content_type="application/json",
    )
    response["Access-Control-Allow-Origin"] = "*"
    return response


def json_response(data, code=200):
    data = {
        "code": code,
        "msg": "success",
        "data": data,
    }
    return response_as_json(data)


def json_error(error_string="error", code=500, **kwargs):
    data = {
        "code": code,
        "msg": error_string,
        "data": {}
    }
    data.update(kwargs)
    return response_as_json(data)


JsonResponse = json_response
JsonError = json_error

old_data = []

def line_base(FigType) -> Line:
    line = (
        Line()
        .add_xaxis(list(range(len(old_data))))
        .add_yaxis(series_name="", y_axis=[x[FigType] for x in old_data], label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(
            title_opts=opts.TitleOpts(title=FigType),
            xaxis_opts=opts.AxisOpts(type_="value"),
            yaxis_opts=opts.AxisOpts(type_="value", is_scale=True)
        )
        .dump_options_with_quotes()
    )
    return line


class ChartView(APIView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(json.loads(line_base(kwargs['FigType'])))


cnt = len(old_data)


class ChartUpdateView(APIView):
    def get(self, request, *args, **kwargs):
        global cnt, old_data
        row_data = json.loads(requests.get(url = "http://127.0.0.1:8002/getLoss/A/" + str(cnt)).text)
        # row_data = [{"MSE": randrange(0, 100), "RMSE": randrange(0, 100), "MAE": randrange(0, 100), "R2": randrange(0, 100)} for _ in range(randrange(0, 3))]
        old_data = old_data + row_data
        new_data = []
        for i in range(len(row_data)):
            cnt = cnt + 1
            new_data.append({"name": cnt, "value": row_data[i]})
        return JsonResponse(new_data)

class IndexView(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open("./templates/index.html").read())
