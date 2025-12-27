"""
定义内部可复用的全局对象
"""
from src.cerebrax.common_depend import (
    httpx,
    docker,
    AsyncRedis,
    ProcessPoolExecutor,
    ThreadPoolExecutor,
)

# -------------------------- Httpx ----------------------------------
httpx_client = httpx.AsyncClient()  # 内部http的异步客户端
# -------------------------- Redis ----------------------------------
redis_client = AsyncRedis() # 内部redis连接客户端
# -------------------------- Process Pool ---------------------------
process_pool = ProcessPoolExecutor(max_workers=10)
# -------------------------- Thread Pool ----------------------------
thread_pool = ThreadPoolExecutor(max_workers=10)
# -------------------------- Docker ---------------------------------
docker_client = docker.from_env()

