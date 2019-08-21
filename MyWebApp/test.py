
import myorm, asyncio
from models import User, Blog, Comment

#测试函数,协程
async def test(loop):
	await myorm.create_pool(loop=loop, user='root', password='1234', database='mywebdb')
	user = User(name='test', email='test@666.com', passwd='123456', image='about:blank')
	await user.save()


if __name__ == '__main__':
	#运行协程的固定写法
	loop = asyncio.get_event_loop()
	loop.run_until_complete(test(loop))
	loop.run_forever()

