import os
import requests
import json

from pytnyu import TNYUAPI

requests.packages.urllib3.disable_warnings()

api = TNYUAPI()
api_event_id = ''
access_token = os.environ['FACEBOOK_ACCESS_TOKEN']


def get_API_people_data():
    people = api.get_resource('people')
    people = people['data']
    return people


def get_event_information(api_event_id):
    event = api.get_resource('events/' + api_event_id)
    event = event['data']
    return event


def post_API_rsvp_data(user_id_list, api_event_id):
    event = get_event_information(api_event_id)
    for i in user_id_list:
        event['links']['rsvps']['linkage'].append({'type': 'people', 'id': i})
    event_data = {}
    event_data['data'] = {}
    event_data['data']['attributes'] = {}
    # event_data['data']['attributes']['aims'] = 'Learn New Skills'
    event_data['data']['type'] = 'events'
    event_data['data']['id'] = api_event_id
    event_data['data']['links'] = {}
    event_data['data']['links']['rsvps'] = {}
    event_data['data']['links']['rsvps'][
        'linkage'] = event['links']['rsvps']['linkage']
    headers = {
        'content-type': 'application/vnd.api+json',
        'accept': 'application/*, text/*',
        'x-api-key': os.environ['TNYU_API_KEY_ADMIN']
    }
    response = requests.patch('https://api.tnyu.org/v2/events/' + api_event_id,
                              data=json.dumps(event_data), headers=headers, verify=False)
    print response


def api_people_facebook_id_to_id():
    facebookid_to_id = {}
    people = get_API_people_data()
    for i in people:
        if 'attributes' in i and 'facebookId' in i['attributes']:
            facebook_id = i['attributes']['facebookId']
            person_id = i['id']
            facebookid_to_id[facebook_id] = person_id
    return facebookid_to_id


def normalize_rsvp_url(event_information):
    if 'attributes' in event_information and 'rsvpUrl' in event_information['attributes']:
        if event_information['attributes']['rsvpUrl'][-1] == '/':
            event_id = event_information[
                'attributes']['rsvpUrl'].split('/')[-2]
        else:
            event_id = event_information[
                'attributes']['rsvpUrl'].split('/')[-1]
        return event_id
    else:
        print 'Missing Facebook rsvpUrl'
        return False


def match_facebook_RSVP_to_API(access_token, api_event_id):
    event_information = get_event_information(api_event_id)
    event_id = normalize_rsvp_url(event_information)
    if not event_id:
        return

    facebook_url = 'https://graph.facebook.com/v2.4/{0}/attending?limit=10000&access_token={1}'
    events = requests.get(facebook_url.format(
        event_id, access_token), verify=False)
    events = json.loads(events.text)
    event_attendees = events['data']
    facebookid_to_id = api_people_facebook_id_to_id()
    rsvp_users_to_put_in_api = []
    for i in event_attendees:
        if i['id'] in facebookid_to_id:
            rsvp_users_to_put_in_api.append(facebookid_to_id[i['id']])
    post_API_rsvp_data(rsvp_users_to_put_in_api, api_event_id)

match_facebook_RSVP_to_API(access_token, api_event_id)
