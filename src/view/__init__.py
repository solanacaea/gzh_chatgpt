from sanic import Blueprint
from .gzh_view import bp_gzh
from .test_view import bp_test

view = Blueprint.group(bp_gzh, bp_test)
