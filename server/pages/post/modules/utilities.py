from flask import request
from app import config
import datetime as dt
import os
from PIL import Image
from webptools import webplib as webp
import re
from models import User, User_Tags, Post_Tag, Post_Tags, Post, Post_Likes, Saved_Posts

def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def SaveImage(post_id):
    # if(form_img.data):
    file_name, file_ext = os.path.splitext(request.files['image'].filename)
    picture_fn = 'post_' + str(post_id) + file_ext
    picture_path = os.path.join(config['UPLOAD_FOLDER_POST'], picture_fn)

    i = Image.open(request.files['image'])
    i.save(picture_path)
    webp.cwebp(os.path.join(config['UPLOAD_FOLDER_POST'], picture_fn),
               os.path.join(config['UPLOAD_FOLDER_POST'], 'post_' + str(post_id) + '.webp'), "-q 80")
    os.remove(os.path.join(config['UPLOAD_FOLDER_POST'], picture_fn))

    picture_fn = 'post_' + str(post_id) + '.webp'

    return picture_fn
