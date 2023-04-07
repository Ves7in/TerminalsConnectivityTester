#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import tkinter as tk
from tkinter import ttk, Frame, font

class AppUI(Frame):
	# The class will create all widgets for UI.
	DEPTS = ()
	# eg:
	# DEPTS = ('deptA', 'deptB')

	COLUMNS = {}
	# eg:
	# COLUMNS = {
	# 	'#0'     : ['Department', 140, tk.CENTER, False],
	# 	'latency': ['Latency'   , 100, tk.CENTER, True ]
	# }

	TG_DEPT     = 'tg_dept'
	TG_NORMAL   = 'tg_normal'
	TG_TIMEOUT  = 'tg_timeout'
	TG_UNKNOWN  = 'tg_unknown'
	TG_UNTESTED = 'tg_untested'

	TREEITEMS = {}

	CONFIGHOST = ""

	_appTitle   = 'TerminalsConnectivityTester'
	_appVersion = '0.2.3'
	_appRights  = ['2023', 'Vestin', 'All rights reserved.']

	def __init__(self, master=None):
		Frame.__init__(self, master)
		s = ttk.Style()
		s.theme_use('alt')

		self.FL_NORMAL   = tk.BooleanVar()
		self.FL_TIMEOUT  = tk.BooleanVar()
		self.FL_UNKNOWN  = tk.BooleanVar()
		self.FL_UNTESTED = tk.BooleanVar()

		# Create widgets
		self.createWidgets()			# 创建控件
		self.initWidgets()				# 初始化控件
		self.resetFilters()				# 重置筛选器
		self.resetNodeItems()			# 刷新节点字典

		# Get everything ready
		master.title(self._appTitle + ' v' + self._appVersion)
		master.update()
		# 宽度自适应，高度调整为450
		master.geometry('{}x450'.format(master.winfo_width()))

	def createWidgets(self):
		#* 创建控件 *#
		self.root = self.winfo_toplevel()

		## 初始化创建菜单栏 ##
		self.menubar = tk.Menu(self.root)

		mnuFile = tk.Menu(self.menubar, tearoff=0)  # File 下拉菜单
		self.menubar.add_cascade(label='File', menu=mnuFile)
		mnuFile.add_command(label='Open ...', command=self.onOpenClicked)
		mnuFile.add_command(label='Save', command=self.onSaveClicked)
		mnuFile.add_command(label='Save as ...', command=self.onSaveAsClicked)
		mnuFile.add_separator() # 分隔线
		mnuFile.add_command(label='Import ...', command=self.onImportClicked)
		mnuFile.add_command(label='Export ...', command=self.onExportClicked)
		mnuFile.add_separator() # 分隔线
		mnuFile.add_command(label='Quit', command=self.quit)

		mnuFilter = tk.Menu(self.menubar, tearoff=0)  # Filter 下拉菜单
		self.menubar.add_cascade(label='Filter', menu=mnuFilter)
		mnuFilter.add_checkbutton(label = "Normal", variable = self.FL_NORMAL, command=self.onFilterChanged)
		mnuFilter.add_checkbutton(label = "Timeout", variable = self.FL_TIMEOUT, command=self.onFilterChanged)
		mnuFilter.add_checkbutton(label = "Unknown", variable = self.FL_UNKNOWN, command=self.onFilterChanged)
		mnuFilter.add_checkbutton(label = "Untested", variable = self.FL_UNTESTED, command=self.onFilterChanged)

		mnuDb = tk.Menu(self.menubar, tearoff=0)  # Database 下拉菜单
		self.menubar.add_cascade(label='Database', menu=mnuDb)
		mnuDb.add_command(label='Dump (Config file)', command=self.onDumpClicked)
		mnuDb.add_command(label='Host: %s' % self.CONFIGHOST, state="disabled")
		mnuDb.add_separator() # 分隔线
		mnuDb.add_command(label='Dump from localhost' , command=lambda: self.onDumpClicked(host='localhost'))
		mnuDb.add_command(label='Dump from remote ...', command=lambda: self.onDumpClicked(specify=True))

		mnuTest = tk.Menu(self.menubar, tearoff=0)  # ConnectivityTest 下拉菜单
		self.menubar.add_cascade(label='ConnectivityTest', menu=mnuTest)
		mnuTest.add_command(label='Run (Performance)' , command=self.onTestClicked)
		mnuTest.add_command(label='Run', command=lambda: self.onTestClicked(slowmode=True))

		mnuAbout = tk.Menu(self.menubar, tearoff=0)  # About 下拉菜单
		self.menubar.add_cascade(label='About', menu=mnuAbout)
		mnuAbout.add_command(label=self._appTitle , command=self.onAboutClicked)
		
		self.root.config(menu=self.menubar)

		## 初始化创建底部信息栏 ##
		self.infoBarVar = tk.StringVar(value='')
		self.infoBar = tk.Label(self.root, textvariable=self.infoBarVar, bd=1, relief=tk.SUNKEN, anchor=tk.W)
		self.infoBar.setText = lambda x: self.infoBarVar.set(x)
		self.infoBar.text = lambda : self.infoBarVar.get()
		self.infoBar.pack(side=tk.BOTTOM, fill=tk.X)

		## 初始化创建垂直滚动条，右对齐，垂直填充 ##
		scrollBar = ttk.Scrollbar(self.root)
		scrollBar.pack(side=tk.RIGHT, fill=tk.Y)

		## 根据COLUMNS初始化创建树表格组件，栏目从COLUMNS键名获取，并忽略'#0' ##
		self.tree = ttk.Treeview(self.root, columns=tuple(self.COLUMNS.keys())[1:], yscrollcommand=scrollBar.set)

		## TreeView尺寸自适应，并绑定垂直滚动条 ##
		self.tree.pack(fill=tk.BOTH,expand=True)
		scrollBar.config(command=self.tree.yview)

	def initWidgets(self):
		#* 初始化控件 *#
		for col in self.COLUMNS:						# 定义表头文字，并设定栏目的宽度，对齐方法，宽度是否随窗体自适应变化
			self.tree.heading(col, text=self.COLUMNS[col][0])
			self.tree.column(col, width=self.COLUMNS[col][1], anchor=self.COLUMNS[col][2], stretch=self.COLUMNS[col][3])
		for dept in self.DEPTS:					# 根据DEPTS初始化TREEITEMS字典，作为后续节点node及计数count容器
			self.TREEITEMS[dept] = {'count': 0}

	def resetFilters(self):
		#* 重置筛选器 *#
		self.FL_NORMAL.set(True)
		self.FL_TIMEOUT.set(True)
		self.FL_UNKNOWN.set(True)
		self.FL_UNTESTED.set(True)

	def resetNodeItems(self):
		#* 刷新节点字典 *#
		for item in self.tree.get_children():	# 清空节点下的所有子项
			self.tree.delete(item)
		for item in self.TREEITEMS:				# 在根节点''下遍历添加子节点，返回节点对象记录到treeItem字典
			self.TREEITEMS[item]['node']  = self.tree.insert('', tk.END, text=item, tags=self.TG_DEPT, open=True)
			self.TREEITEMS[item]['count'] = 0
		self.updateNodeItemsCount()				# 更新显示所有节点的计数信息
		self.updateTagsStyle()					# 更新标签主题

	def updateNodeItemsCount(self):
		#* 更新显示所有节点的计数信息 *#
		for item in self.TREEITEMS:
			self.tree.item(self.TREEITEMS[item]['node'], text=item+' ({})'.format(self.TREEITEMS[item]['count']))

	def updateTagsStyle(self):
		#* 更新标签主题 *#
		self.tree.tag_configure(self.TG_DEPT    , background='#D9D9D9', foreground='#000000', font=font.Font(font=("微软雅黑",10,'italic')))
		self.tree.tag_configure(self.TG_NORMAL  , background='#C6EFCE', foreground='#006100', font=font.Font(font=("微软雅黑",9)))
		self.tree.tag_configure(self.TG_TIMEOUT , background='#FFC7CE', foreground='#9C0006', font=font.Font(font=("微软雅黑",9)))
		self.tree.tag_configure(self.TG_UNKNOWN , background='#FFEB9C', foreground='#9C5700', font=font.Font(font=("微软雅黑",9)))
		self.tree.tag_configure(self.TG_UNTESTED, background='#FFFFFF', foreground='#000000', font=font.Font(font=("微软雅黑",9)))

	def updateInfoBar(self, info):
		#* 更新InfoBar显示消息 *#
		currentTime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
		self.infoBar.setText('[' + currentTime + ']  ' + info)
		self.infoBar.update()

	def updateTitle(self, fn):
		self.root.title(self._appTitle + ' v' + self._appVersion + ' - ' + fn)

	def enableMenuBar(self, enable=True):
		#* 菜单栏使能控制 *#
		if enable:
			self.menubar.entryconfig(2, state=tk.NORMAL)
			self.menubar.entryconfig(3, state=tk.NORMAL)
			self.menubar.entryconfig(4, state=tk.NORMAL)
		else:
			self.menubar.entryconfig(2, state=tk.DISABLED)
			self.menubar.entryconfig(3, state=tk.DISABLED)
			self.menubar.entryconfig(4, state=tk.DISABLED)

	def loadFromDict(self, dict):
		#* 从全局字典加载数据以更新TreeView *#
		self.enableMenuBar(False)				# 过程中禁用菜单栏防止误操作
		self.resetNodeItems()					# 刷新节点字典
		for term in dict['terminals']:			# 遍历获取terminals字典信息，追加行到对应子节点
			termDept   = term['dept']
			termValues = tuple(map(lambda x: term[x], tuple(self.COLUMNS.keys())[1:]))
			if term['latency'] == "Timeout":
				termTag = self.TG_TIMEOUT
			elif term['latency'] == "Unknown":
				termTag = self.TG_UNKNOWN
			elif term['latency'] == "Untested" or term['latency'] == "":
				termTag = self.TG_UNTESTED
			else:
				termTag = self.TG_NORMAL
			self.tree.insert(self.TREEITEMS[termDept]['node'], tk.END, text=termDept, values=termValues, tags=termTag)
			self.TREEITEMS[termDept]['count'] += 1
		self.updateNodeItemsCount()				# 更新显示所有节点的计数信息
		self.updateTagsStyle()					# 更新标签主题
		self.enableMenuBar(True)				# 取消禁用菜单栏
