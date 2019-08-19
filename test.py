
import time, uuid

class A(dict):

	def __init__(self,**kw):
		super(A,self).__init__(**kw)

	def __getattr__(self, key):
		try:
			return self[key]
		except KeyError:
			raise AttributeError(r"'Model' object has no attribute '%s'" % key)

	def __setattr__(self, key, value):
		self[key] = value



a=A(b=1,c=2,d=3)
setattr(a,'e',4)
print(a.e)
print(a.get('e'))
print(a['e'])
print('%015d%s000' % (int(time.time()*1000), uuid.uuid4().hex))