# -*- coding: utf-8 -*-
from datetime import datetime

from jinja2 import Environment, FileSystemLoader
from twisted.web.http import RESPONSES

from helper.database import DatabaseHelper
from helper.permission import is_anybody
from localization import SITE_NAME
from model.board import Board


jinja2_env = Environment(loader=FileSystemLoader("template", encoding="utf-8"),
                         extensions=['jinja2.ext.with_'])
jinja2_env.globals = {
    "site_name": SITE_NAME,
    "datetime": datetime,
    "getattr": getattr,
}


def get_template(name, parent=None, glob=None):
    return jinja2_env.get_template(name, parent, glob)


def render_template(name, request, context=None):
    if context == None:
        context = dict()
    board_query = request.dbsession.query(Board).filter(Board.enabled).order_by(Board.repr_order.asc())
    board_meta = {
        "somoim": [(board.name, board.repr) for board in board_query.filter(Board.classification == "somoim")],
        "normal": [(board.name, board.repr) for board in board_query.filter(Board.classification == "normal")],
    }
    context["board_meta"] = board_meta
    context["request"] = request
    context["is_anybody"] = is_anybody(request)
    return get_template(name).render(context)


def render_template_from_text(text, context=None):
    if not context:
        context = dict()
    template = jinja2_env.from_string(text)
    return template.render(context).encode("utf-8")


def generate_error_message(request, code, detail):
    brief = RESPONSES[code]
    context = {
        "brief": brief,
        "detail": detail,
        "title": str(code) + " " + str(brief),
    }
    return render_template("error.html", request, context)
