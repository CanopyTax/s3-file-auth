import asyncio
import os

from aiohttp import web
import aiohttp_autoreload
import aiobotocore
from botocore.exceptions import ClientError


debug = True
bucket_name = os.getenv('S3_BUCKET')
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
    print(dir(request))
    return web.Response(status=204)


async def init(loop):
    global session
    session = aiobotocore.get_session(loop=loop)
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/test', handle_auth)
    app.router.add_route('GET', '/{tail:.*}', stream_file)  # Everything else
    handler = app.make_handler(debug=debug)
    await loop.create_server(handler, '0.0.0.0', 8080)
    print('======= Private Server running at :8080 =======')


def main():
    global loop
    # setup
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init(loop))

    if debug:
        print('debug enabled, auto-reloading enabled')
        aiohttp_autoreload.start()

    # Run server
    loop.run_forever()

if __name__ == '__main__':
    main()
