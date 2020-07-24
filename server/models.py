import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import sqlalchemy.dialects.postgresql as sq

from sqlalchemy import Column, Integer, Sequence, String, Date, Float, DateTime, Boolean, Text

from app import db, bcrypt, wa, app

from flask import url_for, json
import pytz

from model_types import ChoiceType

class BaseModel():
    created_on = Column(DateTime, default=datetime.datetime.now)
    modified_on = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def add(self):
        db.session.add(self)
        db.session.commit()

    def save(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get(cls):
        return db.session.query(cls)

    @classmethod
    def find(cls, query):
        return cls.query.search(query)

    def time_ago(self):
        now = datetime.datetime.now()
        now = pytz.utc.localize(now)
        now_aware = pytz.utc.localize(self.created_on)
        if (now - now_aware).days / 30 > 1:
            return str(int((now - now_aware).days / 30)) + ' months ago'
        elif int((now - now_aware).days) > 0:
            return str((now - now_aware).days) + ' days ago'
        elif int((now - now_aware).seconds / 3600) > 0:
            return str(int((now - now_aware).seconds / 3600)) + ' hours ago'
        elif (now - now_aware).seconds / 60 > 0:
            return str(int((now - now_aware).seconds / 60)) + ' minutes ago'


class User(BaseModel, db.Model):

    __tablename__ = "users"

    id = Column(Integer, primary_key = True, autoincrement=True)
    name = Column(String(20))
    email = Column(String(50))
    password = Column(String)
    confirmed = Column(Boolean)
    status_id = Column(Integer, ForeignKey("status_types.id"), default = 0)
    role_id = Column(Integer, ForeignKey("user_role.id"), default = 0)
    info = relationship("User_Info", uselist=False, cascade="all, delete", passive_deletes = True)
    ip = Column(ForeignKey("ip_location.id"))
    language_id = Column(Integer, ForeignKey("languages.id"))
    pers = relationship("User_Pers", uselist=False, cascade="all, delete", passive_deletes = True)
    social = relationship("User_Social", uselist=True, cascade="all, delete", passive_deletes = True)
    saved_posts = relationship("Saved_Posts", uselist=True, cascade="all, delete", passive_deletes = True)
    tags = relationship("User_Tags", uselist=True, cascade="all, delete", passive_deletes = True)
    likes = relationship("Post_Likes", uselist=True, cascade="all, delete", passive_deletes = True)
    posts = relationship("Post", backref='author', uselist=True, cascade="all, delete", passive_deletes = True)
    comments = relationship("Post_Comments", backref='author', uselist=True, cascade="all, delete", passive_deletes = True)
    replies = relationship("Comment_Reply", backref='author', uselist=True, cascade="all, delete", passive_deletes = True)
    notifications = relationship("Notification", foreign_keys='Notification.user', uselist=True, cascade="all, delete", passive_deletes = True)
    following = relationship("User_Followed", foreign_keys='User_Followed.user', uselist=True, cascade="all, delete", passive_deletes = True)
    followed = relationship("User_Following", foreign_keys='User_Following.user', uselist=True, cascade="all, delete", passive_deletes = True)

    def __init__ (self, id=None, name="", email="", password="", confirmed=False, status_id=1, role_id=2, language_id=1, pers=None, info=None, location=None, language=None, ip=None):
        self.id = id
        self.name = str(name).lower()
        self.email = email
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        self.confirmed = confirmed
        self.status_id = status_id
        self.role_id = role_id
        self.language_id = language_id
        self.pers = pers
        self.info = info
        self.location = location
        self.language = language
        self.ip = ip


class User_Info(BaseModel, db.Model):
    
    __tablename__ = "user_info"

    user = Column(Integer, ForeignKey("users.id", ondelete = 'CASCADE'), primary_key = True)
    first_name = Column(String(20))
    last_name = Column(String(20))
    avatar_img = Column(String(20), default = None)
    cover_img = Column(String(20), default = None)

    def __init__ (self, user=None, first_name="", last_name="", avatar_img=None, cover_img=None):
        self.user = user
        self.first_name = first_name
        self.last_name = last_name
        self.avatar_img = avatar_img
        self.cover_img = cover_img


    def getFullName(self):
        return self.first_name+' '+self.last_name

class User_Pers(BaseModel, db.Model):
    
    __tablename__ = "user_pers"

    user = Column(Integer, ForeignKey("users.id", ondelete = 'CASCADE'), primary_key = True)
    profession = Column(String(30), default = None)
    birthday = Column(DateTime, default = None)
    bio = Column(String(100), default = "")

    def __init__ (self, user=None, profession=None, birthday=None, bio=""):
        self.user = user
        self.profession = profession
        self.birthday = birthday
        self.bio = bio

class User_Role(BaseModel, db.Model):

    __tablename__ = "user_role"

    id = Column(Integer, primary_key = True, autoincrement=True)
    name = Column(String(15), default = "")
    badge = Column(String(30), default = "")
    permissions = relationship("Role_Permissions", cascade="all, delete", passive_deletes = True, uselist=False)

    user = relationship("User", backref="role")

    def __init__ (self, id=None, name="", badge=""):
        self.id = id
        self.name = name
        self.badge = badge


class User_Settings(BaseModel, db.Model):

    __tablename__ = "user_settings"

    id = Column(Integer, primary_key = True, autoincrement=True)
    name = Column(String(20), default = "")
    type = Column(String(20), nullable=False)
    category = Column(String(20), nullable=False)
    key = Column(String(30), nullable=False)

    def __init__(self, id=None, name='', type='', category='', key=''):
        self.id = id
        self.name = name
        self.type = type
        self.category = category
        self.key = key

class Role_Permissions(BaseModel, db.Model):

    __tablename__ = "role_permissions"

    role = Column(Integer, ForeignKey("user_role.id", ondelete = 'CASCADE'), primary_key = True)
    edit_user = Column(Boolean, default = False)
    delete_user = Column(Boolean, default = False)
    add_post = Column(Boolean, default = True)
    edit_post = Column(Boolean, default = False)
    delete_post = Column(Boolean, default = False)
    add_reply = Column(Boolean, default = True)
    edit_reply = Column(Boolean, default = False)
    delete_reply = Column(Boolean, default = False)
    admin = Column(Boolean, default = False)

    def __init__ (self, role=None, edit_user=False, delete_user=False, add_post=True, \
        edit_post=False, delete_post=False, add_reply=True, edit_reply=False, delete_reply=False, \
            admin=False):

        self.role = role
        self.edit_user = edit_user
        self.delete_user = delete_user
        self.add_post = add_post
        self.edit_post = edit_post
        self.delete_post = delete_post
        self.add_reply = add_reply
        self.edit_reply = edit_reply
        self.delete_reply = delete_reply
        self.admin = admin


class User_Social(BaseModel, db.Model):

    __tablename__ = "user_social"

    id = Column(Integer, primary_key = True, autoincrement=True)
    user = Column(Integer, ForeignKey("users.id", ondelete = 'CASCADE'))
    type = Column(Integer, ForeignKey("social_types.id",  ondelete = 'CASCADE'))
    link = Column(String(50), default = "")

    social = relationship("Social_Types", cascade="all, delete", uselist=False)

    def __init__ (self, user=None, type=0, link=""):
        self.user = user
        self.type = type
        self.link = link


class Social_Types(BaseModel, db.Model):

    __tablename__ = "social_types"

    id = Column(Integer, primary_key = True, autoincrement=True)
    name = Column(String(15), default = "")
    icon = Column(String(20), default = "")
    pre_link = Column(String(30), default = "")

    def __init__ (self, id=None, name="", icon="", pre_link=""):
        self.id = id
        self.name = name
        self.icon = icon
        self.pre_link = pre_link

class Status_Types(BaseModel, db.Model):

    __tablename__ = "status_types"

    id = Column(Integer, primary_key = True, autoincrement=True)
    name = Column(String(10), default = "")
    color = Column(String(10), default = "")

    user = relationship("User", backref="status")

    def __init__ (self, id=None, name="", color=""):
        self.id = id
        self.name = name
        self.color = color

class Saved_Posts(BaseModel, db.Model):

    __tablename__ = "saved_posts"

    id = Column(Integer, primary_key = True, autoincrement=True)
    user = Column(Integer, ForeignKey("users.id", ondelete = 'CASCADE'))
    post = Column(Integer, ForeignKey("post.id", ondelete = 'CASCADE'))

    def __init__ (self, id=None, user=None, post=None):
        self.id = id
        self.user = user
        self.post = post


class User_Tags(BaseModel, db.Model):

    __tablename__ = "user_tags"

    id = Column(Integer, primary_key = True, autoincrement=True)
    user = Column(Integer, ForeignKey("users.id", ondelete = 'CASCADE'))
    tag_id = Column(Integer, ForeignKey("post_tag.id", ondelete = 'CASCADE'))

    def __init__ (self, id=None, user=None, tag_id=None):
        self.id = id
        self.user = user
        self.tag_id = tag_id


class User_Following(BaseModel, db.Model):

    __tablename__ = "user_following"

    id = Column(Integer, primary_key = True, autoincrement=True)
    user = Column(Integer, ForeignKey("users.id"))
    followed = Column(Integer, ForeignKey("users.id"))

    user_rel = relationship("User", foreign_keys=[followed], uselist=False)

    def __init__ (self, id=None, user=None, followed=None):
        self.id = id
        self.user = user
        self.followed = followed


class User_Followed(BaseModel, db.Model):

    __tablename__ = "user_followed"

    id = Column(Integer, primary_key = True, autoincrement=True)
    user = Column(Integer, ForeignKey("users.id", ondelete = 'CASCADE'))
    following = Column(Integer, ForeignKey("users.id", ondelete = 'CASCADE'))

    def __init__ (self, id=None, user=None, following=None):
        self.id = id
        self.user = user
        self.following = following

class Post(BaseModel, db.Model):

    __tablename__ = "post"
    __searchable__ = ["title"]

    id = Column(Integer, primary_key = True, autoincrement=True)
    author_id = Column(Integer, ForeignKey("users.id", ondelete = 'CASCADE'))
    title = Column(String(50))
    approved = Column(Boolean, default = False)
    language_id = Column(Integer, ForeignKey("languages.id", ondelete = 'SET NULL'))
    read_time = Column(String(20))
    info = relationship("Post_Info", cascade="all, delete", passive_deletes = True, uselist=False)
    link = Column(String(100))

    def __init__ (self, id=None, author_id=None, title="", approved=False, language_id=1, read_time="", info=None, link=''):
        self.id = id
        self.author_id = author_id
        self.title = title
        self.approved = approved
        self.language_id = language_id
        self.read_time = read_time
        self.info = info
        self.link = link


class Post_Info(BaseModel, db.Model):

    __tablename__ = "post_info"

    post = Column(Integer, ForeignKey("post.id", ondelete = 'CASCADE'), primary_key = True)
    text = Column(String)
    closed_on = Column(DateTime, default = None)
    closed = Column(Boolean, default = False)
    closed_by = Column(Integer, ForeignKey("users.id"))
    likes = relationship("Post_Likes", cascade="all, delete", passive_deletes = True)
    comments = relationship("Post_Comments",cascade="all, delete",  passive_deletes = True)
    thumbnail = Column(String(20), default = None)
    tags = relationship("Post_Tags", cascade="all, delete", passive_deletes = True)

    def __init__ (self, post=None, text="", closed_on=None, closed=False, closed_by=None, thumbnail="", tags=None):
        self.post = post
        self.text = text
        self.closed_on = closed_on
        self.closed = closed
        self.closed_by = closed_by
        self.thumbnail = thumbnail
        self.tags = tags

class Post_Tags(BaseModel, db.Model):

    __tablename__ = "post_tags"

    id = Column(Integer, primary_key = True, autoincrement=True)
    post = Column(Integer, ForeignKey("post_info.post", ondelete = 'CASCADE'))
    tag_id = Column(Integer, ForeignKey("post_tag.id", ondelete = 'CASCADE'))

    def __init__ (self, id=None, post=None, tag_id=None):
        self.id = id
        self.post = post
        self.tag_id = tag_id

class Post_Tag(BaseModel, db.Model):

    __tablename__ = "post_tag"

    id = Column(Integer, primary_key = True, autoincrement=True)
    name = Column(String(20))
    color = Column(String(20), default = None)
    icon = Column(String(20), default = None)
    count = Column(Integer, default = 0)

    post = relationship("Post_Tags", cascade="all, delete", backref='tag', uselist=False)
    user = relationship("User_Tags", cascade="all, delete", backref='tag', uselist=False)

    def __init__ (self, id=None, name="", color="", icon="", count=0):
        self.id = id
        self.name = name
        self.color = color
        self.icon = icon
        self.count = count


class Post_Likes(BaseModel, db.Model):

    __tablename__ = "post_likes"

    id = Column(Integer, primary_key = True, autoincrement=True)
    post = Column(Integer, ForeignKey("post_info.post", ondelete = 'CASCADE'))
    like = Column(Integer, ForeignKey("like_type.id", ondelete = 'CASCADE'))
    author = Column(Integer, ForeignKey("users.id", ondelete = 'CASCADE'))

    def __init__ (self, id=None, post=None, like=None, author=None):
        self.id = id
        self.post = post
        self.like = like
        self.author = author

class Comment_Likes(BaseModel, db.Model):

    __tablename__ = "comment_likes"

    id = Column(Integer, primary_key = True, autoincrement=True)
    comment = Column(Integer, ForeignKey("post_comments.id", ondelete = 'CASCADE'))
    like = Column(Integer, ForeignKey("like_type.id", ondelete = 'CASCADE'))
    author = Column(Integer, ForeignKey("users.id", ondelete = 'CASCADE'))

    def __init__ (self, id=None, post=None, like=None, author=None):
        self.id = id
        self.comment = comment
        self.like = like
        self.author = author

class Reply_Likes(BaseModel, db.Model):

    __tablename__ = "reply_likes"

    id = Column(Integer, primary_key = True, autoincrement=True)
    reply = Column(Integer, ForeignKey("comment_reply.id", ondelete = 'CASCADE'))
    like = Column(Integer, ForeignKey("like_type.id", ondelete = 'CASCADE'))
    author = Column(Integer, ForeignKey("users.id", ondelete = 'CASCADE'))

    def __init__ (self, id=None, post=None, like=None, author=None):
        self.id = id
        self.reply = reply
        self.like = like
        self.author = author

class Like_Type(BaseModel, db.Model):

    __tablename__ = "like_type"

    id = Column(Integer, primary_key = True, autoincrement=True)
    name = Column(String(10), default = "")
    color = Column(String(15), default = "")
    icon = Column(String(20), default = "")

    def __init__ (self, id=None, name="", color="", icon=""):
        self.id = id
        self.name = name
        self.color = color
        self.icon = icon


class Post_Comments(BaseModel, db.Model):

    __tablename__ = "post_comments"

    id = Column(Integer, primary_key = True, autoincrement=True)
    post = Column(Integer, ForeignKey("post_info.post", ondelete = 'CASCADE'))
    author_id = Column(Integer, ForeignKey("users.id", ondelete = 'CASCADE'))
    text = Column(String, default = "")
    replies = relationship("Comment_Reply", cascade="all, delete", passive_deletes = True)

    def __init__ (self, id=None, post=None, author_id=None, text=''):
        self.id = id
        self.post = post
        self.author_id = author_id
        self.text = text


class Comment_Reply(BaseModel, db.Model):

    __tablename__ = "comment_reply"

    id = Column(Integer, primary_key = True, autoincrement=True)
    comment = Column(Integer, ForeignKey("post_comments.id", ondelete = 'CASCADE'))
    author_id = Column(Integer, ForeignKey("users.id", ondelete = 'CASCADE'))
    text = Column(String, default = "")

    def __init__ (self, id=None, comment=None, author_id=None, text=''):
        self.id = id
        self.comment = comment
        self.author_id = author_id
        self.text = text

    
class Notification(BaseModel, db.Model):

    __tablename__ = "notification"

    id = Column(Integer, primary_key = True, autoincrement=True)
    author = Column(Integer, ForeignKey("users.id", ondelete = 'CASCADE'))
    user = Column(Integer, ForeignKey("users.id", ondelete = 'CASCADE'))
    type = Column(Integer, ForeignKey("notification_type.id", ondelete = 'CASCADE'))
    checked = Column(Boolean, default = False)
    title = Column(String(40), default = "")
    body = Column(String(40), default = "")
    link = Column(String(50), default = "")

    def __init__ (self, id=None, author=None, user=None, type=0, checked=False, title="", body="", link=""):
        self.id = id
        self.author = author
        self.user = user
        self.type = type
        self.checked = checked
        self.title = title
        self.body = body
        self.link = link

class Notification_Type(BaseModel, db.Model):

    __tablename__ = "notification_type"

    id = Column(Integer, primary_key = True, autoincrement=True)
    name = Column(String(20), default = "")

    def __init__ (self, id=None, name=""):
        self.id = id
        self.name = name

class Notification_Subscriber(BaseModel, db.Model):

    __tablename__ = "notification_subscriber"

    id = Column(Integer, primary_key = True, autoincrement=True)
    user = Column(Integer, ForeignKey("users.id", ondelete = 'CASCADE'))
    info = Column(String)
    is_active = Column(Boolean, default = True)

    def __init__ (self, id=None, user=None, info="", is_active=True):
        self.id = id
        self.user = user
        self.info = info
        self.is_active = is_active


class Ip_Location(BaseModel, db.Model):

    __tablename__ = "ip_location"

    id = Column(Integer, primary_key = True, autoincrement=True)
    ip = Column(String(15))
    location = relationship("Location", passive_deletes=True, uselist=False)

    user = relationship("User", backref='location', uselist=False)

    def __init__(self, id=None, ip=None, location=None):
        self.id = id
        self.ip = ip
        self.location = location

class Location(BaseModel, db.Model):

    __tablename__ = "location"

    id = Column(Integer, primary_key = True, autoincrement=True)
    longitude = Column(String(50))
    latitude = Column(String(50))
    country = Column(String(20))
    city = Column(String(20))
    flag = Column(String(10))
    ip = Column(Integer, ForeignKey('ip_location.id', ondelete = 'CASCADE'))
    iso = Column(String(10))

    def __init__ (self, id=None, longitude=None, latitude=None, country=None, city=None, ip=None, iso='', flag=''):
        self.id = id
        self.longitude = longitude
        self.latitude = latitude
        self.country = country
        self.city = city
        self.ip = ip
        self.iso = iso
        self.flag = flag

class Languages(BaseModel, db.Model):

    __tablename__ = "languages"

    id = Column(Integer, primary_key = True, autoincrement=True)
    name = Column(String(20))
    code = Column(String(5))

    user = relationship("User", backref="language")
    post = relationship("Post", backref="language")

    def __init__ (self, id=None,name="", code=""):
        self.id = id
        self.name = name
        self.code = code

class Conversations(BaseModel, db.Model):

    __tablename__ = 'conversations'

    id = Column(Integer, primary_key = True, autoincrement=True)
    members = db.Column(sq.ARRAY(db.Integer), default=[], primary_key = False)
    seen = db.Column(db.Boolean, primary_key=False)

    def __init__(self, id=None, members=[], seen=False):
        self.id = id
        self.members = members
        self.seen = seen

class Conversation(BaseModel, db.Model):

    __tablename__ = 'conversation'

    id = Column(Integer, db.Sequence('conversations_id_seq'), primary_key=True)
    message = Column(Text, primary_key=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    author = relationship("User", foreign_keys=[user_id])
    conversation = relationship("Conversations", backref="chat", foreign_keys=[conversation_id], order_by=id.desc())

    def __init__(self, id=None, message='', user_id=None, conversation_id=None):
        self.id = id
        self.message = message
        self.user_id = user_id
        self.conversation_id = conversation_id

    def date_sent(self):
        return self.created_on.strftime("%A %d %b")

    def when_sent(self):
        return self.created_on.strftime("%H:%M")

class View(BaseModel, db.Model):

    __tablename__ = 'view'

    id = Column(Integer, db.Sequence('conversations_id_seq'), primary_key=True)
    type = Column(String(10))
    route = Column(String(50))
    post_id = Column(Integer, ForeignKey('post.id'), default=None)
    ip_id = Column(Integer, ForeignKey('ip_location.id', ondelete = 'CASCADE'))
    ip = relationship('Ip_Location', foreign_keys=[ip_id])

    def __init__(self, id=None, type='page', route='', ip_id=None, ip=None, post_id=None):
        self.id = id
        self.type = type
        self.route = route
        self.post_id = post_id
        self.ip_id = ip_id
        self.ip = ip



wa.search_index(app,Post)