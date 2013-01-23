from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    )


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('form', '/form')
    config.add_route('messages', '/messages')
    config.add_route('message_add', '/message/add')
    config.add_route('user_add', '/user/add')
    config.add_route('user_del', '/user/delete')
    config.add_route('api_version', '/api_version')
    config.scan()
    return config.make_wsgi_app()
