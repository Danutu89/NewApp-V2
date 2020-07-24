from marshmallow import fields, Schema
from models import Post, User, User_Info, Post_Info, Post_Tags, Saved_Posts, Post_Tag
from sqlalchemy import and_

class AuthorInfoSchema(Schema):
    real_name = fields.Method('getFullName')

    def getFullName(self, obj):
        return obj.first_name + ' ' + obj.last_name

    class Meta:
        model = User_Info
        fields = (
            'avatar_img',
            'real_name'
        )

class AuthorSchema(Schema):
    
    info = fields.Nested(AuthorInfoSchema)
    
    class Meta:
        fields = (
            'name',
            'info'
        )

class PostTagSchema(Schema):
    class Meta:
        model = Post_Tag
        fields = (
            'name',
            'color',
            'icon'
        )

PostTagsOnlySchema = PostTagSchema(many=True)

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

class PostInfoSchema(Schema):

    posted_on = fields.Method('getTimeAgo')
    likes_count = fields.Method('getLikesCount')
    tags = fields.Nested(PostTagsSchema, many=True)

    class Meta:
        model = Post_Info
        fields = (
            'thumbnail',
            'posted_on',
            'likes_count',
            'tags'
        )

    def getTimeAgo(self, obj):
        return obj.time_ago()

    def getLikesCount(self, obj):
        return len(obj.likes)

class PostSchema(Schema):
    author = fields.Nested(AuthorSchema)
    info = fields.Nested(PostInfoSchema)
    saved = fields.Method('ifSaved')

    class Meta:
        model = Post
        fields = (
            'title',
            'read_time',
            'author',
            'info',
            'link',
            'saved',
            'id'
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

PostsSchema = PostSchema(many=True)