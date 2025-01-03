# config.py

# 配置选项
config = {
    # 是否强制重新下载文件。如果为 True，则每次下载都会重新开始，而不是从部分下载的文件继续。
    "force_download": False,
    
    # 是否删除部分下载的文件。如果为 True，则在下载前会删除所有 .incomplete 后缀的文件。
    "remove_incomplete": False,
    
    # 下载失败时的重试次数。设置为 0 表示不重试。
    "retries": 3,
    
    # 每次重试之间的延迟时间，单位为秒。设置较长时间可以避免频繁请求。
    "delay": 30,
    
    # 文件下载保存的目录。所有下载的文件将保存在这个目录中。\\为正则表达式为了让电脑读取的所以必须保证这样。
    "save_dir": "E:\\modelsDownloads\\save",
    
    # 是否启用 hf_transfer。如果为 True，则启用 hf_transfer 进行下载，它可以加速下载过程。
    "use_hf_transfer": True,
    
    # Python 的本地路径。指定 Python 可执行文件的路径，用于运行相关的 Python 脚本。
    "python_path": "E:\\Python\\python.exe",
    
    # 连接超时时间，单位为秒。设置连接到服务器时的超时时间。
    "connect_timeout": 40,
    
    # 读取超时时间，单位为秒。设置从服务器读取数据时的超时时间。
    "read_timeout": 60,
    
    # Hugging Face CLI 路径。如果默认路径不正确，可以在这里进行调整。
    "huggingface_cli_path": "E:\\python\\Scripts\\huggingface-cli.exe"
}

# 镜像站点支持选项
# 这是一个字典，每个键是镜像站点的 URL，每个值是一个列表，包含该镜像站点支持的选项。
mirror_options = {
    # Hugging Face 官方站点，支持 resume_download 选项（断点续传）
    "https://huggingface.co": ["resume_download"],
    
    # Hugging Face 镜像站点，支持 resume_download 选项（断点续传）
    "https://hf-mirror.com": ["resume_download"],
    
    # 上海交通大学镜像站点，不支持任何特殊选项
    "https://mirror.sjtu.edu.cn": [],
    
    # 清华大学镜像站点，不支持任何特殊选项
    "https://mirrors.tuna.tsinghua.edu.cn": [],
    
    # 中国科学技术大学镜像站点，不支持任何特殊选项
    "https://mirrors.ustc.edu.cn": [],
    
    # Gitee 镜像站点，不支持任何特殊选项
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
