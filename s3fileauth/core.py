import asyncio
import os

from aiohttp import web
import aiobotocore
from botocore.exceptions import ClientError
import aiohttp_oauth


debug = os.getenv('DEBUG', False)
bucket_name = os.getenv('S3_BUCKET')
gh_id = os.getenv('GITHUB_ID')
gh_secret = os.getenv('GITHUB_SECRET')
gh_org = os.getenv('GITHUB_ORG')
gsuite_id = os.getenv('GSUITE_ID')
gsuite_secret = os.getenv('GSUITE_SECRET')
gsuite_org = os.getenv('GSUITE_ORG')
gsuite_redirect_url = os.getenv('GSUITE_REDIRECT_URI')
cookie_name = os.getenv('COOKIE_NAME', 's3githubauth')
cookie_key = os.getenv('COOKIE_KEY')

if None in (gh_id, gsuite_id):
    raise ValueError('GITHUB_ID, or GSUITE_ID '
                     'environment variables are missing')
if not bucket_name:
    raise ValueError('S3_BUCKET env var is required')
session = None


async def stream_file(request):
    key = request.path[1:]  # strip leading slash
    s3 = session.create_client('s3')
    content = None
    try:
        obj = await s3.get_object(Bucket=bucket_name, Key=key)
        content = obj['Body']

        response = web.StreamResponse(
            status=200,
            headers={
                'Content-Type': obj['ContentType'],
                'Content-Length': str(obj['ContentLength'])
            }
        )
        await response.prepare(request)
        while True:
            data = await content.read(25000)
            if not data:
                break
            response.write(data)
        await response.write_eof()
        await response.drain()
        return response

    except ClientError as e:
        return web.Response(body=str(e).encode(),
                            status=e.response.get('ResponseMetadata')
                                             .get('HTTPStatusCode'))
    finally:
        if content:
            content.close()
        s3.close()


async def handle_auth(request):
    return web.Response(status=204)

async def heartbeat_middleware_factory(app, handler):
    async def heartbeat(request):
        if request.path == '/healthz':
            return web.Response(status=200)
        return await handler(request)
    return heartbeat

def init():
    global session
    session = aiobotocore.get_session()
    app = web.Application(middlewares=[heartbeat_middleware_factory])
    if gh_id:
        aiohttp_oauth.add_oauth_middleware(
            app,
            github_id=gh_id,
            github_secret=gh_secret,
            github_org=gh_org,
            cookie_name=cookie_name,
            cookie_key=cookie_key
        )
    elif gsuite_id:
        aiohttp_oauth.add_oauth_middleware(
            app,
            gsuite=gsuite_id,
            gsuite_secret=gsuite_secret,
            gsuite_org=gsuite_org,
            gsuite_redirect_url=gsuite_redirect_url,
            cookie_name=cookie_name,
            cookie_key=cookie_key
        )
        
    app.router.add_route('GET', '/test', handle_auth)
    app.router.add_route('GET', '/{tail:.*}', stream_file)  # Everything else
    return app


def main():
    # setup
    app = init()
    handler = app.make_handler(debug=debug)

    # Run server
    web.run_app(app)

if __name__ == '__main__':
    main()
