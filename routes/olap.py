from __future__ import annotations

from flask import Blueprint, render_template
from models.db import (
    get_olap_row_number,
    get_olap_grouping_sets,
    get_olap_rollup,
    get_olap_filter
)

olap_bp = Blueprint("olap", __name__, url_prefix="/olap")

@olap_bp.route("/")
def index():
    data_row_number = get_olap_row_number()
    data_grouping_sets = get_olap_grouping_sets()
    data_rollup = get_olap_rollup()
    data_filter = get_olap_filter()

    return render_template(
        "olap.html",
        data_row_number=data_row_number,
        data_grouping_sets=data_grouping_sets,
        data_rollup=data_rollup,
        data_filter=data_filter
    )
