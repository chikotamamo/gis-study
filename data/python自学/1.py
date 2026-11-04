# print("Hello World")
# print("Hello Python")
# print("-----------------------")

# %占位符
# name = "涛哥"
# age = 18
# pro = "软件工程"
# hobby = "Python、Java"
# print("大家好，我是%s，今年%s，学习的专业是%s，爱好%s"%(name,age,pro,hobby))


# f"....内容{变量名、表达式}...."!!!!常用
# name = "涛哥"
# age = 18
# pro = "软件工程"
# hobby = "Python、Java"
# print(f"大家好，我是{name}，今年{age}，学习的专业是{pro}，爱好{hobby}")


# imput(..) 获取键盘上输入的数据
# name = input("请输入您的姓名：")
# age = input("请输入您的年龄：")
# print(f"您的姓名是：{name}，您的年龄是：{age}")

# 模拟银行取款
# total = 10000
# password = input("输入密码：")
# out = input("输入取款金额：")

# print(f"取款后的余额：{total - out}")
# 此时out是字符串类型（str）
# 【因为input输入结果都为字符串】，输出结果会报错，无法进行运算。所以要将out转为int类型。

# print(f"剩余余额为：{total - int(out)}")


# num1 = input("请输入数字1：")
# num2 = input("请输入数字2：")
# print(f"两数字之和为{int(num1) + int(num2)}")


# if语句，if后面的条件语句必须为布尔值（即输出为True or False）
# score = 698
# if score > 680:
#     print("欢迎你来到清华读书")

# account = 1888888
# password = 666888
# shuru_account = int(input("请输入账号："))
# shuru_password = int(input("请输入密码："))
# if account == shuru_account and password == shuru_password:
#     print("登入成功")
# else:
#     print("登入失败")


# num = int(input("请输入数字："))
# if num > 0:
#     print(f"数字{num}是正数")
# elif num < 0:
#     print(f"数字{num}是负数")
# else:
#     print(f"数字{num}是0")


# username = input("请输入用户名")
# password = input("请输入密码")
# if username == "admin" and password == "666888" or username == "root" and password == "547527" or username == "zhangsan" and password == "123456":
#      print("登入成功")
# else:
#      print("用户名或密码错误")


# username = input("请输入用户名")
# password = input("请输入密码")
# if username == "admin" and password == "666888":
#     print("登入成功")
# elif username == "root" and password:
#     print("登入成功")
# elif username == "zhangsan" and password == "123456":
#     print("登入成功")
# else:
#     print("用户名或密码错误")

"""""
a = int(input("请输入边长a"))
b = int(input("请输入边长b"))
c = int(input("请输入边长c"))
if a + b > c and a + c > b and b + c > a and a != b != c:
    print("普通三角形")
elif a == b == c:
    print("等边三角形")
elif a == b or a == c or b == c:
    print("等腰三角形")
else:
    print("不是三角形")
"""""


"""""
匹配：match....case....  |(或者-or)  _(else匹配其他所有情况)
day = input("请输入星期几(1-7):")
match day:
     case "1":
         print("周一：...")
     case "2":
         print("周二:...")
     case "3":
         print("周三:...")
     case "4":
         print("<UNK>:...")
     case "5":
         print("<UNK>:...")
     case "6" | "7":
         print("<UNK>:...")
     case _:
         print("输入有误")
"""""

# num1 = float(input("请输入数1"))
# num2 = float(input("请输入数2"))
# oper = input("请输入运算符")
# match oper:
#     case "+":
#         print(f"{num1 + num2}")
#     case "-":
#         print(f"{num1 - num2}")
#     case "*":
#         print(f"{num1 * num2}")
#     case "/" if num2 != 0: #if条件成立才能匹配这个case
#         print(f"{num1 / num2}")
#     case _:
#         print("错误！")

"""""
action = input("请输入指令")
match action:
    case "上" | "w" | "W":
        print("角色向上移动")
    case "下" | "s" | "S":
        print("角色向下移动")
    case "左" | "a" | "A":
        print("角色向左移动")
    case "右" | "d" | "D":
        print("角色向右移动")
    case "跳" | " ":
        print("角色跳跃")
    case "攻击" | "j" | "J":
        print("角色攻击")
    case "退出" | "esc" | "ESC":
        print("角色退出游戏")
    case _:
        print("操作有误")
"""""


