# coding=utf-8
import os, re, sys, time
import sublime, sublime_plugin
import base64, thread, functools, subprocess

'''
/**************************************************
 * MingyuanTech --> 深圳市明元科技有限公司
 * 源代码版权由本公司拥有
 * 联系电话：0755 - 83628658	0755 - 83630858
 * 网址：www.MingyuanTech.com.cn
 * 公司地址：深圳市福田区南园路玉田大厦7C~7D
**************************************************/
'''

# 当前脚本的文件全路径 和 当前脚本的路径
SCRIPT_FILE = os.path.realpath(__file__);	SCRIPT_DIR = os.path.dirname(SCRIPT_FILE);

# 存储一个强行显示本插件右键菜单的列表
ShowContextList = []

execfile(SCRIPT_DIR+os.sep+'PHPTools_menu.json')

# 检测操作系统
if os.name == "nt":
	phpCB      = SCRIPT_DIR+'\lib\phpCB.exe'
	phpExec    = SCRIPT_DIR+'\lib\php.exe'
	phpStylist = SCRIPT_DIR+'\lib\phpStylist.php'
else:
	phpCB = SCRIPT_DIR+os.sep+'/lib/phpCB'
	phpExec = '/usr/bin/php'
	phpStylist = SCRIPT_DIR+os.sep+'/lib/phpStylist.php'

class AsyncProcess(object):
	'''
	@ 插件名：AsyncProcess		 --> 作者：Dandy.Mu
	@ 类说明：执行命令，并使用多线程来获取结果
	@ 谱写日期：2013-12-16 13:36:48
	'''
	def __init__(self, execCmd, on_data, on_finished):
		proc_env = os.environ.copy()
		proc_env.update({})

		self.on_data = on_data;	self.on_finished = on_finished;

		for k, v in proc_env.iteritems():
			proc_env[k] = os.path.expandvars(v).encode(sys.getfilesystemencoding())

		startupinfo = None
		if os.name == "nt":
			startupinfo = subprocess.STARTUPINFO()
			startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

		self.proc = subprocess.Popen(execCmd, stdout=subprocess.PIPE,stderr=subprocess.PIPE, startupinfo=startupinfo, env=proc_env, shell=False)

		if self.proc.stdout:
			thread.start_new_thread(self.read_stdout, ())

		if self.proc.stderr:
			thread.start_new_thread(self.read_stderr, ())

	def read_stdout(self):
		while True:
			data = os.read(self.proc.stdout.fileno(), 2**15)

			if data != "":
				if self.on_data:
					self.on_data(data)
			else:
				self.proc.stdout.close()
				if self.on_finished:
					self.on_finished(self)
				break

	def read_stderr(self):
		while True:
			data = os.read(self.proc.stderr.fileno(), 2**15)

			if data != "":
				if self.on_data:
					self.on_data(self, data)
			else:
				self.proc.stderr.close()
				break

