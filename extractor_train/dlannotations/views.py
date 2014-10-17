# -*- coding: utf-8 -*-
from flask import Blueprint, render_template
from flask.ext.login import login_required

blueprint = Blueprint("dlannotation", __name__, url_prefix='/dlannotations',
                        static_folder="../static")


@blueprint.route("/")
@login_required
def members():
    return render_template("dlannotations/members.html")
