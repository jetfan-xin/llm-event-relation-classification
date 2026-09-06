import os

# 指定文件夹路径
folder_path = "semantic-networks"

# 遍历文件夹的第一层文件
def list_first_level_files(folder):
    try:
        for item in os.listdir(folder):
            full_path = os.path.join(folder, item)
            if os.path.isfile(full_path):  # 只检查文件
                print(full_path)
    except Exception as e:
        print(f"Error: {e}")

# 执行函数
list_first_level_files(folder_path)