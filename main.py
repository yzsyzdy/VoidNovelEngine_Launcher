import os
import time
import file

def menu():
    time.sleep(1)
    os.system('cls')
    print("="*50,"\n欢迎使用VNEHub\n","="*50)
    print("操作菜单")
    print("1.创建新项目")
    print("2.打开已有的项目")
    print("3.管理项目")
    print("E.退出程序")
    Translate_user_input()

def Translate_user_input():
    user_input = input("请输入选项:")
    if user_input == "1":
        user_input = input("项目名称:")
        file.new_project(name=user_input,dr=True)
        file.start_engineer(project_name=user_input)
    if user_input == "2":
        print("项目列表",file.get_project())
        user_input = input("请输入要打开的项目名称:")
        file.start_engineer(project_name=user_input)
    if user_input == "E" or user_input == "e":
        print("程序已退出")
        exit()
menu()