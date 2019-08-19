# -*- coding: utf-8 -*-

from aiohttp import web  #导入模块

routes = web.RouteTableDef()

#获取主页html函数
@routes.get('/')
async def index(request):
    return web.Response(text='awsome')


app = web.Application()
app.add_routes(routes)
web.run_app(app, host='127.0.0.1', port=9090)