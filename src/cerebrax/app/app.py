"""
注册各个路由器
"""
from fastapi import FastAPI, Request
from lifespan import lifespan
from routers import (shutdown, database, proxy)
import types


app = FastAPI(
    title='CerebraX',
    lifespan=lifespan,
)
"""
初始化必要的属性，避免获取时抛出异常
"""
app.state.implementation_classes = None  # 初始化功能实现类
app.state.shared_instances = None  # 初始化动态共享对象类


app.include_router(shutdown.shutdown_router)
# app.include_router(database.memory_database_router)
app.include_router(proxy.proxy_router)

@app.get('/metrics')
async def metrics():
    return {'message': 'success'}

@app.get('/')
async def root():
    return {'message': "Welcome to CerebraX!"}


@app.get("/cfg")
async def cfg():
    shared_instance = app.state.shared_instances
    cfg = shared_instance.cfg_parser.proxy_cfg
    return cfg
