from marshmallow import fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, ModelSchema
from sqlalchemy import and_
from app import db
from models import Ip_Location, Location, User, User_Pers, User_Info, Languages, User_Following
from pages.post.modules.serializer import CommentsSchema, PostMinSchema, PostTagsSchema

class NewLocationSchema(ModelSchema):
    class Meta:
        model = Location
        sqla_session = db.session

class NewIpSchema(ModelSchema):
    location = fields.Nested(NewLocationSchema, many=False)

    class Meta:
        model = Ip_Location
        include_fk = True
        sqla_session = db.session

class NewLanguageSchema(ModelSchema):
    class Meta:
        model = Languages
        sqla_session = db.session

class NewUserPersSchema(ModelSchema):
    class Meta:
        model = User_Pers
        include_fk = True
        sqla_session = db.session

class NewUserInfoSchema(ModelSchema):
    class Meta:
        model = User_Info
        include_fk = True
        sqla_session = db.session

class NewUserSchema(ModelSchema):
    info = fields.Nested(NewUserInfoSchema, many=False)
    pers = fields.Nested(NewUserPersSchema, many=False)
    language = fields.Nested(NewLanguageSchema, many=False)
    location = fields.Nested(NewIpSchema, many=False)

    class Meta:
        model = User
        include_fk = True
        sqla_session = db.session

class UserInfoSchema(Schema):
    full_name = fields.Method('getFullName')
    joined_on = fields.Method('getJoinedOn')

    class Meta:
        fields = (
            'avatar_img',
            'cover_img',
            'joined_on',
            'first_name',
            'last_name',
            'full_name'
        )

    def getFullName(self, obj):
        return obj.first_name + ' ' + obj.last_name

    def getJoinedOn(self, obj):
        return str(obj.created_on.ctime())[:-14] + ' ' + str(obj.created_on.ctime())[20:]

class UserMinSchema(Schema):
    info = fields.Nested(UserInfoSchema, many=False)

    class Meta:
        fields = (
            'name',
            'info',
            'id'
        )

class UserFollowingSchema(Schema):
    user_rel = fields.Nested(UserMinSchema, many=False)

    class Meta:
        fields = (
            'user_rel',
        )

class UserPersSchema(Schema):
    class Meta:
        fields = (
            'bio',
            'birthday',
            'profession'
        )

class SocialSchema(Schema):
    class Meta:
        fields = (
            'name',
            'icon',
            'pre_link',
            'id'
        )

class UserSocialSchema(Schema):
    social = fields.Nested(SocialSchema, many=False)

    class Meta:
        fields = (
            'social',
            'link',
            'id'
        )

class LocationSchema(Schema):
    class Meta:
        fields = (
            'country',
            'flag',
            'city',
        )

class IpSchema(Schema):
    location = fields.Nested(LocationSchema, many=False)

    class Meta:
        fields = (
            'ip',
            'location'
        )

class LanguageSchema(Schema):
    class Meta:
        fields = (
            'code',
            'name'
        )

class UserSchema(Schema):
    info = fields.Nested(UserInfoSchema, many=False)
    pers = fields.Nested(UserPersSchema, many=False)
    language = fields.Nested(LanguageSchema, many=False)
    location = fields.Nested(IpSchema, many=False)
    tags = fields.Nested(PostTagsSchema, many=True)
    comments = fields.Nested(CommentsSchema, many=True)
    p_list = fields.Nested(PostMinSchema, many=True)
    social = fields.Nested(UserSocialSchema, many=True)
    following = fields.Nested(UserFollowingSchema, many=True)
    userInfo = fields.Method('getUserInfo')
    posts = fields.Method('getPosts')
    posts_count = fields.Method('getPostsCount')
    comments_count = fields.Method('getCommentsCount')
    followers_count = fields.Method('getFollowersCount')

    class Meta:
        fields = (
            'name',
            'email',
            'info',
            'pers',
            'language',
            'location',
            'social',
            'tags',
            'comments',
            'posts',
            'posts_count',
            'comments_count',
            'following',
            'followers_count',
            'userInfo'
        )

    def getUserInfo(self, obj):
        currentUser = self.context.get('currentUser')
        if currentUser:
            return {
                'following': True if User_Following.get().filter(and_(User_Following.user==currentUser.id, User_Following.followed==obj.id)).first() is not None else False,
                'mine': True if obj.id == currentUser.id else False,
            }
        else:
            return {
                'following': False,
                'mine': False,
            }

    def getPosts(self, obj):
        posts = self.context.get('posts')
        return {
            'hasnext': posts.has_next,
            'list': PostMinSchema(many=True).dump(posts.items)
        }

    def getPostsCount(self, obj):
        return len(obj.posts)
        
    def getCommentsCount(self, obj):
        return len(obj.comments)

    def getFollowersCount(self, obj):
        return len(obj.followed)
    

class SettingsSchema(ModelSchema):
    info = fields.Nested(UserInfoSchema, many=False, exclude=('joined_on',))
    pers = fields.Nested(UserPersSchema, many=False)
    social = fields.Nested(UserSocialSchema, many=True)

    class Meta:
        model = User
        sqla_session = db.session
        fields = (
            'info',
            'pers',
            'social'
        )