class PhptoolsCommand(sublime_plugin.TextCommand):
	'''
	@ 插件名：Phptools		 --> 作者：Dandy.Mu
	@ 类说明：PHP的扩展IDE功能
	@ 谱写日期：2013-12-16 13:36:48
	'''
	def run(self, edit, iDe = None, Type = None):
		global PHPTOOLSMENU

		self.edit = edit;

		self.Menu = PHPTOOLSMENU[:];

		# 得到当前窗口的对象
		self.window = sublime.active_window();

		if iDe == "Syntax":
			
			self.Syntax();							# 语法检测
		
		elif iDe == "execScript":
			
			self.execScript(Type);					# 执行文件
		
		elif iDe == "Stylist":
			
			self.Stylist(Type);						# 格式化代码
		
		elif iDe == "ShowContext":
			self.ShowContext();						# 显示右键菜单

		else:
			
			self.Show_menu();						# 显示选择窗口

		pass

	def ShowContext(self):
		'''
		@ 函数名：ShowContext		 --> 作者：Dandy.Mu
		@ 函数说明：强行在右键菜单中显示本插件的功能，基本上可以是非PHP文件或者说非PHP的语法编辑
		@ 谱写日期：2013-12-18 15:34:23
		'''
		global ShowContextList

		oFile = self.view.file_name()

		ShowContextList.append(oFile);			# 将当前文件加入到可显示菜单的文件列表

		# print list(set(ShowContextList))

		return sublime.message_dialog('启用成功喽，再点击右键看下有木有!'.decode('utf-8'));

		pass

	def Show_menu(self):
		'''
		@ 函数名：Show_menu		 --> 作者：Dandy.Mu
		@ 函数说明：显示一个菜单
		@ 谱写日期：2013-12-16 13:36:48
		'''
		# 加载默认菜单
		self.Menu = self.Menu if len(self.Menu) >= 1 else PHPTOOLSMENU;

		self.Display_menu = []
		
		for Index in self.Menu: self.Display_menu.append(Index['NAME'].decode('utf-8'));

		# 发起一个选择提示
		self.window.show_quick_panel(self.Display_menu, self.on_done)

		pass

	def Is_save(self):
		'''
		@ 函数名：Is_save		 --> 作者：Dandy.Mu
		@ 函数说明：检测当前文件是否已经保存
		@ 谱写日期：2013-12-17 10:37:59
		'''

		self.FILE = None

		# 当前文件的对象
		self.FILE = self.view.file_name()

		# 检测文件是否存在，也就是说文件是否已经创建，语法检测和运行的时候需要用到
		if not os.path.exists(self.FILE):
			if sublime.ok_cancel_dialog('搞不了, 是不是还没有保存文件啊?\n现在保存不?'.decode('utf-8')):
				self.view.run_command('save')
			else:
				return sublime.status_message('你吖不保存，偶搞不了!'.decode('utf-8'))

		# 检测当前文件是否已经保存
		if self.view.is_dirty():
			if sublime.ok_cancel_dialog("当前文件未保存, 是否现在保存当前文件?.".decode('utf-8')):
				self.view.run_command('save')
			else:
				return sublime.status_message('文件未保存取消检测！'.decode('utf-8'))

		# 检测扩展名是否为PHP
		if not self.FILE[-3:] == 'php':
			if not sublime.ok_cancel_dialog("当前文件可能不是PHP文件, 是否要继续执行?".decode('utf-8')):
				return sublime.status_message('取消非PHP文件的语法检测!'.decode('utf-8'))

		return self.FILE;
		pass

	def Get_Select(self):
		'''
		@ 函数名：Get_Select		 --> 作者：Dandy.Mu
		@ 函数说明：获取选择的内容
		@ 谱写日期：2013-12-16 18:38:52
		'''
		View = self.view;
		
		Sel = View.sel();										# 获取当前的选择对象

		# 声明一下当前使用的选区
		self.oBegin = Sel[0].b;	self.oEnd = Sel[0].a;

		return self.Get();

		pass

	def Get_Lines(self):
		'''
		@ 函数名：Get_Lines		 --> 作者：Dandy.Mu
		@ 函数说明：获取选择的行的内容
		@ 谱写日期：2013-12-16 18:38:52
		'''
		View = self.view;									# 视图对象

		oRegion = sublime.Region;							# 选区对象
		
		Sel = View.sel();									# 获取当前的选择对象

		Line_nums = [View.rowcol(line.a)[0] for line in View.lines(Sel[0])];					# 获取当前选择区域的行列表

		self.oBegin = oRegion.begin(View.line(View.text_point(Line_nums[0], 0)))						# 选中区域的起始位置
		self.oEnd   = oRegion.end(View.line(View.text_point(Line_nums[len(Line_nums) -1 ], 0)))		# 选中区域的结束位置

		return self.Get();
		
		pass

	def Get_Full(self):
		'''
		@ 函数名：Get_Full		 --> 作者：Dandy.Mu
		@ 函数说明：获取当前文档的所有内容
		@ 谱写日期：2013-12-17 10:32:32
		'''
		# 声明一下当前使用的选区
		self.oBegin = 0;	self.oEnd = self.view.size();

		return self.Get();

		pass

	def Get(self, oBegin = None, oEnd = None):

		oBegin = oBegin if oBegin != None else self.oBegin;
		
		oEnd = oEnd if oEnd != None else self.oEnd;

		# 创建一个选区，也就是当前文件的所有内容
		oRegion = sublime.Region(oBegin, oEnd);

		# 当前选区中的内容
		oContent = self.view.substr(oRegion).encode('utf-8');

		return oContent;

		pass

	def Replace(self, edit, Content, oBegin = None, oEnd = None):
		'''
		@ 函数名：Replace		 --> 作者：Dandy.Mu
		@ 函数说明：替换当前选区的内容
		@ 谱写日期：2013-12-17 10:53:16
		'''
		Content = Content.decode('utf-8') if len(Content) else Content;

		oBegin = oBegin if oBegin != None else self.oBegin;
		oEnd = oEnd if oEnd != None else self.oEnd;

		# 创建一个选区，也就是当前文件的所有内容
		oRegion = sublime.Region(oBegin, oEnd)
		
		# 执行替换操作
		self.view.replace(edit, oRegion, re.sub(r'\r\n|\r', '\n', Content))
		
		pass

	# 语法检测
	def Syntax(self):
		'''
		@ 函数名：Syntax		 --> 作者：Dandy.Mu
		@ 函数说明：语法检测
		@ 谱写日期：2013-12-18 13:09:56
		'''

		if not self.Is_save(): return False;			# 检测文件是否已经保存

		self.window.run_command("exec", {"cmd": [phpExec, "-l", self.FILE]})
		
		pass

	# 执行文件
	def execScript(self, Type = None):
		'''
		@ 函数名：execScript		 --> 作者：Dandy.Mu
		@ 函数说明：执行文件
		@ 谱写日期：2013-12-18 13:18:51
		'''
		self.execScriptData = [];		# 声明返回数据
		if Type == None:
			if not self.Is_save(): return False;									# 检测文件是否已经保存
			self.window.run_command("exec", {"cmd": [phpExec, "-f", self.FILE]});	# 执行PHP文件
			return True
		elif Type == "Lines":
			Content = base64.b64encode(self.Get_Lines());							# 获取选择的行的内容
			self.window.run_command("exec", {"cmd": [phpExec, "-r", "$execContent = '"+Content+"'; include '"+phpStylist+"';"]});	# 执行脚本
			return True
		elif Type == "Select":
			Content = base64.b64encode(self.Get_Select());							# 获取选择的行的内容
			self.window.run_command("exec", {"cmd": [phpExec, "-r", "$execContent = '"+Content+"'; include '"+phpStylist+"';"]});	# 执行脚本
			return True
		pass

	def execScript_On_data(self, retData):
		sublime.set_timeout(functools.partial(self.Output_info, retData.decode('utf-8')), 0)
		pass

	def execScript_On_finished(self, proc):
		pass

	# 代码格式化
	def Stylist(self, Type = None):
		'''
		@ 函数名：Stylist		 --> 作者：Dandy.Mu
		@ 函数说明：代码格式化
		@ 谱写日期：2013-12-18 13:37:31
		'''

		if Type == None:
			Content = base64.b64encode(self.Get_Full());		# 获取当前视图的所有的内容
		elif Type == "Lines":
			Content = base64.b64encode(self.Get_Lines());		# 获取选择的行的内容
		elif Type == "Select":
			Content = base64.b64encode(self.Get_Select());		# 获取选中的字符

		if not len(Content): return False;						# 检测一下获取到的内容是不是空的

		self.phpStylistData = [];		# 声明返回数据

		AsyncProcess([phpExec, "-r", "$Content = '"+Content+"'; include '"+phpStylist+"';"], self.Stylist_on_data, self.Stylist_on_finished)

		pass

	# 接收Stylist格式化后的代码
	def Stylist_on_data(self, data):
		self.phpStylistData.append(data)
		pass

	# 替换Stylist格式化的代码为格式化后的
	def Stylist_on_finished(self, proc):
		for Index in self.phpStylistData:
			sublime.set_timeout(functools.partial(self.Replace, self.edit, Index), 0)
		pass

	def on_done(self, select):
		'''
		@ 函数名：on_done		 --> 作者：Dandy.Mu
		@ 函数说明：判断选择的菜单项，应该执行什么动作，要扩展什么动作的话，也是在这里。
		@ 谱写日期：2013-12-16 15:33:56
		'''
		if select == -1: return;

		self.Select_menu = self.Menu[select];			# 存储当前选择菜单

		if self.Select_menu['TYPE'] == 'MENU':
			self.Parent_menu = self.Menu[:];				# 存储一个父级菜单
			self.Menu = self.Select_menu['MENU'];
			self.Show_menu();
			return;
		elif self.Select_menu['TYPE'] == 'JUMP':
			self.Menu = self.Parent_menu[:];
			self.Show_menu();
			return;
		elif self.Select_menu['TYPE'] == 'CLASS':
			self.view.run_command(self.Select_menu['CLASS'], self.Select_menu['ARGS'])
			return;
			pass

		pass

	# 控制右键菜单的显示
	def is_visible(self, **args):
		global ShowContextList

		oFile = self.view.file_name()
		oFile = oFile if oFile != None else 'Error'
		Syntax = os.path.splitext(self.view.settings().get('syntax'))[0].split('/')[-1].upper()
		oShow = oFile in ShowContextList

		if oShow == True: Syntax = "PHP";						# 忽悠一下自己，打开插件的右键菜单

		if oFile[-3:].upper() != "PHP" and Syntax != "PHP":
			if 'iDe' in args and args['iDe'] == "ShowContext":
				return True
			else:
				return False

		elif oFile[-3:].upper() == "PHP" or Syntax == "PHP":
			if 'iDe' in args and args['iDe'] == "ShowContext":
				return False				
		 	else:
		 		return True
		else:
			return True

	def is_enabled(self, **args):
		if "Type" in args and args["Type"] == "Select":
			if len(self.Get_Select()) > 0:
				return True
			else:
				return False
		
		return True
