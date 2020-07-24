from flask import request, make_response, jsonify
import jwt
from app import config
import datetime as dt
from sqlalchemy import desc, func, or_, asc, and_
import re
import os
from PIL import Image, ImageDraw, ImageFont
from webptools import webplib as webp
import random

from models import User, Post_Tag, Post_Tags, Post, Post_Likes, Saved_Posts


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def SaveImage(userId, type):
    if type == 'profile':
        file_name, file_ext = os.path.splitext(request.files['avatarimg'].filename)
        picture_path = config['UPLOAD_FOLDER_PROFILE']+str(userId)+'/avatar.'+file_ext
    elif type == 'cover':
        file_name, file_ext = os.path.splitext(request.files['coverimg'].filename)
        picture_path = config['UPLOAD_FOLDER_PROFILE']+str(userId)+'/cover.'+file_ext

    if type == 'profile':
        i = Image.open(request.files['avatarimg'])
        output_size = (500, 500)
        i.thumbnail(output_size)
    elif type == 'cover':
        i = Image.open(request.files['coverimg'])

    i.save(picture_path)

    if type == 'profile':
        webp.cwebp(config['UPLOAD_FOLDER_PROFILE']+str(userId)+'/avatar.'+file_ext,
                   config['UPLOAD_FOLDER_PROFILE']+str(userId)+'/avatar.webp', "-q 80")
        return str(userId)+'/avatar.png'
    elif type == 'cover':
        webp.cwebp(config['UPLOAD_FOLDER_PROFILE']+str(userId)+'/cover.'+file_ext,
                   config['UPLOAD_FOLDER_PROFILE']+str(userId)+'/cover.webp', "-q 80")
        return str(userId)+'/cover.webp';

def GetItemForKeyN(value):
    return value['id']

def dict_from_class(cls):
    return dict(
        (key, value if type(value) is not dt.datetime else str(value))
        for (key, value) in cls.__dict__.items()
        if key[:1] != '_'
    )

def generateUserToken(user, userIP):
    token = jwt.encode(
        {
            'id': user.id,
            'perm_lvl': user.role.id,
            'permissions': dict_from_class(user.role.permissions),
            'name': user.name,
            'realname': user.info.getFullName(),
            'avatar': user.info.avatar_img,
            'ip': userIP,
            'epx': str(dt.datetime.now() + dt.timedelta(minutes=60))
        }, config['JWT_KEY'])

    return token

def CreateAvatar(user):
    image_w = 500
    image_h = 500

    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    img = Image.new('RGB', (image_w, image_h), color=color)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(config.get('ROOT_PATH')+'/static/fonts/Roboto-Bold.ttf', size=300)

    user_letters = user['first_name'][0]+user['last_name'][0]

    text_w, text_h = draw.textsize(user_letters, font=font)

    draw.text(
        (
            (image_w - text_w)/2,
            (image_h - text_h - 80)/2,
        ),
        user_letters, 
        font=font, 
        fill=(int(color[0] - (color[0]/10)), int(color[1] - (color[1]/10)), int(color[2]  - (color[2]/10))),
    )

    image_path = user['id']+'/avatar.png'

    img.save(config['UPLOAD_FOLDER_PROFILE']+image_path)

    webp.cwebp(config['UPLOAD_FOLDER_PROFILE']+image_path, config['UPLOAD_FOLDER_PROFILE']+user['id']+'/avatar.webp', "-q 90")

    return image_path