# while循环
# i = 0
# while i < 10:
#     print("学python")
#     i += 1
# else:
#     print("执行完毕")

"""""
#1-100中所有偶数累加之和
total = 0     #记录累加之和
i = 1         #循环开始
while i <= 100:
    if i % 2 == 0:
        total += i
    else:
        pass
    i += 1
else:
    print(total)
"""""


#for 循环结构
# for ... in ....:
#     循环体（对元素进行处理）
# else:   可有可无
# 循环结束的代码体


# msg = "Hello-Python" #定义要遍历的字符串(就是将里面的元素都过一遍)
# for i in msg: #遍历字符串，并进行处理
#     print(i)
# else:
#     print("遍历结束")

# """""
# total = 0
# i = 1
# for i in range(101):
#     if i % 2 != 0:
#         total += i
#     else:
#         pass
#     i += 1
# else:
#     print(total) #0-100中奇数之和
#
# \n
# total = 0
# for i in range(1,101,2)
#     total += i
# print(total)
# \n
#
# #range(end) {range(5)---0.1.2.3.4}
# #range(start,end){range(1,5)---1.2.3.4}
# #range(start,end,step){range(0,10,2)---0.2.4.6.8}
#
# total = 0 #100-500中 3的倍数之和
# i = 100
# for i in range(100,501):
#     if i % 3 == 0:
#         total += i
#     else:
#         pass
#     i += 1
# else:
#     print("100-500中 3的倍数之和",total)
# """""


#打印一个长度为m，宽度为n的长方形
"""""
m = int(input("请输入长度："))
n = int(input("请输入宽度"))
for j in range(n):  #控制行
    for i in range(m): #控制列
        print("*", end="  ")
    print() #自动换行
"""""


#打印一个99乘法表
"""""
for i in range(1,10):
    for j in range(1,i+1):
        print(f" {j} x {i} = {i*j}", end="\t")
    print()
"""""#标准答案

#我的
"""""
i = 1
j = 1
if j < 10:
    for i in range(1,10):
        for j in range(1,i+1):
            print(f" {j} x {i} = {i*j}", end="\t")
        print()
"""""

"""""
a = int(input("请输入直角边的边长"))
for a in range(1,a+1):
    for a in range(1,a+1):
        print("*", end=" ")
    print()
"""""


'''''
while True:
    name = input("请输入用户名：")
    password = input("请输入密码：")
    if name == "" or password == "":
        print("不能为空！")
        break
    if name != "zhangsan" and password != "666888":
        print("用户或密码错误，请重新输入")
        break

while True:
    name = input("请输入正确的用户名：")
    password = input("请输入正确的密码：")
    if name == "" or password == "":
        print("不能为空！")
    elif name == "zhangsan" and password == "666888":
        print("登入成功，进入b站首页~")
        break
    else:
        print("用户或密码错误，请重新输入")
'''''

# 需求：用户名密码登录，
# 正确的用户名和密码为admin/666888 、zhangsan/123456、taoge/888666,
# 5次登录机会，输入错误五次，不允许再操作了。
# n = 0
# while True:
#     name = input("请输入正确的用户名：")
#     password = input("请输入正确的密码：")
#     if name == "admin" and password == "666888":
#         print("登陆成功")
#         break
#     elif name == "zhangsan" and password == "123456":
#         print("登陆成功")
#         break
#     elif name == "taoge" and password == "888666":
#         print("登陆成功")
#         break
#     else:
#         if n == 4:
#             break
#         n += 1
#         print(f"输入错误，您还有{5-n}次机会")


'''''
# 猜数字
import random
random_num = random.randint(1,100)
while True:
    num = int(input("请输入一个数字："))
    if num > random_num:
        print("数字太大了")
        continue
    elif num < random_num:
        print("数字太小了")
        continue
    else:
        print("对了")
        print("随机的数字是", random_num)
        break
'''''


# num = 0
# for i in range(1,1001):
#     if i % 5 == 0:
#         num += i
#         print(num)


# s = [1,5,9,6,44,5,"hello",8,33,"python"]
# print(s[0])   #正向索引
# print(s[-1])  #反向索引
# s[5] = "abc"  #修改列表元素
# del s[3]      #删除列表元素
# print(s)



