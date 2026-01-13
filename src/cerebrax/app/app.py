"""
注册各个路由器
"""
from lifespan import lifespan
from routers import (shutdown, proxy)
from src.cerebrax.common_depend import (
    FastAPI, Request,
)
from src.cerebrax._container import (
    Shared,
    Toolkit,
)

app = FastAPI(
    title='CerebraX',
    lifespan=lifespan,
)
"""
初始化必要的属性，避免获取时抛出异常
"""
app.state.shared = Shared()
app.state.toolkit = Toolkit()

app.include_router(shutdown.shutdown_router)
# app.include_router(database.memory_database_router)
app.include_router(proxy.proxy_router)

@app.get('/metrics')
async def metrics():
    return {'message': 'success'}

@app.get('/')
async def root():
    return {'message': "Welcome to CerebraX!"}
