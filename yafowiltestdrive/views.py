from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    MyModel,
    Users,
    Messages,
)

import requests
import json

from yafowil import loader
import yafowil.webob
from yafowil.base import factory
from yafowil.controller import Controller

address, port = '127.0.0.1', 6543
url = 'http://%s:%s/form' % (address, port)
apiurl_useradd = 'http://127.0.0.1:6542/user'


def make_user_put(name):
    data = json.dumps(
        {'name': name, }
    )
    r = requests.put('http://127.0.0.1:6542/users', data, )
#    print dir(r)
    print("the result of requests.put")
    print r.json()
    return r.json


def make_message_post(message, token):
    data = json.dumps(
        {'text': message, }
    )
    print("in make_message_post: ")
    print("data: " + data)
    print("token: " + token)
    _auth_header = {'X-Messaging-Token': token}
    r = requests.post(
        'http://127.0.0.1:6542/', data,
        headers=_auth_header)

    print("result of make_message_post:")
    print r.json
    return r.json


def store(widget, data):
    print("the widget:")
    print(widget)
    print("the data:")
    print(data.fetch('username.name').extracted)
    print("about to PUT")
    make_user_put(data.fetch('username.name').extracted)
    print("done with PUT")


def store_user(widget, data):
    print("about to PUT user")
    res = make_user_put(data.fetch('username.name').extracted)
    print(res)
    print("done with PUTting user")
    return res


def store_message(widget, data):
    #print("the data:")
    #print(data.fetch('messages.message').extracted)
    #print("about to POST")
    res = make_message_post(
        data.fetch('messages.message').extracted,
        data.fetch('messages.token').extracted)
    #print("done with POST")
    return res


def next(request):
    #import pdb
    #pdb.set_trace()
    #print(request)
    return url


# yafowil 'blueprint' for a custom validator
def myvalidator(widget, data):
    # validate the data, raise ExtractionError if somethings wrong
    #if (data.extracted != 'something'):
    if (' ' in data.extracted):
        raise ExtractionError("only '' is allowed as input.")
    return data.extracted
#
#widget = factory('field:label:*myvalidation:text',
#                 props={'label': 'Inner Field'},
#                 custom={'myvalidation': dict(extractor=[myvalidator])#}
#)


# this is also the user_add and/or get_token view
@view_config(route_name='form', renderer='templates/formtemplate.pt')
def form_view(request):

    if (
        ('action.username.submit' in request.POST)
            and (request.POST['username.name'] != '')):
        #print request.POST
        uname = request.POST['username.name']
        res = make_user_put(uname)
        if 'status' in res() and res()[u'status'] == u'error':
            return {
                'form': 'username exists! <a href="/form">come again</a>'
            }
        #token = res()['token']
        print(type(res))
        print(dir(res))
        print(res()['token'])
        return {'form': "your token: " + str(res()['token'])}

    #print("next: " + next(request))
    form = factory(
        u'form',
        name='username',
        props={
            'action': 'http://127.0.0.1:6543/form'
        },
        custom={'myvalidation': dict(extractor=[myvalidator])}
    )
    form['name'] = factory('field:label:error:text', props={
        'label': 'Enter a name',
        'value': '',
        'required': True})
    form['submit'] = factory('field:submit', props={
        'label': 'get token',
        'action': 'save',
        'handler': store_user,
        'next': next})
    controller = Controller(form, request)
    form1 = controller.rendered

    return {'form': form1, }


@view_config(route_name='message_add', renderer='templates/message_add.pt')
def message_add_view(request):

    if (
        ('action.messages.submit' in request.POST)
            and (request.POST['messages.token'] != '')):
        #print("the request.POST:")
        #print request.POST
        message = request.POST['messages.message']
        token = request.POST['messages.token']
        print("form was submitted, here are the values:")
        print message
        print token
        res = make_message_post(message, token)
        #print("the result of the post")
        #print(res)
        #print(dir(res))

        #if 'status' in res() and res()[u'status'] == u'error':
        #    return {
        #        'form': 'wtf? <a href="/message/add">come again</a>'
        #    }
        #token = res()['token']
        print("========== res type, dir and content ============")
        print(type(res))
        print(dir(res))
        print(res)
        if 'status' in res() and res()['status'] == 'added':
            result = "your message was added."
        else:
            result = res()['error']
        return {'form': result}
        #return {'form': "nothing yet..."}
##    if request.
    #print("the request:.............................")
    #print(request)
    #print("end request:.............................")
    print("next: (will be overridden)")
    print(next)
    mform = factory(
        u'form',
        name='messages',
        props={
            'action': 'http://192.168.2.111:6543/message/add'
        }
    )
    mform['message'] = factory('field:label:error:text', props={
        'label': 'Enter a message',
        'value': '',
        'required': True})
    mform['token'] = factory('field:label:error:text', props={
        'label': 'Enter your token',
        'value': '',
        'required': True})
    mform['submit'] = factory('field:submit', props={
        'label': 'store message',
        'action': 'save',
        'handler': store_message,
        'next': next})
    controller = Controller(mform, request)
    form_ = controller.rendered

    return {'form': form_, }


@view_config(route_name='messages', renderer='templates/messages.pt')
def messages_view(request):
    r = requests.get('http://127.0.0.1:6542')
    print("status:" + str(r.status_code))
    # make result beautiful
    print r
    #import pdb
    #pdb.set_trace()
    list = r.json()  # [0]

    return {'messages': list}


@view_config(route_name='api_version', renderer='templates/messages.pt')
def api_version(request):
    r = requests.get('http://127.0.0.1:6542/api_version')
    #print("status:" + str(r.status_code))
    return {'messages': "API version: " + r.json()['API version'], }

from requests.exceptions import ConnectionError


@view_config(route_name='home', renderer='templates/mytemplate.pt')
def my_view(request):
    try:
        #one = DBSession.query(MyModel).filter(MyModel.name == 'one').first()
        r = requests.get('http://127.0.0.1:6542/api_version')
    except ConnectionError, ce:
        print("..ConnectionError!! " + str(ce))
        return {
            'APIstatus': 'down!',
            'project': 'yafowil.testdrive'
        }
    return {
        'APIstatus': r.json()['API version'],
        'project': 'yafowil.testdrive'
    }

conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_yafowil.testdrive_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""
