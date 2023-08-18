from github import Github
import os

# GitHub账户信息
username = "jackylang2012@163.com"
password = "Jacky456123"

# 仓库信息
repo_owner = "jackylang2012"
repo_name = "superJump"

# 文件路径
file_path = "cunDang/name1.json"  # 修改为实际文件路径

# 创建Github对象并登录
g = Github(username, password)

# 获取指定仓库
repo = g.get_user(repo_owner).get_repo(repo_name)

# 上传文件
with open(file_path, "r") as file:
    content = file.read()

# 将文件上传到仓库
try:
    repo.create_file(file_path, "Commit message", content, branch="main")  # 您可能需要修改分支名
    print("File uploaded successfully to GitHub.")
except Exception as e:
    print("Error uploading file to GitHub:", e)
