# -*- coding: utf-8 -*-

import asyncio, logging, aiomysql

#数据库连接池
async def create_pool(loop, **kw):
	logging.info('create database connection pool...')
	global __pool
	__pool = await aiomysql.create_pool(
		loop = loop,
		host = kw.get('host','127.0.0.1'),
		port = kw.get('port',3306),
		user = kw['user'],
		password = kw['password'],
		db = kw['database'],
		charset = kw.get('charset','utf8'),
		autocommit = kw.get('autocommit',True),
		maxsize = kw.get('maxsize',10),
		minsize = kw.get('minsize',1)
	)


#查找数据
async def select(sql, args, size=None):
	logging.info(sql,args)
	global __pool
	async with __pool.get() as conn:
		#aiomysql.DictCursor参数用于创建字典形式输出的游标
		async with conn.cursor(aiomysql.DictCursor) as cur:
			#把sql语句的占位符由'?'换回'%s'(mysql的占位符只有%s一种,任何类型都用它)
			await cur.execute(sql.replace('?','%s'), args or ())
			if size:
				rs = await cur.fetchmany(size)
			else:
				rs = await cur.fetchall()
		logging.info('rows returned: %s' % len(rs))
		return rs


#增删改数据
async def execute(sql, args, autocommit=True):
	logging.info(sql,args)
	global __pool
	async with __pool.get() as conn:
		if not autocommit:
			await conn.begin()
		try:
			async with conn.cursor(aiomysql.DictCursor) as cur:
				#把sql语句的占位符由'?'换回'%s'
				await cur.execute(sql.replace('?','%s'), args)
				affected = cur.rowcount
			if not autocommit:
				await conn.commit()
		except BaseException as e:
			if not autocommit:
				await conn.rollback()
			raise
		return affected


#构造占位符组字符串
def create_args_string(num):
	L = []
	for n in range(num):
		L.append('?')
	return ', '.join(L)


############################################数据库字段属性类###############################################

#列属性基类
class Field(object):

	#构造初始化
	def __init__(self, name, column_type, primary_key, default):
		self.name = name
		self.column_type = column_type
		self.primary_key = primary_key
		self.default = default

	#字符串化
	def __str__(self):
		return '<%s, %s:%s>' % (self.__class__.__name__,self.column_type,self.name)


#字符串类型列
class StringField(Field):

	#重写父类__init__函数
	def __init__(self, name=None, column_type='varchar(100)', primary_key=False, default=None):
		super().__init__(name, column_type, primary_key, default)


#布尔类型列
class BooleanField(Field):
	
	#重写父类__init__函数
	def __init__(self, name=None, default=False):
		super().__init__(name, 'boolean', False, default)


#整数类型列
class IntegerField(Field):

	#重写父类__init__函数
	def __init__(self, name=None, primary_key=False, default=0):
		super().__init__(name, 'bigint', primary_key, default)


#浮点数类型列
class FloatField(Field):

	#重写父类__init__函数
	def __init__(self, name=None, primary_key=False, default=0.0):
		super().__init__(name, 'real', primary_key, default)


#文本类型列
class TextField(Field):

	#重写父类__init__函数
	def __init__(self, name=None, default=None):
		super().__init__(name, 'text', False, default)



############################################数据库表映射关系类###############################################

