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
political_blogs_file = 'new_political_blogs_5727_download_ids.txt'

download_id_files = [ 'egypt_composite_dalia_20140425_media_tag_8878255_download_ids.txt',
                      #'new_msm_download_ids.txt', 
                      'new_political_blogs_5727_download_ids.txt',
                      'russian_media_tag_7796878_download_ids.txt',
                      'pew_knight_study_media_tag_2453107_downloads_ids.txt',
                      'ap_english_us_top25_20100110_media_tag_8875027_downloads_ids.txt',
                      'spidered_story_tag_8875452_downloads_ids.txt'
                      ]

#ownloads_id_file = political_blogs_file

#downloads_id_list = []

def get_downloads_id_list():

    #if len( downloads_id_list ) > 0 :
    #    return downloads_id_list

    downloads_id_list = []

    for downloads_id_file in download_id_files:
        #print 'downloads_id_file', downloads_id_file

        with open( downloads_id_file , 'rb' ) as f:
            content = f.readlines()

        content.pop()

        #ipdb.set_trace()

        downloads_id_list.extend( [ int(downloads_id) for downloads_id in content if len(downloads_id) > 0 and downloads_id != ''] )

        #print len ( downloads_id_list );

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

        
def get_next_unannotated_downloads_id( downloads_id ):
    downloads_id_list = get_downloads_id_list()
    dl_index =  downloads_id_list.index( downloads_id )

    for next_downloads_id in downloads_id_list[ dl_index + 1: ]:
         qr = Dlannotations.query.filter( Dlannotations.downloads_id == next_downloads_id )
         dl = qr.first()
         if dl == None :
             return next_downloads_id
        
    
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

    next_unannotated_downloads_id = get_next_unannotated_downloads_id( downloads_id )

    return render_template("public/extractor_train.html", form=form, downloads_id=downloads_id, downloads_id_next=downloads_id_next, next_unannotated_downloads_id=next_unannotated_downloads_id, num_downloads_annotated=num_downloads_annotated, annotator_name=annotator_name )
    return download['raw_content']
    return ''


@blueprint.route("/save/", methods=["GET", "POST"])
def save( ):

    print 'in save'

    data = request.json

    downloads_id = data[ 'downloads_id']
    selections = data['selections']

    annotator_name = data[ 'annotator_name' ]
    selected_texts = data[ 'selected_texts' ]
    #ipdb.set_trace()
    raw_content = get_download_raw_content( downloads_id )

    qr = Dlannotations.query.filter( Dlannotations.downloads_id == downloads_id )
    dl = qr.first()
    if dl == None :
        dl = Dlannotations.create( downloads_id=downloads_id, raw_content=raw_content, annotator_name=annotator_name, selected_texts_json=json.dumps(selected_texts), annotations_json=json.dumps( selections) )

    else:
        dl.update( downloads_id=downloads_id, raw_content=raw_content, annotator_name=annotator_name, selected_texts_json=json.dumps(selected_texts), annotations_json=json.dumps( selections) )

    
    #annotated_content = get_annotated_content( downloads_id )


    print "success";
    response = flask.make_response( json.dumps( { 'message': 'success' } ) );

    #form = LoginForm(request.form)
    #return render_template("public/about.html", form=form)
    
    return response

@blueprint.route("/previous_annotations/", methods=["POST"])
def previous_annotations( ):

    print 'previous_annotations'
    #ipdb.set_trace()

    data = request.json

    downloads_id = data[ 'downloads_id']
    
    #selections = data['selections']

    #annotator_name = data[ 'annotator_name' ]

    #ipdb.set_trace()
    #raw_content = get_download_raw_content( downloads_id )

    qr = Dlannotations.query.filter( Dlannotations.downloads_id == downloads_id )
    dl = qr.first()

    if dl == None :
        ret = { 'previously_annotated': False }
    else:
        #ipdb.set_trace()
        ret = { 'previously_annotated': True,
                'downloads_id': dl.downloads_id,
                'annotator_name': dl.annotator_name,
                'annotations': dl.annotations
                }
    
    #annotated_content = get_annotated_content( downloads_id )

    response = flask.make_response( json.dumps( ret ) );

    #form = LoginForm(request.form)
    #return render_template("public/about.html", form=form)

    print 'ret', ret

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

