# -*- coding: utf-8 -*-
from flask.ext.assets import Bundle, Environment

css = Bundle(
    "libs/bootstrap/dist/css/bootstrap.css",
    "css/style.css",
#    "libs/annotator.1.2.9/annotator.min.css",
    filters="cssmin",
    output="public/css/common.css"
)

js = Bundle(
    "libs/jQuery/dist/jquery.js",
    "libs/bootstrap/dist/js/bootstrap.js",
    "js/plugins.js",
    # "libs/annotator.1.2.9/annotator.min.js",
    # "libs/rangy/external/log4javascript_stub.js",
    # "libs/rangy/src/core/core.js",
    # "libs/rangy/src/core/dom.js",
    # "libs/rangy/src/core//domrange.js",
    # "libs/rangy/src/core/wrappedrange.js",
    # "libs/rangy/src/core/wrappedselection.js",
    # "libs/rangy/src/modules/rangy-classapplier.js",
    # "libs/rangy/src/modules/rangy-highlighter.js",
    filters='jsmin',
    output="public/js/common.js"
)

assets = Environment()

assets.register("js_all", js)
assets.register("css_all", css)