# 列表切片： 序列数据[开始索引:结束索引:步长]
# 如s = [1,2,3,4,5,6,7]
# s[0:5:1] print后为 1 2 3 4 5（从0到4不包括第5个）
# s[0:5:2] print后为 1 3 5（每2个截取1个）



'''''
# append()  在列表的尾部追加元素
# s.append (10086)

# insert()  在指定索引之前，插入该元素
# s.insert(o,92)   第一个数字为位置，第二个数字为要插入的数值

# remove()  移除列表中第一个匹配到的值
# s.remove(75)   如果列表里面有两个75，就会删匹配到的第一个75

# pop()     删除列表中指定索引位置的元素（如果未指定索引，默认删最后一个)
# s.pop(2)/ s.pop()

# sort()    对列表进行排序（列表元素的数据类型一致，才可以进行排序）
# s.sort()

# reverse() 反转列表元素
# s.reverse()
'''''


# a_list = []
# for i in range(10):
#     a = int(input("请输入数字"))
#     a_list.append(a)
# print("数字列表",a_list)
# a_list.sort()
# print("排序后的数字列表",a_list)
# print("最小值",a_list[0])    min()
# print("最大值",a_list[-1])   max()
# print("平均值",sum(a_list)/len(a_list))   #sum()求和；len()列表的长度/元素的个数


'''''
# 字符串不可变（无法进行修改）
s = "Hello-Python-Hello-World!"
# find()查找指定字符串第一次出现的索引位置（5）
index = s.find("-")
print(index)
# count()------出现的次数（4）
c = s.count("o")
print(c)
# strip()------去除字符串之间的空格
# replace()-----将字符串中的指定字串替换为新的内容
sr = s.replace("-", "h")
print(sr)
# split()-------将字符串切割，放到列表之中   ['Hello', 'Python', 'Hello', 'World!']
ss = s.split("-")
print(ss)
startswith()/endswith() 判断是不是括号内容的值开始/结尾 返回布尔值
经过操作后原字符串不会变，即s不会变
'''''


# mail = input("请输入邮箱()")
# if mail.count("@") == 1 and mail.count(".") >= 1:
#     print(f"{mail}是合法的邮箱")
# else:
#     print(f"{mail}不合法")


# str = input("请输入：")
# if str[::1] == str[::-1]:
#     print("对称的")
# else:
#     print("不对称")


# 元祖类似于列表，但创建后不能修改，只能进行查找。可以重复、有序，可以储存不同的数据
# t1 = (80,55,62,14,33,95,34,36,15,2,)
# print(t1)
# print(len(t1))
'''''
# 元组解包：
t1 = (5,61,3,11,35,88)
# 基础解包，需要变量数量与元祖内的个数一致
a,b,c,d,e,f = t1
print(a,b,c,d,e,f)
# 扩展解包（*号手机剩余的所有元素-----不确定数量）
a,b,c,*other,f = t1
print(a,b,c,*other,f)
'''''


# set 是一种无序的（无法通过索引找到元素）、不可重复、可修改的数据容器
# s1 = {"C","D","E","F","G","H","I"}     #定义集合
# s2 = set()   #定义空集合-------如果是 s2 = {} 这个是字典（dict）的格式


# 选修足球学生名单
football_set = {"王林", "曾牛", "徐立国", "遁天", "天运子", "韩立", "厉飞雨", "乌丑", "紫灵"}
# 选修篮球学生名单
basketball_set = {"张铁", "墨居仁","王林", "姜老道", "曾牛", "王蝉", "韩立", "天运子", "李化元", "厉飞雨", "云露"}
# 选修法语学生名单
french_set = {"许木", "王卓", "十三", "虎咆", "姜老道", "天运子",  "红蝶", "厉飞雨", "韩立", "曾牛"}
# 选修艺术学生名单
art_set = { "遁天", "天运子", "韩立", "虎咆", "姜老道", "紫灵"}


# fa = french_set.intersection(art_set)  #选择法语和艺术的学生（交集）用&也是并集（and符）
# print(f"同时选择了法语和艺术的学生:{fa}")
# all = fa & basketball_set & football_set
# print(all)


