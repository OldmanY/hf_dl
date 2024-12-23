import argparse
import os
import subprocess
import sys
import time
import requests
import random
import logging
import config  # 导入配置模块

# 设置日志
logging.basicConfig(filename='download_errors.log', level=logging.ERROR,
                    format='%(asctime)s %(levelname)s %(message)s')

# 从配置文件中获取配置选项和镜像站点支持选项
config_options = config.get_config()
mirror_options = config.get_mirror_options()

# 预定义的备用下载地址和镜像地址列表
download_endpoints = list(mirror_options.keys())

# 检查镜像站点支持的选项
def check_supported_options(mirror_url):
    # 返回镜像站点支持的选项列表
    return mirror_options.get(mirror_url, [])

def install_package(package_name):
    # 安装指定的 Python 包
    subprocess.check_call([config_options["python_path"], "-m", "pip", "install", package_name])

try:
    import huggingface_hub
except ImportError:
    print("Installing huggingface_hub...")
    install_package("huggingface_hub")

try:
    import hf_transfer
except ImportError:
    print("Installing hf_transfer...")
    install_package("hf_transfer")

parser = argparse.ArgumentParser(description="HuggingFace Download Accelerator Script.")
parser.add_argument("--model", "-M", default=None, type=str, help="Model name in HuggingFace, e.g., baichuan-inc/Baichuan2-7B-Chat")
parser.add_argument("--token", "-T", default=None, type=str, help="Hugging Face access token, e.g., hf_*****")
parser.add_argument("--include", default=None, type=str, help="Specify the file to be downloaded")
parser.add_argument("--exclude", default=None, type=str, help="Files you don't want to download")
parser.add_argument("--dataset", "-D", default=None, type=str, help="Dataset name in HuggingFace, e.g., zh-plus/tiny-imagenet")
parser.add_argument("--preferred_mirror", default=None, type=str, help="Preferred mirror URL for downloading")
args = parser.parse_args()

# 设置环境变量
if config_options["use_hf_transfer"]:
    os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
    print("export HF_HUB_ENABLE_HF_TRANSFER=", os.getenv("HF_HUB_ENABLE_HF_TRANSFER"))
else:
    os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "0"

if args.model is None and args.dataset is None:
    print("Specify the name of the model or dataset, e.g., --model baichuan-inc/Baichuan2-7B-Chat")
    exit(1)
elif args.model is not None and args.dataset is not None:
    print("Only one model or dataset can be downloaded at a time.")
    exit(1)

if args.token is not None:
    token_option = ["--token", args.token]
else:
    token_option = []

if args.include is not None:
    include_option = ["--include", args.include]
else:
    include_option = []

if args.exclude is not None:
    exclude_option = ["--exclude", args.exclude]
else:
    exclude_option = []

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# 确保保存目录存在
ensure_dir(config_options["save_dir"])

def remove_incomplete_files(directory):
    # 查找并删除所有 .incomplete 后缀的文件
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".incomplete"):
                os.remove(os.path.join(root, file))

def check_model_in_mirror(mirror_url, model_name):
    url = f"{mirror_url}/{model_name}"
    try:
        response = requests.head(url, timeout=(config_options["connect_timeout"], config_options["read_timeout"]))  # 使用配置中的超时时间
        if response.status_code == 200:
            print(f"Model {model_name} found at {mirror_url}")
            return True
        else:
            print(f"Model {model_name} not found at {mirror_url} (status code: {response.status_code})")
            return False
    except requests.RequestException as e:
        logging.error(f"Error accessing {mirror_url}: {e}")
        print(f"Error accessing {mirror_url}: {e}")
        return False

def run_command_with_retry(command, retries, delay, endpoints=None, model_name=None):
    if args.preferred_mirror:
        endpoints.insert(0, args.preferred_mirror)

    for endpoint in endpoints:
        os.environ["HF_ENDPOINT"] = endpoint
        print(f"Trying endpoint: {endpoint}")
        
        for attempt in range(retries):
            if not check_model_in_mirror(endpoint, model_name):
                print(f"Model {model_name} not found at {endpoint}. Skipping.")
                break
            
            # 检测支持的选项
            supported_options = check_supported_options(endpoint)
            try:
                # 动态构建下载命令
                dynamic_command = command.copy()
                dynamic_command.extend(supported_options)
                if config_options["force_download"]:
                    dynamic_command.append("--force-download")

                # 删除部分下载的文件
                if config_options["remove_incomplete"]:
                    remove_incomplete_files(config_options["save_dir"])
                
                # 打印当前执行的命令用于调试
                print(f"Executing command: {' '.join(dynamic_command)}")

                # 执行下载命令
                subprocess.run(dynamic_command, check=True)
                return True
            except subprocess.CalledProcessError as e:
                logging.error(f"Attempt {attempt + 1} failed: {e}")
                print(f"Attempt {attempt + 1} failed: {e}")
                if e.stderr and "Authentication required" in e.stderr:
                    print("Authentication required. Please provide username and password.")
                if attempt < retries - 1:
                    # 增加随机延迟，避免频繁请求
                    delay_time = delay + random.uniform(1, 5)
                    print(f"Retrying in {delay_time} seconds...")
                    time.sleep(delay_time)
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                logging.error(f"Connection error or timeout: {e}")
                print(f"Connection error or timeout: {e}")
                if attempt < retries - 1:
                    # 增加随机延迟，避免频繁请求
                    delay_time = delay + random.uniform(1, 5)
                    print(f"Retrying in {delay_time} seconds...")
                    time.sleep(delay_time)
    print("Download failed after multiple attempts.")
    return False

# 根据用户输入的模型或数据集名称构建下载命令
if args.model is not None:
    model_name = args.model
    save_path = os.path.join(config_options["save_dir"], f"models--{args.model.replace('/', '--')}")
    save_dir_option = ["--local-dir", save_path]

    huggingface_cli_path = config_options["huggingface_cli_path"]
    if not os.path.exists(huggingface_cli_path):
        logging.error(f"Hugging Face CLI not found at {huggingface_cli_path}")
        print(f"Hugging Face CLI not found at {huggingface_cli_path}")
        exit(1)

    base_download_command = [
        huggingface_cli_path, "download",
        *token_option,
        *include_option,
        *exclude_option,
        args.model,
        *save_dir_option
    ]

elif args.dataset is not None:
    model_name = args.dataset
    save_path = os.path.join(config_options["save_dir"], f"datasets--{args.dataset.replace('/', '--')}")
    save_dir_option = ["--local-dir", save_path]

    huggingface_cli_path = config_options["huggingface_cli_path"]
    if not os.path.exists(huggingface_cli_path):
        logging.error(f"Hugging Face CLI not found at {huggingface_cli_path}")
        print(f"Hugging Face CLI not found at {huggingface_cli_path}")
        exit(1)

    base_download_command = [
        huggingface_cli_path, "download",
        *token_option,
        *include_option,
        *exclude_option,
        "--repo-type", "dataset", args.dataset,
        *save_dir_option
    ]

# 执行带有重试逻辑的下载命令
if not run_command_with_retry(base_download_command, config_options["retries"], config_options["delay"], endpoints=download_endpoints, model_name=model_name):
    exit(1)
