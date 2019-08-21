
drop database if exists mywebdb;  #如果已经存在同名数据库就先删除掉

create database mywebdb;  #创建名为'mywebdb'的数据库

use mywebdb;  #对数据库中的表进行操作前必须先use所属数据库名

#给不是管理员的账号分配操作权限(此处分配给某个账号分配了对mywebdb数据库中所有表的增删改查权限,无建表和删表等其他权限)
#grant select, insert, update, delete on mywebdb.* to 'root'@'localhost' identified by '1234';  #管理员账户默认有最高权限

#创建'用户表'
create table users (
	`id` varchar(50) not null comment '用户id',
	`email` varchar(50) not null comment '用户邮箱',
	`passwd` varchar(50) not null comment '账户密码',
	`admin` bool not null comment '是否管理员',
	`name` varchar(50) not null comment '用户昵称',
	`image` varchar(500) not null comment '用户头像',
	`created_at` real not null comment '账户创建时间',
	unique key `idx_email` (`email`) comment '唯一索引,值不可重复(除null外)',
	key `idx_created_at` (`created_at`) comment '普通单列索引,索引的作用是该列作为查询条件时可以加快查询速度',
	primary key (`id`) comment '主键'
) engine=innodb default charset=utf8;

#创建'日志表'
create table blogs (
	`id` varchar(50) not null comment '日志id',
	`user_id` varchar(50) not null comment '发表日志的用户id',
	`user_name` varchar(50) not null comment '发表日志的用户昵称',
	`user_image` varchar(500) not null comment '发表日志的用户头像',
	`title` varchar(50) not null comment '日志标题',
	`summary` varchar(200) not null comment '日志摘要',
	`content` mediumtext not null comment '日志内容',
	`created_at` real not null comment '日志发表时间',
	key `idx_created_at` (`created_at`) comment '单列索引',
	primary key (`id`) comment '主键'
) engine=innodb default charset=utf8;

#创建'评论表'
create table comments (
	`id` varchar(50) not null comment '评论id',
	`blog_id` varchar(50) not null comment '所针对的日志id',
	`user_id` varchar(50) not null comment '发表评论的用户id',
	`user_name` varchar(50) not null comment '发表评论的用户昵称',
	`user_image` varchar(500) not null comment '发表评论的用户头像',
	`content` mediumtext not null comment '评论内容',
	`created_at` real not null comment '评论发表时间',
	key `idx_created_at` (`created_at`) comment '单列索引',
	primary key (`id`) comment '主键'
) engine=innodb default charset=utf8;