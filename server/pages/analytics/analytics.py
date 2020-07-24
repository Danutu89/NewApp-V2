from flask import Blueprint, make_response, jsonify, request
from .modules.serializer import ViewSchema, LocationSchema
from models import Location, Ip_Location, Post
from app import db
from sqlalchemy import Sequence
import requests

analytics = Blueprint('analytics', __name__, url_prefix='/api/v2/analytics')

@analytics.route('view', methods=['POST'])
def view():
    data = request.json
    userIP = None
    post_id = None

    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        userIP = request.environ['REMOTE_ADDR']
    else:
        userIP = request.environ['HTTP_X_FORWARDED_FOR']

    ips = userIP.split(',')
    userIP = ips[0]

    if userIP == '127.0.0.1':
        userIP = '81.196.139.149'

    check_ip = Ip_Location.get().filter(Ip_Location.ip == userIP).first()

    if check_ip is None:
        try:
            resp = requests.get(
                ('https://www.iplocate.io/api/lookup/{}').format('81.196.139.149'))
            userLoc = resp.json()
            iso_code = userLoc['country_code']
            api_2 = requests.get(
                ("https://restcountries.eu/rest/v2/alpha/{}").format(iso_code))
            result_2 = api_2.json()
        except:
            pass

        ip_loc_index = str(db.session.execute(Sequence('ip_location_id_seq')))
        loc_index = str(db.session.execute(Sequence('location_id_seq')))

        ip_schema = {
            "ip": userIP,
            "id": ip_loc_index,
            "location": {
                "id": loc_index,
                "city": userLoc['city'],
                "country": userLoc['country'],
                "flag": result_2['languages'][0]['iso639_1'],
                "iso": userLoc['country_code'],
                "latitude": str(userLoc['latitude']),
                "longitude": str(userLoc['longitude']),
            }
        }
    else:
        ip_schema = LocationSchema().dump(check_ip)

    if '/post/' in data['route']:
        url_part = data['route'].split('/')[-1]
        id = url_part.split('-')[-1]
        post = Post.get().filter(Post.id==int(id)).first()
        post_id = post.id if post else None

    new_view = ViewSchema(many=False).load({
        "type": 'post' if '/post/' in data['route'] else 'page',
        "route": data['route'],
        "ip": ip_schema,
        "post_id": post_id
    })

    new_view.add()

    return make_response(jsonify({'operation': 'success'}), 200)

    