"""""
shopping_cart = {}
menu = """
############### 购物车系统 ###############
#              1.添加购物车              #
#              2.修改购物车              #
#              3.删除购物车              #
#              4.查询购物车              #
#              5.退出购物车              #
########################################
"""
print("欢迎使用购物车系统")
while True:
    print(menu)


    choice = input("请选择执行的操作(1-5)：")
    match choice:
        case "1": #添加购物车
            good_name = input("请输入商品名称：")
            good_price = input("请输入商品价值：")
            good_num = input("请输入商品数量：")
            if good_nane in shopping_cart:
                print("该商品已存在，请重新选择")
            else:
                shopping_cart[good_name] = {"price":good_price, "num":good_num}
                print("商品添加完成")
        case "2": #修改购物车
            good_name = input("请输入商品名称：")
            if good_name not in shopping_cart:
                print("该商品不存在，请重新选择")
                continue
            good_price = input("请输入商品价值：")
            good_num = input("请输入商品数量：")

            shopping_cart[good_name] = {"price": good_price, "num": good_num}
            print("商品修改完成")
        case "3": #删除购物车
            good_name = input("请输入商品名称：")
            if good_name not in shopping_cart:
                print("该商品不存在，请重新选择")
            else:
                del shopping_cart[good_name]
        case "4": #查询购物车
            for good_name in shopping_cart.keys():
                good_info = shopping_cart[good_name]
                print(f"商品名称：{good_name},商品价格：{good_info['price']},商品数量：{good_info['num']}")
        case "5": #退出购物车
            print("bye~")
            break
        case _:#匹配其他所有情况
            print("错误操作")
"""""


"""
采用面向对象的编程思想，完成教务管理系统的开发。教务管理系统可以管理在校学生的成绩信息，通过控制台菜单与用户交互，具体的功能如下：
    1. 添加学生成绩：根据输入的学生姓名、语文成绩、数学成绩、英语成绩，记录在系统中
        1.1 输入学生姓名、语文成绩、数学成绩、英语成绩
        1.2 检查学生姓名是否已存在, 如果学生不存在, 再添加 (存在则, 不添加)
        1.3 验证成绩范围（0-100分）
        1.4 创建学生对象并添加到系统
    2. 修改学生成绩：根据输入的学生姓名，修改对应的学生成绩
        2.1 输入要修改的学生姓名
        2.2 根据姓名查找该学生, 显示该生当前成绩信息
        2.3 输入新的语文、数学、英语成绩
        2.4 更新学生成绩数据
    3. 删除学生成绩：根据输入的学生姓名，删除对应的学生成绩
    4. 查询指定学生成绩：根据输入的学生姓名，查找对应的学生成绩，并输出
        4.1 输出格式为: "姓名：张三 | 语文：85 | 数学：90 | 英语：88 | 总分：263"
    5. 展示全部学生成绩：展示出系统中所有学生的成绩
"""



'''''
student_system = {}
menu = """
1.添加学生成绩
2.修改学生成绩
3.删除学生成绩
4.查询指定学生成绩
5.展示全部学生成绩
"""
while True:
    print(menu)
    choice = input("请输入执行的操作（1-5）：")
    match choice:
        case "1":
            student_name = input("请输入姓名：")
            if student_name in student_system:
                print("该学生已存在")
            elif student_china and student_math and student_english in (0,101):
                student_china = input("请输入语文成绩：")
                student_math = input("请输入数学成绩：")
                student_english = input("请输入英语成绩：")


                student_system[student_name] = {"china": student_china, "math": student_math,"english": student_english}
                print("成绩添加完毕")
            else:
                print("成绩非法")
        case "2":
            xiugai_student = input("请输入要修改的同学名字：")
'''''


# # 定义函数：
# def 函数名（参数列表）:  -----------------def out_line()
#     函数体             ---------------------print('-----')
#     .....:
#     return 返回值
#
# 调用函数：
# 函数名（参数）           -----------------out_line()
#
# 函数必须先定义再调用

'''''
def out_line():
    print("---------")
    print("---------/....")

函数调用
out_line()   函数定义后不会执行，只会调用的时候才会执行
'''''

#函数的参数与返回值
# def circle_area(r):
#     area = math.pi * r * r # math.pi * r ** 2
#     return area
# area = circle_area(10)
# print(area)


'''''
# 返回多个值，中间用，隔开、
def circle_area_len(r):
    """
    该函数用于计算圆的面积和周长
    return 圆的面积，圆的周长
    """
    return math.pi * r ** 2 , round(2 * math.pi * r , 2)  #保留2位小数
al = circle_area_len(5)
print(al)                       #--------------多个值装到元祖之中
area,len = circle_area_len(5)   #--------------元祖的解包
print(area,len) 
'''''


