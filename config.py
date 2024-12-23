"""
@File      :hf_dl05.py
@Author:fayue yang
"""
# config.py

# 配置选项
config = {
    # 是否强制重新下载文件。如果为 True，则每次下载都会重新开始，而不是从部分下载的文件继续。
    "force_download": False,
    
    # 是否删除部分下载的文件。如果为 True，则在下载前会删除所有 .incomplete 后缀的文件。
    "remove_incomplete": False,
    
    # 下载失败时的重试次数。
    "retries": 3,
    
    # 每次重试之间的延迟时间，单位为秒。
    "delay": 30,
    
    # 文件下载保存的目录。
    "save_dir": "E:\\modelsDownloads\\save",
    
    # 是否启用 hf_transfer。如果为 True，则启用 hf_transfer 进行下载。
    "use_hf_transfer": True,
    
    # Python 的本地路径。
    "python_path": "E:\\Python\\python.exe"
}

# 镜像站点支持选项
mirror_options = {
    # 每个镜像站点支持的选项。例如，"resume_download" 表示支持断点续传。
    "https://huggingface.co": ["resume_download"],
    "https://hf-mirror.com": ["resume_download"],
    "https://mirror.sjtu.edu.cn": [],
    "https://mirrors.tuna.tsinghua.edu.cn": [],
    "https://mirrors.ustc.edu.cn": [],
    "https://gitee.com": []
}

# 获取配置选项
def get_config():
    return config

# 获取镜像站点支持选项
def get_mirror_options():
    return mirror_options

# 更新配置选项
def update_config(new_config):
    global config
    config.update(new_config)

# 更新镜像站点支持选项
def update_mirror_options(mirror, options):
    global mirror_options
    mirror_options[mirror] = options