import os
import time
import file
import webbrowser

# 状态管理
current_state = "menu"          # "menu", "awaiting_project_name"
pending_action = None           # 等待执行的动作

# 这两个函数将在 GUI 启动时被替换
def gui_print(*args, **kwargs):
    print(*args, **kwargs)

clear_screen = None              # 将在 GUI 中注入

def menu():
    
    gui_print("=" * 50)
    gui_print("\n欢迎使用VoidNovelEngine_Launcher\n")
    gui_print("=" * 50)
    gui_print("操作菜单")
    gui_print("1.创建新项目")
    gui_print("2.打开已有的项目")
    gui_print("3.管理项目")
    gui_print("4.工具")
    gui_print("5.设置")
    gui_print("E.退出程序")

def Translate_user_input(user_input):
    global current_state, pending_action

    if current_state == "menu":
        if user_input == "1":
            gui_print("请输入新项目名称：")
            current_state = "awaiting_project_name"
            pending_action = "create_project"
        elif user_input == "2":
            projects = file.get_project()
            if projects:
                gui_print("现有项目列表：")
                for i, project in enumerate(projects, 1):
                    gui_print(f"{i}. {project}")
                gui_print("请输入要打开的项目名称：")
                current_state = "awaiting_project_name"
                pending_action = "open_project"
            else:
                gui_print("暂无项目，请先创建项目")
                menu()
        elif user_input == "3":
            projects = file.get_project()
            if projects:
                gui_print("项目列表:")
                for project in projects:
                    gui_print(f"  - {project}")
            else:
                gui_print("暂无项目")
            menu()
        elif user_input == "4":
            gui_print("=" * 50)
            gui_print("工具")
            gui_print("=" * 50)
            gui_print("1.调用VNEhub的多线程下载引擎进行文件下载")
            gui_print("未完待续...")
            gui_print("E.返回主菜单")
            # 实际应进入子菜单，这里简化处理
            menu()
        elif user_input == "5":
            webbrowser.open("https://www.bilibili.com/video/BV1UT42167xb")
            menu()
        elif user_input.lower() == "e":
            gui_print("程序已退出")
            exit()
        else:
            gui_print("无效输入，请重新选择")
            menu()

    elif current_state == "awaiting_project_name":
        if pending_action == "create_project":
            if user_input:
                try:
                    file.new_project(name=user_input, dr=True)
                    gui_print(f"项目 '{user_input}' 创建成功！")
                    gui_print("正在启动编辑器...")
                    file.start_engineer(project_name=user_input)
                except Exception as e:
                    gui_print(f"创建项目失败：{e}")
            else:
                gui_print("项目名称不能为空")
            current_state = "menu"
            pending_action = None
            menu()
        elif pending_action == "open_project":
            if user_input:
                projects = file.get_project()
                if user_input in projects:
                    try:
                        file.start_engineer(project_name=user_input)
                    except Exception as e:
                        gui_print(f"启动编辑器失败：{e}")
                else:
                    gui_print(f"项目 '{user_input}' 不存在")
            else:
                gui_print("项目名称不能为空")
            current_state = "menu"
            pending_action = None
            menu()