# 函数的嵌套调用   遵循栈结构-----后进先出/先进后出
# def triangle_area(d,h):
#     """
#     根据输入的底和高，计算三角形的面积
#     :param d: 底长
#     :param h: 高
#     :return: 三角形面积
#     """
#     area = d * h / 2
#     return area
# print(triangle_area(4,5))


"""""
def count_aeiou(s):
    num = 0
    for i in s:
        if i in "aeiouAEIOU":
            num += 1
    return num

count = count_aeiou("Hello World!")
print(count)

def calc_score(score_list):
    max_s = max(score_list)
    min_s = min(score_list)
    avg_s = round(sum(score_list)) / len(score_list)
    return max_s, min_s, avg_s

s_list = [500,620,580,540,532,489,528]
max_score, min_score, avg_score = calc_score(s_list)
print("最高分",max_score)
print("最低分",min_score)
print("平均分",avg_score)
"""""


# 需求1：定义一个函数，根据传入的分数，计算对应的分数等级并返回。
# - 分数 >= 90：A
# - 分数 >= 75：B
# - 分数 >= 60：C
# - 分数 < 60：D
# def score(num):
#     if num >= 90:
#         return "A"
#     elif num >= 80:
#         return "B"
#     elif num >= 70:
#         return "C"
#     else:
#         return "D"
# print(score(66))
# print(score(90))
# print(score(80))
# print(score(78))

# 需求2：定义一个函数，用于判断一个字符串是否是回文串，返回bool值。
# 把字符串反转，如果和原字符串相同，就是回文串。（如："level"，"radar"，"黄山落叶松叶落山黄"）
# def sent(put):
#     return put == put[::-1]
# print(sent("<UNK>"))

# 定义一个函数：完成时间转换功能，将传入的秒转换为小时、分钟、秒。
# def time_convert(seconds):
#     hours = seconds // 3600
#     minutes = (seconds % 3600) // 60
#     seconds = (seconds % 3600) % 60
#     return f"{seconds} 转换为 {hours} 小时 {minutes} 分钟 {seconds} 秒"
#
# print(time_convert(3772))


"""""
# 函数的传参方式
def reg_stu(name,age,gender,city):
    print(f"注册成功，姓名：{name}.年龄：{age},性别：{gender},城市：{city}")
    return {"name":name,"age":age,"gender":gender,"city":city}
stu1 = reg_stu("张三",18,"男","北京")                                 #位置参数，要求顺序对应
stu2 = reg_stu(name = "王林",age = 18,gender = "男",city = "北京")    #关键字参数
stu3 = reg_stu(age = 18,gender = "女",city = "北京",name = "李慕婉")   #关键字参数不要求顺序
"""""


# 基于位置参数的不定长参数  ---->*args为一个元祖
# def calc(*args):
#     max_data = max(args)
#     min_data = min(args)
#     avg_data = round(sum(args)/len(args),2)
#     print(f"最大值：{max_data},最小值：{min_data},平均值：{avg_data}")
#     return max_data, min_data, avg_data
#
# args1 = calc(1,2,3,55,88,964,12,548,32)
# args2 = calc(22,65,84,3,168,49,561,31)

#基于关键字参数的不定长参数-------> **kwargs为一个字典
# def calc(*args,**kwargs):
#     """
#     根据输入的数据，计算最小最大平均值
#     :param args: 不定长位置参数
#     :param kwargs: 不定长关键字参数
#             round:保留的个位数小数
#     :return: 最小值、最大值、平均值
#     """
#     max_data = max(args)
#     min_data = min(args)
#     avg_data = round(sum(args)/len(args),2)
#     if kwargs.get("round") is not None:
#         avg_data = round(avg_data,kwargs.get("round"))
#     if kwargs.get("print"):
#         print(f"最大值：{max_data},最小值：{min_data},平均值：{avg_data}")
#     return max_data, min_data, avg_data
#
# args1 = calc(1,2,3,55,88,964,12,548,round=3,print=True)
# args2 = calc(22,65,84,3,168,49,561,31)
# print(args2)


'''
# 定义匿名函数
lambda 参数列表：函数体
例如： lambda : print('-------')    #没有名字，只有输出函数
lambda x,y:x + y                   #lambda匿名函数只能比较简单或单行表达式---简化书写
'''

