import aiohttp
from aiohttp import web
from aiohttp_session import get_session
import asyncio
import logging
from pathlib import Path
from textwrap import dedent

from ..util import get_random_name
from ..model.errors import ModelError, NotFoundError, InvalidPasswordError


logger = logging.getLogger(__name__)

routes = web.RouteTableDef()


redirect_page = dedent('''
    <!DOCTYPE html>
    <html>
        <head>
            <title>Redirecting</title>
        </head>
        <body>
            <script>
                let nextUrl = null
                try {
                    nextUrl = window.localStorage.getItem('cwUrlAfterLogin')
                    window.localStorage.removeItem('cwUrlAfterLogin')
                } catch (err) {
                }
                // redirect
                window.location = nextUrl || '/'
            </script>
        </body>
    </html>
''')


def get_login_methods(conf):
    return {
        'facebook': {'url': '/auth/facebook'} if conf.fb_oauth2 else None,
        'google': {'url': '/auth/google'} if conf.google_oauth2 else None,
        'dev': {
            'student_url': '/auth/dev?role=student',
            'coach_url': '/auth/dev?role=coach',
            'admin_url': '/auth/dev?role=admin',
        } if conf.allow_dev_login else None,
    }


@routes.get('/auth/logout')
async def logout(req):
    session = await get_session(req)
    session['user'] = None
    raise  web.HTTPFound('/')


@routes.get('/auth/dev')
async def auth_dev(req):
    model = req.app['model']
    courses = req.app['courses']
    role = req.query['role']
    if role not in {'student', 'coach', 'admin'}:
        raise web.HTTPBadRequest(text=f'Unknown role: {role!r}')
    session = await get_session(req)
    name = get_random_name()
    logger.debug('Generated random name: %r', name)
    user = await model.users.create_dev_user(name)
    course_ids = [c.id for c in courses.list_active()]
    if role == 'student':
        await user.add_attended_courses(course_ids, author_user_id=None)
    if role == 'coach':
        await user.add_coached_courses(course_ids, author_user_id=None)
    if role == 'admin':
        await user.set_admin(True, author_user_id=None)
    session['user'] = {
        'id': user.id,
        'name': user.name,
    }
    return web.Response(text=redirect_page, content_type='text/html')


@routes.post('/auth/register')
async def register(req):
    data = await req.json()
    session = await get_session(req)
    session['user'] = None
    errors = []
    try:
        user = await req.app['model'].users.create_password_user(
            name=data['name'], email=data['email'], password=data['password'])
    except ModelError as e:
        errors.append(str(e))
    except Exception as e:
        logger.exception('create_password_user failed: %r', e)
        errors.append('Server error')
    return web.json_response({'errors': errors})


@routes.post('/auth/password-login')
async def register(req):
    data = await req.json()
    session = await get_session(req)
    session['user'] = None
    errors = []
    user = None
    try:
        user = await req.app['model'].users.login_password_user(
            email=data['email'], password=data['password'])
    except (NotFoundError, InvalidPasswordError) as e:
        errors.append('Nesprávný e-mail nebo heslo')
    except ModelError as e:
        errors.append(str(e))
    except Exception as e:
        logger.exception('login_password_user failed: %r', e)
        errors.append('Server error')
    assert user or errors
    if user:
        assert not errors
        session['user'] = {
            'id': user.id,
            'name': user.name,
        }
    return web.json_response({'errors': errors})
