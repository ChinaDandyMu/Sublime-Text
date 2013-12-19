/**************************************************
 * PHPTools --> Coco 老爸
 * 版本号：v1.0.0
 * 作者QQ：358279128
 * PHPTools 操作演示
 * 广告：www.MingyuanTech.com.cn
**************************************************/

## 插件介绍
	本插件属于Sublime Text 2的一个PHP的扩展，目前可实现的功能为【语法检测】【执行文件】【执行内容】【格式化文件】【格式化内容】

## 主菜单
	默认快捷键为ctrl+alt+shift+p弹出菜单，菜单的定义文件为：PHPTools_menu.json
	[
		{
			"NAME": "(1) 语法检测",
			"TYPE": "CLASS",
			"CLASS": "phptools",
			"ARGS": {"iDe":"Syntax"}
		},
		{
			"NAME": "(2) 执行代码",
			"TYPE": "MENU",
			"MENU":
			[
				{"NAME": "(0) 返回上一级", "TYPE":"JUMP",},
				{"NAME": "(1) 执行文件","TYPE": "CLASS","CLASS": "phptools", "ARGS": {"iDe":"execScript"}},
				{"NAME": "(2) 执行选择行", "TYPE": "CLASS","CLASS": "phptools", "ARGS": {"iDe":"execScript", "Type": "Lines"}},
				{"NAME": "(3) 执行选中字符", "TYPE": "CLASS","CLASS": "phptools", "ARGS": {"iDe":"execScript", "Type": "Select"}}
			]
		},
		{
			"NAME": "(3) 格式化代码",
			"TYPE": "MENU",
			"MENU":
			[
				{"NAME": "(0) 返回上一级", "TYPE":"JUMP",},
				{"NAME": "(1) 格式化文件", "TYPE": "CLASS","CLASS": "phptools", "ARGS": {"iDe":"Stylist"}},
				{"NAME": "(2) 格式化选择行","TYPE": "CLASS","CLASS": "phptools", "ARGS": {"iDe":"Stylist", "Type": "Lines"}},
				{"NAME": "(3) 格式化选中字符","TYPE": "CLASS","CLASS": "phptools", "ARGS": {"iDe":"Stylist", "Type": "Select"}}
			]
		}
	];
	如果要调整菜单要注意前面的(1)的排序，程序中是以这个数字来排序菜单的
	TYPE 为 当前菜单的类型
		MEMU：菜单
		CLASS:为要执行的命令	ARGS:待执行命令的参数
		JUMP:返回上一层菜单

# 插件描述
	插件功能中的多数功能其实还是调用了ST的编译器函数执行的，由于对show_panel还不是很了解，所以就采用了使用ST本身的功能，稳定可靠啊。
	关于代码格式化采用的是 phpStylist.php，也修复了其中的一些Bug。
	其中的lib目录的php.exe的版本是 5.2.17 如有必要可自行升级
	程序包中还附带打包了phpCB，一个老牌的php代码格式化的程序，只是本人不太喜欢他格式化后的样式，所以采用了phpStylist。

# 本插件也是本人的第一个ST的插件，由于是初学Python，所以不足之处还请多多见谅啊。
	Bug 和 建议反馈邮箱：358279128@QQ.com