#Model基类的元类
class ModelMetaclass(type):

	def __new__(cls, name, bases, attrs):
		if name == 'Model':
			return type.__new__(cls, name, bases, attrs)  #创建基类本身毫无意义
		tableName = attrs.get('__table__',None) or name  #表名,如果参数中未指定表名则默认和类名同名
		logging.info('found model: %s (table: %s)' % (name, tableName))
		mappings = dict()  #类属性与数据表字段映射字典
		fields = []  #除主键以外的其他的类属性集合(注意不是实例属性)
		primaryKey = None  #主键对应的类属性
		for k, v in attrs.items():
			#遍历该类的所有属性(包含函数),如果是数据表字段属性就存入映射字典,并移除类属性
			if isinstance(v, Field):
				logging.info('  found mapping: %s ==> %s' % (k, v))
				mappings[k] = v
				if v.primary_key:  #如果这个属性对应的是主键
					if primaryKey:  #如果已经有另一个主键存在
						raise StandardError('Duplicate primary key for field %s' % k)
					primaryKey = k  #把这个类属性标记为主键属性
				else:
					fields.append(k)  #添加到非主键列的对应属性集合中
		if not primaryKey:
			raise StandardError('Primary key not found.')  #没有找到主键则抛出错误
		for k in mappings.keys():
			attrs.pop(k)  #把字段属性从类属性中剔除,因为将来会给每个实例绑定同名属性,类属性至此已无用处
		attrs['__table__'] = tableName  #类属性__table__记录表名
		attrs['__mappings__'] = mappings  #类属性__mappings__记录映射关系
		attrs['__primary_key__'] = primaryKey  #类属性__primary_key__记录主键属性
		attrs['__fields__'] = fields  #类属性__fields__记录除主键外的其他属性
		#用于增删改查的sql语句(下面的赋值占位符用'?'是因为cursor.execute函数需要两个参数,一个是带赋值占位符的sql语句,另一个参数是占位符对应的值组,所以sql语句在编译时是没有对应值组的,换成'?'就不会报错了)
		attrs['__select__'] = 'select `%s`,%s from `%s`' % (primaryKey, ','.join(list(map(lambda f: '`%s`' % (mappings.get(f).name or f), fields))), tableName)  #类属性__select__记录查询语句
		attrs['__insert__'] = 'insert into `%s` (%s,`%s`) values (%s)' % (tableName, ', '.join(list(map(lambda f: '`%s`' % (mappings.get(f).name or f), fields))), primaryKey, create_args_string(len(fields)+1))  #类属性__insert__记录增添语句
		attrs['__update__'] = 'update `%s` set %s where `%s` = ?' % (tableName, ', '.join(list(map(lambda f: '`%s`=?' % (mappings.get(f).name or f), fields))), primaryKey)  #类属性__update__记录修改语句
		attrs['__delete__'] = 'delete from `%s` where `%s` = ?' % (tableName, primaryKey)
		#调用父类type的__new__函数构建具体的类
		return type.__new__(cls, name, bases, attrs)


