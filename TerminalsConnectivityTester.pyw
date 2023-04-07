#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import yaml, json, csv, time
from tkinter import messagebox, simpledialog, filedialog
from ping3 import ping
from AppUI import *
from SqlDump import *

class Main(AppUI):
	# The class implements callback function for events and logical code.

	TERMINALS_FILE = ""					# 当前文件名
	TERMINALS_DICT = {}					# 当前字典

	TIMEOUT = 0.2						# 测试超时，单位s
	SLOWMOD = 0.05						# 慢速延时，单位s

	def __init__(self, master=None):
		self.loadConfigs()				# 加载外部配置文件
		AppUI.__init__(self, master)	# 初始化UI

	###############
	## CoreFuncs ##
	###############

	def loadConfigs(self):
		#* 加载外部配置文件 *#
		global root
		try:
			configFile = open('config.yaml', 'r')
			configDict = yaml.safe_load(configFile)
			configFile.close()

			## SqlDump Configurations ##
			SqlDump.DBHOST = str(configDict['database']['host'])
			SqlDump.DBPORT = int(configDict['database']['port'])
			SqlDump.DBUSER = str(configDict['database']['username'])
			SqlDump.DBPASS = str(configDict['database']['password'])
			for dept in configDict['departments']:
				newDept = {'name': dept, 'dbs': configDict['departments'][dept]}
				SqlDump.DEPTS.append(newDept)
			SqlDump.DUMPCODES = configDict['dumpcodes']

			## AppUI Configurations ##
			AppUI.DEPTS = tuple(configDict['departments'].keys())
			for column in configDict['columns']:
				AppUI.COLUMNS[column] = [
					configDict['columns'][column]['fullname'],
					configDict['columns'][column]['width'],
					tk.CENTER, True]
			AppUI.COLUMNS['#0'][3] = False
			AppUI.CONFIGHOST = str(configDict['database']['host'])
		except Exception as e:
			root.destroy()	# stops the mainloop and kills the window, but leaves python running
			messagebox.showerror(title="Failed while loading config.yaml", message=str(e))
			exit()			# stops the whole process

	def doOpen(self):
		#* 打开文件主逻辑，更新至全局空间 *#
		fp = open(self.TERMINALS_FILE, 'r')
		fs = fp.read()
		fp.close()
		self.TERMINALS_DICT = json.loads(fs)

	def doSave(self):
		#* 保存文件主逻辑，更新至全局空间 *#
		fp = open(self.TERMINALS_FILE, 'w')
		fp.write(json.dumps(self.TERMINALS_DICT))
		fp.close()

	def setFile(self, file):
		#* 设置 TERMINALS_FILE *#
		self.TERMINALS_FILE = file
		if file == "":
			AppUI.updateTitle(self, "untitled*")
		else:
			AppUI.updateTitle(self, self.TERMINALS_FILE.split('/')[-1])

	def getFile(self):
		#* 获取 TERMINALS_FILE *#
		return self.TERMINALS_FILE

	def setDict(self, dict):
		#* 设置 TERMINALS_DICT *#
		self.TERMINALS_DICT = dict

	def getDict(self, filtered=False):
		#* 获取 TERMINALS_DICT *#
		if not filtered: return self.TERMINALS_DICT		# 默认不过滤，直接返回全局字典
		filteredDict = self.TERMINALS_DICT.copy()		# 深拷贝，不改变全局字典
		if not self.FL_NORMAL.get():					# 过滤掉测试正常项
			filteredDict['terminals'] = list(filter(lambda x: not x['latency'].replace('.', '', 1).isdigit(), filteredDict['terminals']))
		if not self.FL_TIMEOUT.get():					# 过滤掉测试超时项
			filteredDict['terminals'] = list(filter(lambda x: x['latency'] != 'Timeout', filteredDict['terminals']))
		if not self.FL_UNKNOWN.get():					# 过滤掉未知主机项
			filteredDict['terminals'] = list(filter(lambda x: x['latency'] != 'Unknown', filteredDict['terminals']))
		if not self.FL_UNTESTED.get():					# 过滤掉未测试项
			filteredDict['terminals'] = list(filter(lambda x: x['latency'] != 'Untested', filteredDict['terminals']))
		return filteredDict

	###############
	## Callbacks ##
	###############

	def onOpenClicked(self, event=None):
		#* 打开文件事件响应 *#
		fn = filedialog.askopenfilename(
			title='Select a terminals report (.json) file',
			filetypes=[('JSON', '*.json'), ('All Files', '*')],
			initialdir='.')								# 对话框选择文件，返回文件名
		if fn == "": return								# 取消则直接返回
		try:
			self.setFile(fn)							# 更新全局文件名
			self.doOpen()								# 加载至全局空间
			AppUI.loadFromDict(self, self.getDict())	# 更新TreeView
		except Exception as e:							# 提示加载文件错误
			AppUI.updateInfoBar(self, 'Failed: {}'.format(e))
			self.setFile("")							# 清空全局文件名
			self.setDict({})
			AppUI.resetNodeItems(self)					# 刷新节点字典
		else:
			AppUI.resetFilters(self)					# 重置筛选器
			AppUI.updateInfoBar(self, 'File loaded.')	# 更新InfoBar
		finally:
			AppUI.enableMenuBar(self, True)				# 取消禁用菜单栏

	def onSaveClicked(self, event=None):
		#* 保存文件事件响应 *#							# 空字典跳过事件
		if self.getDict() == {}: return AppUI.updateInfoBar(self, 'Failed: Empty Dictionary.')
		if self.getFile() == "":
			self.onSaveAsClicked()						# 无文件名转到另存为事件
		else:
			self.doSave()								# 从全局空间保存
			AppUI.updateInfoBar(self, 'File Saved.')	# 更新InfoBar

	def onSaveAsClicked(self, event=None):
		#* 另存为文件事件响应 *#							# 空字典跳过事件
		if self.getDict() == {}: return AppUI.updateInfoBar(self, 'Failed: Empty Dictionary.')
		fn = filedialog.asksaveasfilename(
			title='Select a directory to save terminals report',
			filetypes=[('JSON', '*.json'), ('All Files', '*')],
			defaultextension='.json',
			initialfile='terminals-{}'.format(time.strftime('%Y%m%d-%H%M%S',time.localtime(time.time()))),
			initialdir='.')								# 对话框输入文件名，返回文件名
		if fn == "": return								# 取消则直接返回
		self.setFile(fn)								# 更新全局文件名
		self.doSave()									# 从全局空间保存
		AppUI.updateInfoBar(self, 'File Saved.')		# 更新InfoBar

	def onImportClicked(self):
		#* 导入文件事件响应 *#
		try:
			fn = filedialog.askopenfilename(
				title='Select a terminals report (.csv) file',
				filetypes=[('CSV', '*.csv'), ('All Files', '*')],
				initialdir='.')							# 对话框选择文件，返回文件名
			if fn == "": return							# 取消则直接返回
			csvFile = open(fn, 'r', newline='')
			reader = csv.DictReader(csvFile)
			termCount = 0
			self.getDict()['terminals'] = []
			for row in reader:
				self.getDict()['terminals'].append(row)
				termCount += 1
			csvFile.close()
			self.getDict()["updateTime"] = int(time.time())	# 更新时间
			self.getDict()["terminalsCount"] = termCount	# 终端总数
			self.setFile("")							# 清空全局文件名
			AppUI.loadFromDict(self, self.getDict())	# 更新TreeView
		except Exception as e:							# 提示错误信息
			AppUI.updateInfoBar(self, 'Failed: {}'.format(e))
		else:
			AppUI.resetFilters(self)					# 重置筛选器
			AppUI.updateInfoBar(self, 'File Imported.')	# 更新InfoBar
		finally:
			AppUI.enableMenuBar(self, True)				# 取消禁用菜单栏

	def onExportClicked(self):
		#* 导出文件事件响应 *#							# 空字典跳过事件
		if self.getDict() == {}: return AppUI.updateInfoBar(self, 'Failed: Empty Dictionary.')
		try:
			fieldnames = list(self.getDict()['terminals'][0].keys())
			fn = filedialog.asksaveasfilename(
				title='Select a directory to export terminals report as csv',
				filetypes=[('CSV', '*.csv'), ('All Files', '*')],
				defaultextension='.csv',
				initialfile='terminals-{}'.format(time.strftime('%Y%m%d-%H%M%S',time.localtime(time.time()))),
				initialdir='.')							# 对话框输入文件名，返回文件名
			if fn == "": return							# 取消则直接返回
			csvFile = open(fn, 'w', newline='')
			writer = csv.DictWriter(csvFile, fieldnames=fieldnames)
			writer.writeheader()						# 写入表头
			for term in self.getDict()['terminals']:	# 遍历写入terminals信息
				writer.writerow(term)
			csvFile.close()
		except Exception as e:							# 提示错误信息
			AppUI.updateInfoBar(self, 'Failed: {}'.format(e))
		else:
			AppUI.updateInfoBar(self, 'File Exported.')	# 更新InfoBar
		finally:
			AppUI.enableMenuBar(self, True)				# 取消禁用菜单栏

	def onFilterChanged(self):
		#* 改变过滤器事件响应 *#							# 空字典跳过事件
		if self.getDict() == {}: return AppUI.updateInfoBar(self, 'Failed: Empty Dictionary.')
		try:
			AppUI.loadFromDict(self, self.getDict(filtered=True))
		except Exception as e:							# 提示错误信息
			AppUI.updateInfoBar(self, 'Failed: {}'.format(e))
		else:
			AppUI.updateInfoBar(self, 'List Filtered.')	# 更新InfoBar
		finally:
			AppUI.enableMenuBar(self, True)				# 取消禁用菜单栏

	def onDumpClicked(self, event=None, specify=False, host=None):
		#* 下载数据库事件响应 *#
		if specify:
			host = simpledialog.askstring(title='Dump from server', prompt = 'Please specify the server IP:')
			if host == None or host == '': return		# 取消则直接返回
		AppUI.enableMenuBar(self, False)				# 事件中禁用菜单栏防止误操作
		try:
			self.setDict(SqlDump.dump(dbhost=host))		# 封装的SqlDump类
			AppUI.loadFromDict(self, self.getDict())	# 更新TreeView
		except Exception as e:							# 提示错误信息
			AppUI.updateInfoBar(self, 'Failed: {}'.format(e))
		else:
			AppUI.resetFilters(self)					# 重置筛选器
			AppUI.updateInfoBar(self, 'Dumped.')		# 更新InfoBar
		finally:
			AppUI.enableMenuBar(self, True)				# 取消禁用菜单栏

	def onTestClicked(self, event=None, slowmode=False):
		#* 测试终端事件响应 *#							# 空字典跳过事件
		if self.getDict() == {}: return AppUI.updateInfoBar(self, 'Failed: Empty Dictionary.')
		AppUI.enableMenuBar(self, False)				# 事件中禁用菜单栏防止误操作
		try:
			totalCount    = self.getDict()['terminalsCount']# 终端总数
			progressCount = 0							# 测试进度计数

			for term in self.getDict()['terminals']:	# 遍历测试
				progressCount += 1
				AppUI.updateInfoBar(self, 'Testing {} of {} ...'.format(progressCount, totalCount))
				if slowmode:							# 慢速测试添加延迟
					time.sleep(self.SLOWMOD)
				if term['ip'] == "": continue			# 空地址，跳过
				try:
					latency = ping(term['ip'], timeout = self.TIMEOUT, unit='ms')
				except:
					term['latency'] = 'Unknown'
					continue							# 非法地址，跳过
				if not isinstance(latency, float):		# 测试异常，进行4次慢速测试
					for i in ('1st', '2nd', '3rd', '4th'):
						AppUI.updateInfoBar(self, 'Testing {} of {} Failed! Retry for {} time ...'.format(progressCount, totalCount, i))
						time.sleep(0.5)
						latency = ping(term['ip'], timeout = self.TIMEOUT, unit='ms')
						if isinstance(latency, float): break	#成功，跳出重试循环
					if latency == None:
						term['latency'] = 'Timeout'
						continue						# 测试超时，跳过
					elif latency == False:
						term['latency'] = 'Unknown'
						continue						# 未知主机，跳过
				term['latency'] = '{:.3f}'.format(latency)	# 否则，保存测试结果，单位毫秒，保留3位

			self.getDict()["updateTime"] = int(time.time())	# 更新时间
			AppUI.loadFromDict(self, self.getDict())		# 更新TreeView
		except Exception as e:							# 提示错误信息
			AppUI.updateInfoBar(self, 'Failed: {}'.format(e))
		else:
			AppUI.resetFilters(self)					# 重置筛选器
			AppUI.updateInfoBar(self, 'Finish, {} terminals tested.'.format(progressCount))
		finally:
			AppUI.enableMenuBar(self, True)				# 取消禁用菜单栏

	def onAboutClicked(self, event=None):
		rights = AppUI._appRights[0] + ' ' + AppUI._appRights[1] + ', ' + AppUI._appRights[2]
		aboutMessage = AppUI._appTitle + '\nVersion: ' + AppUI._appVersion + '\n' + rights
		return messagebox.showinfo(title='About '+AppUI._appTitle, message=aboutMessage)

if __name__ == '__main__':
	root = tk.Tk()
	Main(root).mainloop()	# 事件循环