# -*- coding: utf-8 -*-
'''Public section, including homepage and signup.'''
from flask import (Blueprint, request, render_template, flash, url_for,
                    redirect, session)

import flask

from flask.ext.login import login_user, login_required, logout_user

from extractor_train.extensions import login_manager
from extractor_train.user.models import User
from extractor_train.public.forms import LoginForm
from extractor_train.user.forms import RegisterForm
from extractor_train.utils import flash_errors
from extractor_train.database import db

blueprint = Blueprint('public', __name__, static_folder="../static")

@login_manager.user_loader
def load_user(id):
    return User.get_by_id(int(id))


@blueprint.route("/", methods=["GET", "POST"])
def home():
    form = LoginForm(request.form)
    # Handle logging in
    if request.method == 'POST':
        if form.validate_on_submit():
            login_user(form.user)
            flash("You are logged in.", 'success')
            redirect_url = request.args.get("next") or url_for("user.members")
            return redirect(redirect_url)
        else:
            flash_errors(form)
    return render_template("public/home.html", form=form)

@blueprint.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('You are logged out.', 'info')
    return redirect(url_for('public.home'))

@blueprint.route("/register/", methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form, csrf_enabled=False)
    if form.validate_on_submit():
        new_user = User.create(username=form.username.data,
                        email=form.email.data,
                        password=form.password.data,
                        active=True)
        flash("Thank you for registering. You can now log in.", 'success')
        return redirect(url_for('public.home'))
    else:
        flash_errors(form)
    return render_template('public/register.html', form=form)

@blueprint.route("/about/")
def about():
    form = LoginForm(request.form)
    return render_template("public/about.html", form=form)

@blueprint.route("/download_text/<int:downloads_id>")
def download_text( downloads_id ):
    print 'downloads_id', downloads_id
    download =  get_download( downloads_id )

    raw_content = download['raw_content']

    print raw_content[:200]

    response = flask.make_response( raw_content );

    return response

    print download.keys()
    
    #form = LoginForm(request.form)
    #return render_template("public/about.html", form=form)
    #return download['raw_content']
    return ''

@blueprint.route("/extractor_train/<int:downloads_id>")
def extractor_train( downloads_id ):
    print 'downloads_id', downloads_id

    form = LoginForm(request.form)
    return render_template("public/extractor_train.html", form=form, downloads_id=downloads_id )
    return download['raw_content']
    return ''


import cPickle
import os.path

api_key = cPickle.load( file( os.path.expanduser( '~/mediacloud_api_key.pickle' ), 'r' ) )

loc_key = 'f66a50230d54afaf18822808aed649f1d6ca72b08fb06d5efb6247afe9fbae52'

import mediacloud, requests, csv, sys, os, json, cPickle

def get_download( downloads_id ):
    download = requests.get('https://api.mediacloud.org/api/v2/downloads/single/'+str(downloads_id)+'?key='+api_key)

    download.raise_for_status()

    return download.json()[0]

