# -*- coding: utf-8 -*-

import time, uuid
from myorm import Model, StringField, BooleanField, FloatField, TextField


#自动生成主键,在uuid算法的基础上生成一个长度为50字节的字符串id,以确保主键的唯一性
def next_id():
	return '%015d%s000' % (int(time.time()*1000), uuid.uuid4().hex)


#用户数据类
class User(Model):

	__table__ = 'users'

	id = StringField(column_type='varchar(50)', primary_key=True, default=next_id)  #主键
	email = StringField(column_type='varchar(50)')  #电子邮箱地址
	passwd = StringField(column_type='varchar(50)')  #密码
	admin = BooleanField()  #是否管理员
	name = StringField(column_type='varchar(50)')  #昵称
	image = StringField(column_type='varchar(500)')  #头像
	created_at = FloatField(default=time.time)  #账户创建时间


#日志数据类
class Blog(Model):

	__table__ = 'blogs'

	id = StringField(column_type='varchar(50)', primary_key=True, default=next_id)  #主键
	user_id = StringField(column_type='varchar(50)')  #用户id
	user_name = StringField(column_type='varchar(50)')  #用户昵称
	user_image = StringField(column_type='varchar(500)')  #用户头像
	title = StringField(column_type='varchar(50)')  #日志标题
	summary = StringField(column_type='varchar(200)')  #日志摘要
	content = TextField()  #日志内容
	created_at = FloatField(default=time.time)  #日志创建时间


#评论数据类
class Comment(Model):

	__table__ = 'comments'

	id = StringField(column_type='varchar(50)', primary_key=True, default=next_id)  #主键
	blog_id = StringField(column_type='varchar(50)')  #日志id
	user_id = StringField(column_type='varchar(50)')  #用户id
	user_name = StringField(column_type='varchar(50)')  #用户昵称
	user_image = StringField(column_type='varchar(500)')  #用户头像
	content = TextField()  #评论内容
	created_at = FloatField(default=time.time)  #评论创建时间

		