# out_line = lambda : print("---------")
# out_line()
# add = lambda x,y: x + y
# print(add(100,500))

"""
#定义一个函数，根据传入的数字，计算该数字阶乘的结果（f(n) = n * f(n-1)）
def jc(n):
    if n == 1
        return 1
    return n * jc(n-1)      #递归调用-----在函数体中自己调用自己的情况
#递归调用一定要有终结点，不然会一直进行调用
"""


#函数类型注解
                  #↓给函数值参数指定类型    ↓后面是指定返回值的类型
# def circle_area(r: float) -> tuple[float, float]:
#     return round( 3.14 * r ** 2, 2) , round( 2 * 3.14 * r ** 2, 1)
#
# al = circle_area(10)
# print(al)


#模块：   导入模块        多个模块用，隔开                  调用方式   random为模块  randint为功能
# import 模块名------>  import random, os  ---------->  模块名.功能名（random.randint(10,100)）
# from 模块名 import 功能名 ----> from random import randint -------> randint(10,100)

# 导入模块-----> 调用方式：模块名/别名.功能名
# import random as rd
#
# for i in range(100):
#     print(rd.randint(1,100))
#
# # 导入模块的功能 --> 调用方式：功能名/别名
# from random import randint as rt
# for i in range(100):
#     print(rt(1,100))
# 每一个python文件都可以作为一个模块，模块的名字就是文件的名字。


# 面向对象编程--->谁能帮我做...事，调用合适的功能去完成需求
# 类---->模版    对象----->基于类创造出来的实例
"""
# 定义类：     类名的命名需每个单词的首字母为答谢，且没有分隔符（例如：UserInfo，UserAccount)
class 类名:           class Car:
    pass                pass
# 创建对象：     对象名=类名()     对象名.属性名1=属性值1     对象名.属性值2=属性值2
c1 = Car()
c1.brand = "BMW"
c1.name = "X5"
c1.price = 500000
print(c1.__dict__)              --------->__dict__为特殊的属性，以字典的形式储存对象的属性值
"""

# class Car:
#     pass
# # 创建对象
# c2 = Car()
# # 动态的为对象添加属性
# c2.color = "red"
# c2.brand = "AD"
# c2.name = "A6l"
# c2.price = 50000
# print(c2)
# print(c2.__dict__)      # 会将对象中的所有属性以字典的形式输出出来


"""
# 定义类：  __init__为初始化方法，自动调用的设置对象的属性-->构造函数    self-->第一个参数，表示当前创建的实例对象
# class 类名：
#      def __init__(self,参数列表):
#          self.属性名 = 参数值
#          self.属性名 = 参数值
# 创建对象：
# 对象名 = 类名(参数列表)

class Car:
    def __init__(self, c_brand, c_name, c_price):
        self.brand = c_brand
        self.name = c_name
        self.price = c_price
        print("Car类的对象初始化完毕，对象属性已经添加完毕。")
# 创建对象
c1 = Car("BWM","X7","800000")
print(c1.__dict__)
"""

'''
class Car:
    def __init__(self, c_color, c_brand, c_name, c_price):
        self.color = c_color
        self.brand = c_brand
        self.name = c_name
        self.price = c_price
        print("Car类的对象初始化完毕，对象属性已经添加完毕。")
# 定义实例方法
    def running(self):
        print(f"{self.brand}{self.name}正在高速行驶中...")
    def total_cost(self, discount, rate):
        """
        :param discount: 折扣
        :param rate: 税率
        :return: 提车的总价格
        """
        total = float(self.price * discount + self.price * rate)
        return total
    def __str__(self):          #构造函数（魔法方法） 调用方法的时候会自动调用魔法方法，使得对象变成字符串。
        return f"{self.color} {self.brand} {self.name} {self.price}"
    def __eq__(self,other):     #__eq__是对比两个对象是否相等
        return self.price == other.price and self.color == other.color and self.brand == other.brand and self.name == other.name
    def __lt__(self,other):     #用于对比谁大谁小  lt代表的是小于
        return self.price < other.price
# 创建对象
c1 = Car("黑色","BMW","X7",800000)
c2 = Car("白色","BMW","X7",800000)
print(c1)
print(c2)
c1.running()
print(c1 == c2)
print(c1 > c2)
cost = c1.total_cost(0.8,0.1)
print("提车的总费用为",cost)
'''