#Model--数据基类
#继承自dict,并指定了元类,所有子类均具备字典功能并且由元类量身构建
class Model(dict, metaclass = ModelMetaclass):

	#初始化函数,继承父类的属性以及字典功能
	def __init__(self, **kw):
		super().__init__(**kw)


	#特殊函数__getattr__,使字典中的元素可以像属性一样通过a.b形式访问
	def __getattr__(self, key):
		try:
			return self[key]
		except KeyError:
			raise AttributeError(r"'Model' object has no attribute %s" % key)


	#特殊函数__setattr__,使实例可以通过a.b=c形式给字典添加元素
	def __setattr__(self, key, value):
		self[key] = value


	#用于获取某个属性的值(如果未显式赋值且无映射关系则返回空,如果存在映射关系且未显示赋值,则根据映射关系得到属性的默认缺省值)
	def getValue(self, key):
		value = getattr(self, key, None)
		if value is None:
			#如果未显示绑定赋值,则查找是否存在映射关系
			field = self.__mappings__.get(key)
			if field is not None:
				if field.default is not None:
					#存在映射关系,并且缺省值不为空,则拿到缺省值,注意可能是函数
					value = field.default() if callable(field.default) else field.default
					logging.info('using default value for %s:%s' % (key, str(value)))  #%s占位符只能对应字符串类型数据
					setattr(self, key, value)  #显示绑定属性值,以便下一次直接拿
		return value


	#类函数,用来查找符合要求的数据集合,并转换成对应类的实例对象数组
	@classmethod
	async def findAll(cls, where=None, args=None, **kw):
		sql = [cls.__select__]  #用于保存数据库语法的各个组成部分
		#如果where参数不为空,说明查找带附加条件
		if where:
			sql.append('where')  #在查找语句尾部添加'where'字样
			sql.append(where)  #在查找语句尾部添加查找条件字符串
		#如果占位属性值集合未指定,就给指定一个空数组(一个'?'占位符对应一个值)
		if args is None:
			args = []
		#如果关键字参数'orderBy'不为空,则说明要进行排序
		orderBy = kw.get('orderBy', None)
		if orderBy:
			sql.append('order by')  #在查找语句尾部添加'order by'字样
			sql.append(orderBy)  #在查找语句尾部添加排序条件字符串
		#如果关键字参数'limit'不为空,则说明附加索引及条数限制
		limit = kw.get('limit', None)
		if limit:
			sql.append('limit')  #在查询语句尾部添加'limit'字样
			#如果limit参数传的是整数,说明索引从0开始
			if isinstance(limit, int):
				sql.append('?')  #在查询语句尾部添加一个'?'占位符(后面替换成'%s')
				args.append(limit)  #把limit限制值加入占位符值组中
			#如果limit参数传的是元组,并且长度为2,说明指定了起始索引和条数
			elif isinstance(limit, tuple) and len(limit) == 2:
				sql.append('?, ?')  #在查询语句尾部添加两个'?'占位符,分别对应起始索引和条数
				args.extend(limit)  #将limit元表扩展添加到占位符值组args列表中
			else:
				raise ValueError('Invalid limit value: %s' % str(limit))  #传值错误
		rs = await select(' '.join(sql), args)  #执行查询语句并等待查询结果
		return [cls(**r) for r in rs]  #rs是由一个或多个字典组成的元表,每个字典对应数据库表中的一行数据,而每一行数据都可以用来创建一个对应类的实例对象


	#类函数,用于获取符合查询要求的数据行数
	'''
	@classmethod
	async def findNumber(cls, selectField, where=None, args=None)
		sql = ['select %s _num_ from `%s`' % (selectField, cls.__table__)]
		#如果包含查询条件
		if where:
			sql.append('where')  #在查询语句尾部添加'where'关键字
			sql.append(where)  #在查询语句尾部添加where条件字符串
		rs = await select(' '.join(sql), args, 1)  #执行查询语句并等待查询结果
		if len(rs) == 0:
			return None
		return rs[0]['_num_']  #返回查询结果第一行中的'_num_'键对应的值,即符合要求的数据行数
	'''


	#类函数,根据主键值查找一条数据,返回由这条数据构建的映射类实例对象
	@classmethod
	async def find(cls, pk):
		rs = await select('%s where `%s`=?' % (cls.__select__, cls.__primary_key__), [pk], 1)
		if len(rs) == 0:
			return None  #没有找到则返回空值
		return cls(**rs[0])  #有则返回由首行数据构建的映射类实例


	#实例函数,用于往数据库表中增加一条数据(数据各字段对应该实例的映射属性)
	async def save(self):
		args = list(map(self.getValue, self.__fields__))  #占位符值组(除主键值外)
		args.append(self.getValue(self.__primary_key__))  #把主键值加上(没有则为空,即自增)
		rows = await execute(self.__insert__, args)  #执行插入语句
		if rows != 1:
			#增加数据失败
			logging.warn('faild to insert record: affected rows; %s' % str(rows))


	#实例函数,用于修改数据库表中的某条数据(以主键为索引)
	async def update(self):
		args = list(map(self.getValue, self.__fields__))  #占位符值组(除主键外)
		args.append(self.getValue(self.__primary_key__))  #修改数据是以主键为索引的,故要加上主键值
		rows = await execute(self.__update__, args)  #执行修改语句
		if rows != 1:
			logging.warn('faild to update by primary key: affected rows: %s' % str(rows))	



	#实例函数,用于删除数据库表中的某条数据(以主键为索引)
	async def remove(self):
		args = [self.getValue(self.__primary_key__)]
		rows = await execute(self.__delete__, args)
		if rows != 1:
			logging.warn('faild to remove by primary key: affected rows: %s' % str(rows))









