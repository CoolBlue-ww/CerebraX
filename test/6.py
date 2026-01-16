import asyncio

async def q(x):
    count = 0
    while count < 5:
        print(f"第{5 - count}秒后释放暂停")
        count += 1
        await asyncio.sleep(1)
    print("继续执行主循环")
    x.set()

async def test(x):

    count = 0
    while True:
        if count == 10:
            print("循环正式进入休眠，立即开始计时。")
            asyncio.create_task(q(x))
            await x.wait()
        print(f"当前count为：{count}，还未进入暂停。")
        count += 1

async def main():
    event = asyncio.Event()
    await test(event)
    while True:
        await asyncio.sleep(1)


asyncio.run(main())