# class Car:
#     # 类属性（所有实例对象共享）: --------> 查找先查找实例属性，再查类属性   类属性相当于是默认值
#     wheel = 4        # 轮胎数量
#     tax_rate = 0.1   # 税率
#     def __init__(self, c_color, c_brand, c_name, c_price):
#         # 实例属性
#         self.color = c_color
#         self.brand = c_brand
#         self.name = c_name
#         self.price = c_price
#         print("Car类的对象初始化完毕，对象属性已经添加完毕。")
# # 定义实例方法
#     def running(self):
#         print(f"{self.brand}{self.name}正在高速行驶中...")
#     def total_cost(self, discount, rate):
#         total = float(self.price * discount + self.price * rate)
#         return total


"""
采用面向对象的编程思想，完成教务管理系统的开发。教务管理系统可以管理在校学生的成绩信息，通过控制台菜单与用户交互，具体的功能如下：
1．添加学生成绩：根据输入的学生姓名、语文成绩、数学成绩、英语成绩，记录在系统中
    1.1输入学生姓名、语文成绩、数学成绩、英语成绩
    1.2检查学生姓名是否已存在，如果学生不存在，再添加（存在则，不添加）
    1.3验证成绩范围（0-100分）
    1.4创建学生对象并添加到系统
2．修改学生成绩：根据输入的学生姓名，修改对应的学生成绩
    2.1输入要修改的学生姓名
    2.2根据姓名查找该学生，显示该生当前成绩信息
    2.3输入新的语文、数学、英语成绩
    2.4更新学生成绩数据
3，删除学生成绩：根据输入的学生姓名，删除对应的学生成绩
4，查询指定学生成绩：根据输入的学生姓名，查找对应的学生成绩，并输出
    4.1输出格式为："姓名：张三/语文：85|数学：90|英语：88|总分：263"
5.展示全部学生成绩：展示出系统中所有学生的成绩

# 学生信息
class Student:
    def __init__(self,name,china,math,english):
        self.name = name
        self.china = china
        self.math = math
        self.english = english

    def __str__(self):
        return (f"姓名：{self.name} | 语文：{self.china} | 数学：{self.math} | 英语：{self.english} \n"
                f"总分：{self.china + self.math + self.english}")

    def data_score(self,china=None,math=None,english=None):
        if china is not None:
            self.china = china
        if math is not None:
            self.math = math
        if english is not None:
            self.english = english

# if __name__ == "__main__":
#     s1 = Student("小王",98,99,84)
#     print(s1)
#     s1.data_score(math=100)
#     print(s1)

# 教务管理系统
class EduManagement:
    system_version = 1.0
    system_name = "教务管理系统"

    def __init__(self):
        self.student_list = []

# 添加学生成绩
    def add_student(self):
        name = input("请输入学生的姓名")
        # 判断学生是否存在
        for s in self.student_list:
            if s.name == name:
                print("该学生已存在")
                return

        china = int(input("请输入学生的语文成绩"))
        math = int(input("请输入学生的数学成绩"))
        english = int(input("请输入学生的英语"))

        # 判断分数是否在 0 - 100 之间
        if china and math and english in range(1,101):
            s = Student(name,china,math,english)
            self.student_list.append(s)
            print("学生信息添加成功~")
        else:
            print("各科成绩非法")

# 修改学生信息
    def data_student(self):
        name = input("请输入要修改的学生的姓名：")
        for s in self.student_list:
            if s.name == name:
                print(f"当前成绩为：{s}")
                china = int(input("请输入修改后的语文成绩"))
                math = int(input("请输入修改后的数学成绩"))
                english = int(input("请输入修改后的英语"))
                if china and math and english in range(1, 101):
                    s.data_score(china,math,english)
                    print("学生信息修改成功~")
                    print(f"修改后的成绩：{s}")
                else:
                    print("各科成绩非法")
                return
        print("未找到该学生，修改失败")

# 删除学生成绩
    def delete_student(self):
        name = input("请输入需要删除的学生姓名：")
        for s in self.student_list:
            if s.name == name:
                self.student_list.remove(s)
                print("学生信息删除成功~")
                return
        print("未找到该学生，删除失败")

# 查询指定学生的成绩
    def index_student(self):
        name = input("请输入需要查询的学生姓名：")
        for s in self.student_list:
            if s.name == name:
                print(f"学生信息：{s}")
            return
        print("未找到该学生，查询失败")

#展示全部学生成绩
    def all_student(self):
        for s in self.student_list:
            print(s)

# 运行系统的方法
    def run(self):
        print(f"欢迎来到教务管理系统  V{EduManagement.system_version}")

        while True:
            print()
            print(" # " * 30)
            print("1. 添加学生  2. 修改学生  3. 删除学生  4. 查询指定学生 5. 查询所有学生  6. 退出系统")
            print(" # " * 30)

            choice = input("请选择要执行的操作：输入1-6：")
            match choice:
                case "1":
                    self.add_student()
                case "2":
                    self.data_student()
                case "3":
                    self.delete_student()
                case "4":
                    self.index_student()
                case "5":
                    self.all_student()
                case "6":
                    print("拜拜~")
                    break
                case _:
                    print("输入非法")

# 测试
if __name__ == "__main__":
    edu = EduManagement()
    edu.run()
"""


