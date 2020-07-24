from models.models import User, User_Pers, User_Info, User_Role, Role_Permissions, Status_Types, Languages, Like_Type, Notification_Type

offline = Status_Types(
    name='Offline',
    color='#e60b00'
)
online = Status_Types(
    name='Online',
    color='#29f500'
)

offline.add()
online.add()

language = Languages(
    name='English',
    code='en'
)

language.add()

heart = Like_Type(
    name="Heart",
    color="#ff2b2b",
    icon="heart"
)

heart.add()

notification_types = [
    Notification_Type(name="follow"),
    Notification_Type(name="like"),
    Notification_Type(name="comment"),
    Notification_Type(name="reply"),
    Notification_Type(name="share"),
    Notification_Type(name="mention")
]

for n in notification_types:
    n.add()

admin_role = User_Role(
    name="Admin"
)
admin_role.add()

admin_permissios = Role_Permissions(
    role=admin_role.id,
    edit_user=True,
    delete_user=True,
    add_post=True,
    edit_post=True,
    delete_post=True,
    add_reply=True,
    edit_reply=True,
    delete_reply=True,
    admin=True
)

admin_permissios.add()

member_role = User_Role(
    name="Member"
)
member_role.add()

member_permissios = Role_Permissions(
    role=member_role.id
)
member_permissios.add()

admin = User(
    name="Danutu",
    email="danutu@new-app.dev",
    password="FCsteaua89",
    confirmed=True,
    role_id=admin_role.id,
    language_id=1
)

admin.add()

admin_info = User_Info(
    user=admin.id,
    first_name="Daniel",
    last_name="Ionut"
)

admin_info.add()

admin_pers = User_Pers(user=admin.id)
admin_pers.add()