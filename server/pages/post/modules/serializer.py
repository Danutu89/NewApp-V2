from marshmallow import fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, ModelSchema
from models import Saved_Posts, Post_Likes, User_Following, User, Post_Info, Post, Post_Tags, Comment_Likes, Reply_Likes
from sqlalchemy import and_
from .utilities import cleanhtml
import re
from app import db

class AuthorLocation(Schema):
    country = fields.Method('getCountry')
    flag = fields.Method('getFlag')

    class Meta:
        fields = (
            'country',
            'flag'
        )

    def getCountry(self, obj):
        return obj.location.country
    
    def getFlag(self, obj):
        return obj.location.flag

class PostTagSchema(Schema):
    class Meta:
        fields = (
            'name',
            'color',
            'icon'
        )

class PostTagsSchema(Schema):
    name = fields.Method('getName')
    color = fields.Method('getColor')
    icon = fields.Method('getIcon')

    class Meta:
        fields = (
            'name',
            'color',
            'icon'
        )

    def getName(self, obj):
        return obj.tag.name

    def getColor(self, obj):
        return obj.tag.color

    def getIcon(self, obj):
        return obj.tag.icon

class PostInfoMinSchema(Schema):
    posted_on = fields.Method('getTimeAgo')
    likes_count = fields.Method('getLikesCount')
    tags = fields.Nested(PostTagsSchema, many=True)
    

    class Meta:
        fields = (
            'thumbnail',
            'posted_on',
            'likes_count',
            'tags',
            
        )

    def getTimeAgo(self, obj):
        return obj.time_ago()

    def getLikesCount(self, obj):
        return len(obj.likes)

class AuthorInfoMinSchema(Schema):
    full_name = fields.Method('getFullName')

    def getFullName(self, obj):
        return obj.first_name + ' ' + obj.last_name

    class Meta:
        fields = (
            'avatar_img',
            'full_name'
        )

class AuthorMinSchema(Schema):
    info = fields.Nested(AuthorInfoMinSchema)
    
    class Meta:
        fields = (
            'name',
            'info'
        )

class PostMinSchema(Schema):
    author = fields.Nested(AuthorMinSchema)
    info = fields.Nested(PostInfoMinSchema)
    saved = fields.Method('ifSaved')
    tags = fields.Nested(PostTagsSchema, many=True)

    class Meta:
        fields = (
            'title',
            'read_time',
            'author',
            'info',
            'link',
            'saved',
            'tags'
        )

    def ifSaved(self, obj):
        currentUser = self.context.get('currentUser')
        if currentUser:
            if Saved_Posts.get().filter(and_(Saved_Posts.user==currentUser.id, Saved_Posts.post==obj.id)).first():
                return True
            else:
                return False
        else:
            return False

class RepliesSchema(Schema):

    author = fields.Nested(AuthorMinSchema)
    mentions = fields.Method('getMentions')
    userInfo = fields.Method('getUserInfo')

    class Meta:
        fields = (
            'author',
            'text',
            'mentions',
            'id',
            'userInfo'
        )

    def getMentions(self, obj):
        m = []
        mentions = re.findall("@([a-zA-Z0-9]{1,15})", cleanhtml(obj.text))

        for mention in mentions:
            check = User.get().filter_by(name=mention).first()
            if check is not None:
                m.append(mention)
        
        return m

    def getUserInfo(self, obj):
        currentUser = self.context.get('currentUser')
        if currentUser:
            return {
                'liked': True if Reply_Likes.get().filter(and_(Reply_Likes.author==currentUser.id, Post_Likes.post==obj.id)).first() is not None else False, 
                'mine': True if obj.author.id == currentUser.id else False,
            }
        else:
            return {
                'liked': False, 
                'mine': False,
            }

class CommentsSchema(Schema):

    author = fields.Nested(AuthorMinSchema)
    replies = fields.Nested(RepliesSchema, many=True)
    mentions = fields.Method('getMentions')
    userInfo = fields.Method('getUserInfo')

    class Meta:
        fields = (
            'author',
            'text',
            'replies',
            'mentions',
            'id',
            'userInfo'
        )

    def getMentions(self, obj):
        m = []
        mentions = re.findall("@([a-zA-Z0-9]{1,15})", cleanhtml(obj.text))

        for mention in mentions:
            check = User.get().filter_by(name=mention).first()
            if check is not None:
                m.append(mention)
        
        return m

    def getUserInfo(self, obj):
        currentUser = self.context.get('currentUser')
        if currentUser:
            return {
                'liked': True if Comment_Likes.get().filter(and_(Comment_Likes.author==currentUser.id, Comment_Likes.comment==obj.id)).first() is not None else False, 
                'mine': True if obj.author.id == currentUser.id else False,
            }
        else:
            return {
                'liked': False, 
                'mine': False,
            }

