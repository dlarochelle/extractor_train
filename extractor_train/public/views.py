# -*- coding: utf-8 -*-
'''Public section, including homepage and signup.'''
from flask import (Blueprint, request, render_template, flash, url_for,
                    redirect, session)

import flask

from flask.ext.login import login_user, login_required, logout_user

from extractor_train.extensions import login_manager
from extractor_train.user.models import User
from extractor_train.dlannotations.models import Dlannotations
from extractor_train.public.forms import LoginForm
from extractor_train.user.forms import RegisterForm
from extractor_train.utils import flash_errors
from extractor_train.database import db

import ipdb

msm_downloads_file = 'new_msm_download_ids.txt'


downloads_id_list = []

def get_downloads_id_list():

    #if len( downloads_id_list ) > 0 :
    #    return downloads_id_list

    with open( 'new_msm_download_ids.txt' , 'rb' ) as f:
        content = f.readlines()

    content.pop()
    
    #ipdb.set_trace()

    downloads_id_list = [ int(downloads_id) for downloads_id in content if len(downloads_id) > 0 and downloads_id != ''];

    print len ( downloads_id_list );

    return downloads_id_list

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

    valid_emails = [ 'ben.doernberg@gmail.com', 'dlarochelle@cyber.law.harvard.edu', 'bdoernberg@cyber.law.harvard.edu']

    if form.email.data not in valid_emails:
        return 'not an approved email';

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

def get_download_raw_content( downloads_id ):
    download =  get_download( downloads_id )

    raw_content = download['raw_content'] 

    return raw_content

@blueprint.route("/download_text/<int:downloads_id>")
def download_text( downloads_id ):
    print 'downloads_id', downloads_id

    raw_content = get_download_raw_content( downloads_id )

    print raw_content[:200]

    response = flask.make_response( raw_content );

    return response


@blueprint.route("/download_text_fake/<int:downloads_id>")
def download_text_fake( downloads_id ):
    raw_content = '''
<html>
<head>
</head>
<body>
<p>
Article Paragraph 1
</p>
<p>
Article Paragraph 2
</p>
<p>
Article Paragraph 3
</p>
</html>
'''

    response = flask.make_response( raw_content );

    return response

from lxml import etree
import xml.etree.ElementTree as ET

def get_annotated_content( downloads_id ):
    download = get_download( downloads_id )
    download_text = download[ 'raw_content' ]
    qr = Dlannotations.query.filter( Dlannotations.downloads_id == downloads_id )
    dl = qr.first()
    annotations = dl.annotations

    htmlparser = etree.HTMLParser()

    root = etree.fromstring( download_text, htmlparser )

    #ipdb.set_trace()
    for annotation in annotations:
        ipdb.set_trace()
        start = root.xpath( annotation['start_xpath'] )[0]
        end   = root.xpath( annotation['end_xpath'] )[0]

        
    
@blueprint.route("/extractor_train/<int:downloads_id>")
def extractor_train( downloads_id ):
    print 'downloads_id', downloads_id

    form = LoginForm(request.form)

    downloads_id_list = get_downloads_id_list()

    #ipdb.set_trace()

    annotator_name = request.args.get('annotator_name',None )

    num_downloads_annotated = Dlannotations.query.count()

    dl_index = downloads_id_list.index( downloads_id )

    downloads_id_next = downloads_id_list[ dl_index + 1 ]

    return render_template("public/extractor_train.html", form=form, downloads_id=downloads_id, downloads_id_next=downloads_id_next, num_downloads_annotated=num_downloads_annotated, annotator_name=annotator_name )
    return download['raw_content']
    return ''


@blueprint.route("/save/", methods=["GET", "POST"])
def save( ):

    print 'in save'

    data = request.json

    downloads_id = data[ 'downloads_id']
    selections = data['selections']

    annotator_name = data[ 'annotator_name' ]

    #ipdb.set_trace()
    raw_content = get_download_raw_content( downloads_id )

    qr = Dlannotations.query.filter( Dlannotations.downloads_id == downloads_id )
    dl = qr.first()
    if dl == None :
        dl = Dlannotations.create( downloads_id=downloads_id, raw_content=raw_content, annotator_name=annotator_name, annotations_json=json.dumps( selections) )

    else:
        dl.update( downloads_id=downloads_id, raw_content=raw_content, annotator_name=annotator_name, annotations_json=json.dumps( selections) )

    
    #annotated_content = get_annotated_content( downloads_id )


    print "success";
    response = flask.make_response( json.dumps( { 'message': 'success' } ) );

    #form = LoginForm(request.form)
    #return render_template("public/about.html", form=form)
    
    return response


import cPickle
import os.path

api_key = cPickle.load( file( os.path.expanduser( '~/mediacloud_api_key.pickle' ), 'r' ) )

loc_key = 'f66a50230d54afaf18822808aed649f1d6ca72b08fb06d5efb6247afe9fbae52'

import requests, csv, sys, os, json, cPickle

def get_download( downloads_id ):
    download = requests.get('https://api.mediacloud.org/api/v2/downloads/single/'+str(downloads_id)+'?key='+api_key)

    download.raise_for_status()

    return download.json()[0]

