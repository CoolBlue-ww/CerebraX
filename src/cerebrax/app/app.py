"""
注册各个路由器
"""
from fastapi import FastAPI, Request
from lifespan import lifespan
from routers import (shutdown, database, proxy)


app = FastAPI(
    title='CerebraX',
    lifespan=lifespan,
)

app.include_router(shutdown.shutdown_router)
app.include_router(database.memory_database_router)
app.include_router(proxy.proxy_router)

@app.get('/metrics')
async def metrics():
    return {'message': 'success'}

@app.get('/')
async def root():
    return {'message': "Welcome to CerebraX!"}


