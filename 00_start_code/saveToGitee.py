import os
from git import Repo

# Gitee repository information
repo_url = "git@gitee.com:jackylang2012/super-jump.git"  # Replace with your repository URL
repo_path = "E:\lcl\pythonProject\lcl\superJump"  # Replace with your local repository path

# File information
file_path = "cunDang"  # Replace with the file you want to upload
commit_message = "Upload file"

# Clone the repository if not already cloned
if not os.path.exists(repo_path):
    Repo.clone_from(repo_url, repo_path)

# Open the repository
repo = Repo(repo_path)

# Fetch the latest changes from the remote
origin = repo.remotes.origin
origin.fetch()

# Create a new branch and switch to it
new_branch_name = "upload_branch"
repo.create_head(new_branch_name, origin.refs.master).set_tracking_branch(origin.refs.master)
repo.heads[new_branch_name].checkout()

# Copy the file to the repository directory
file_name = os.path.basename(file_path)
repo_file_path = os.path.join(repo_path, file_name)
with open(file_path, "rb") as src_file, open(repo_file_path, "wb") as dest_file:
    dest_file.write(src_file.read())

# Add, commit, and push the changes
index = repo.index
index.add([file_name])
index.commit(commit_message)
origin.push(new_branch_name)

print("File uploaded successfully to Gitee.")
