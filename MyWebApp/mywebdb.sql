
drop database if exists mywebdb;  #如果已经存在同名数据库就先删除掉

create database mywebdb;  #创建名为'mywebdb'的数据库

use mywebdb;  #对数据库中的表进行操作前必须先use所属数据库名

#给不是管理员的账号分配操作权限(此处分配给某个账号分配了对mywebdb数据库中所有表的增删改查权限,无建表和删表等其他权限)
#grant select, insert, update, delete on mywebdb.* to 'root'@'localhost' identified by '1234';  #管理员账户默认有最高权限


create table users(
	'id' varchar(50) not null,  #用户id
	'email' varchar(50) not null,  #电子邮箱
	'passwd' varchar(50) not null,  #账户密码
	'admin' bool not null,  #是否管理员
	'name' varchar(50) not null,  #用户昵称
	'image' varchar(500) not null,  #用户头像
	'created_at' real not null,  #注册时间
	unique key 'idx_email' ('email'),  #邮箱不能重复
	key 'idx_created_at' ('created_at'),  #key暂不清楚作用
	primary key ('id')  #主键
) engine=innodb default charset=utf8;  #数据驱动以及编码格式


create table blogs(
	'id' varchar(50) not null,  #日志id
	'user_id' varchar(50) not null,  #发表日志的用户id
	'user_name' varchar(50) not null,  #发表日志的用户昵称
	'user_image' varchar(500) not null,  #发表日志的用户头像
	'title' varchar(50) not null,  #日志标题
	'summary' varchar(200) not null,  #日志摘要
	'content' mediumtext not null,  #日志内容
	'created_at' real not null,  #日志发表时间
	key 'idx_created_at' ('created_at'),
	primary key ('id')  #主键
) engine=innodb default charset=utf8;


create table comments(
	'id' varchar(50) not null,  #评论id
	'blog_id' varchar(50) not null,  #评论所针对的日志id
	'user_id' varchar(50) not null,  #发表评论的用户id
	'user_name' varchar(50) not null,  #发表评论的用户昵称
	'user_image' varchar(500) not null,  #发表评论的用户头像
	'content' mediumtext not null,  #评论内容
	'created_at' real not null,  #评论发表时间
	key 'idx_created_at' ('created_at'),
	primary key ('id')  #主键
) engine=innodb default charset=utf8;