class PostLikesSchema(Schema):
    name = fields.Method('getName')
    color = fields.Method('getColor')
    icon = fields.Method('getIcon')
    
    class Meta:
        fields = (
            'name',
            'color',
            'icon',
        )

    def getName(self, obj):
        return obj.like.name

    def getColor(self, obj):
        return obj.like.color

    def getIcon(self, obj):
        return obj.like.icon

class PostInfoSchema(Schema):
    posted_on = fields.Method('getTimeAgo')
    likes_count = fields.Method('getLikesCount')
    tags = fields.Nested(PostTagsSchema, many=True)
    description = fields.Method('getDesc')
    keywords = fields.Method('getKeywords')
    comments = fields.Nested(CommentsSchema, many=True)

    class Meta:
        fields = (
            'thumbnail',
            'posted_on',
            'likes_count',
            'tags',
            'text',
            'description',
            'keywords',
            'closed',
            'closed_on',
            'closed_by',
            'comments'
        )

    def getTimeAgo(self, obj):
        return obj.time_ago()

    def getLikesCount(self, obj):
        return len(obj.likes)

    def getDesc(self, obj):
        return cleanhtml(obj.text)[:97]

    def getKeywords(self, obj):
        return ', '.join([key.tag.name for key in obj.tags])


class AuthorPersSchema(Schema):
    class Meta:
        fields = (
            'profession',
        )

class AuthorInfoSchema(Schema):
    full_name = fields.Method('getFullName')
    joined_on = fields.Method('getJoinedOn')

    class Meta:
        fields = (
            'avatar_img',
            'full_name',
            'joined_on'
        )

    def getFullName(self, obj):
        return obj.first_name + ' ' + obj.last_name

    def getJoinedOn(self, obj):
        return str(obj.created_on.ctime())[:-14] + ' ' + str(obj.created_on.ctime())[20:]

class LanguageSchema(Schema):
    class Meta:
        fields = (
            'code',
            'name'
        )

class AuthorSchema(Schema):
    info = fields.Nested(AuthorInfoSchema)
    posts = fields.Nested(PostMinSchema, many=True)
    location = fields.Nested(AuthorLocation)
    language = fields.Nested(LanguageSchema)
    pers = fields.Nested(AuthorPersSchema)
    
    class Meta:
        fields = (
            'name',
            'info',
            'posts',
            'location',
            'pers',
            'language'
        )


class PostLikes(Schema):
    class Meta:
        fields = (
            'author',
            'info'
        )


class PostSchema(Schema):
    author = fields.Nested(AuthorSchema)
    info = fields.Nested(PostInfoSchema)
    userInfo = fields.Method('getUserInfo')

    class Meta:
        fields = (
            'title',
            'read_time',
            'author',
            'info',
            'link',
            'userInfo',
            'id'
        )

    def getUserInfo(self, obj):
        currentUser = self.context.get('currentUser')
        if currentUser:
            return {
                'liked': True if Post_Likes.get().filter(and_(Post_Likes.author==currentUser.id, Post_Likes.post==obj.id)).first() is not None else False, 
                'following': True if User_Following.get().filter(and_(User_Following.user==currentUser.id, User_Following.followed==obj.author.id)).first() is not None else False,
                'mine': True if obj.author.id == currentUser.id else False,
                'saved': True if Saved_Posts.get().filter(and_(Saved_Posts.user==currentUser.id, Saved_Posts.post==obj.id)).first() is not None else False
            }
        else:
            return {
                'liked': False, 
                'mine': False,
            }

PostSchemaOnly = PostSchema(many=False)

class NewPostTagsSchema(ModelSchema):
    class Meta:
        model = Post_Tags
        include_fk = True
        sqla_session = db.session

class NewPostInfoSchema(ModelSchema):
    tags = fields.Nested(NewPostTagsSchema, many=True)

    class Meta:
        model = Post_Info
        sqla_session = db.session

class NewPostSchema(ModelSchema):
    info = fields.Nested(NewPostInfoSchema, many=False)

    class Meta:
        model = Post
        include_fk = True
        sqla_session = db.session
