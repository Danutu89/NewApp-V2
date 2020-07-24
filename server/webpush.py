from pywebpush import webpush, WebPushException
from models import Notification_Subscriber
import json

VAPID_PRIVATE_KEY = "gdZv-jxuKPeaukXrkXlKZ33j4zbLDe60WCnAN0Pba94"
VAPID_PUBLIC_KEY = "BGfsb_G1tXj-jSN8h-9spz2znzfm1sib-Xx42FLmN8p7xQwv8C_ke_-77DFKkBiv843msSFlvQw0PDr2--mpJmw"
VAPID_CLAIMS = {"sub": "mailto:develop@raturi.in"}

def send_notification(users, body):
    check = Notification_Subscriber.get().filter(Notification_Subscriber.user.in_([users])).all()
    for c in check:
        try:
            sub = (str(c.info).encode().decode('utf-8')).replace("'", '"')
            sub = sub.replace("None", "null")
            body = ((str(body).replace("'", '"')).replace("None", "null"))
            send_web_push(json.loads(sub), body)
        except:
            pass


def send_web_push(subscription_information, body):
    return webpush(
        subscription_info=subscription_information,
        data=body,
        vapid_private_key=VAPID_PRIVATE_KEY,
        vapid_claims=VAPID_CLAIMS
    )