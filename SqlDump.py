#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pymysql, time

class SqlDump():
	# The class implements SqlDump functions.

	DBHOST = "localhost"
	DBPORT = 3306
	DBUSER = "root"
	DBPASS = "123456"

	DEPTS = []
	# eg:
	# DEPTS = [
	# 	{ "name": "A", "dbs": ["a1", "a2", "a3"]},
	# 	{ "name": "B", "dbs": ["b1"]			}
	# ]

	DUMPCODES = {}
	# eg:
	# DUMPCODES = {
	# 	"typeA": "SELECT name, ip, line FROM ainfo",
	# 	"typeB": "SELECT name, ip, line FROM binfo"
	# }

	DUMPCOUNT = 0

	DUMP = {}

	@classmethod
	def refresh(cls):
		cls.DUMP = {
			"updateTime"    : 0,
			"terminalsCount": 0,
			"terminals"     : []
		}

	@classmethod
	def dumpProcess(cls, dumpcursor, dumpcode, dumpdept, dumptype):
		dumpcursor.execute(dumpcode)			# 使用 execute() 方法执行SQL语句
		terminalsInfo = dumpcursor.fetchall()	# 使用 fetchall() 方法获取所有数据

		for info in terminalsInfo:				# 遍历完善信息并添加至 DUMP["terminals"] 列表
			info["dept"] = dumpdept
			info["type"] = dumptype
			info["latency"] = "Untested"
			cls.DUMP["terminals"].append(info)
			cls.DUMPCOUNT += 1

	@classmethod
	def dump(cls, dbhost=DBHOST, dbport=DBPORT, dbuser=DBUSER, dbpass=DBPASS):
		cls.refresh()
		dbhost = cls.DBHOST if dbhost == None else dbhost
		for dept in cls.DEPTS:
			for dbName in dept["dbs"]:
				dbConn = pymysql.connect(host=dbhost, port=dbport, user=dbuser, password=dbpass, db=dbName)
				cursor = dbConn.cursor(pymysql.cursors.DictCursor)	# cursor()方法获取操作游标，返回字典格式

				for dumptype in cls.DUMPCODES:
					cls.dumpProcess(cursor, cls.DUMPCODES[dumptype], dept["name"], dumptype)

				## 关闭数据库连接 ##
				cursor.close()
				dbConn.close()
		cls.DUMP["updateTime"] = int(time.time())	# 更新时间
		cls.DUMP["terminalsCount"] = cls.DUMPCOUNT	# 终端总数
		return cls.DUMP