"""
采用面向对象的编程思想，开发一个购物车管理系统，实现商品信息的添加、修改、删除、查询功能。系统使用自定义对象存储商品数据，通过控制台菜单与用户交互。
具体功能如下：
    1. 添加购物车：用户根据提示录入商品名称、以及该商品的价格、数量，保存该商品信息到购物车。
    2. 修改购物车：要求用户输入要修改的购物车商品名称，然后再提示输入该商品的价格、数量，输入完成后修改该商品信息。
    3. 删除购物车：要求用户输入要删除的购物车名称，根据名称删除购物车中的商品。
    4. 查询购物车：将购物车中的商品信息展示出来，格式为："商品名称: xxx, 商品价格: xxx, 商品数量: xxx"。
    5. 退出购物车

class Goods:
    def __init__(self,name,price,num):
        self.name = name
        self.price = price
        self.num = num

    def __str__(self):
        return f"名字{self.name} | 价格{self.price} | 数量{self.num} "

    def data_goods(self,name=None,price=None,num=None):
        if name is not None and price is not None and num is not None:
            self.name = name
            self.price = price
            self.num = num

class Shopping:
    def __init__(self):
        self.shopping_list = []

    def add_goods(self):
        name = input("请输入商品名称：")
        for g in self.shopping_list:
            if g.name == name:
                print(f"商品{g}已存在")
                return
        price = input("请输入商品价格：")
        num = input("请输入商品数量：")
        g = Goods(name,price,num)
        self.shopping_list.append(g)
        print(f"商品{name}录入完毕")

    def data_goods(self):
        name = input("请输入要修改的商品名字")
        for g in self.shopping_list:
            if g.name == name:
                n_name = input("请输入修改后的商品名字")
                n_price = int(input("请输入修改后的商品价格"))
                n_num = int(input("请输入修改后的商品数量"))
                g.data_goods(name=n_name,price=n_price,num=n_num)
                print("商品修改成功")
                return
            print("未找到该商品")


    def delete_goods(self):
        name = input("请输入要删除的商品名字")
        for g in self.shopping_list:
            if g.name == name:
                self.shopping_list.remove(g)
                print(f"商品{name}删除完毕")
                return
            print("未找到该商品")


    def index_goods(self):
        name = input("请输入要查询的商品名字")
        for g in self.shopping_list:
            if g.name == name:
                self.shopping_list = []
                print(f"商品{name}的价格为{g.price}，数量{g.num}")
                return
            print("未找到该商品")
            

    def run(self):
        while True:
            print("欢迎来到购物车系统")
            print(" # " * 30)
            print("1. 添加购物车  2. 修改购物车  3. 删除购物车  4. 查询购物车 5. 退出购物车 ")
            print(" # " * 30)

            choice = input("请输入功能1-5：")
            try:
                match choice:
                    case "1":
                        self.add_goods()
                    case "2":
                        self.data_goods()
                    case "3":
                        self.delete_goods()
                    case "4":
                        self.index_goods()
                    case "5":
                        print("拜拜~")
                        break
                    case _:
                        print("操作有误，请重新选择1-5功能：")
            except ValueError:
                print("输入的数据有问题，请重新输入")
            except Exception:
                print("程序有误")

if __name__ == "__main__":
    good = Shopping()
    good.run()
"""
