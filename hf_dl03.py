"""
@File      :hf_dl03.py
@Author:fayue yang
"""

import argparse
import os
import subprocess
import sys
import time
import requests

# 预定义的备用下载地址和镜像地址列表
download_endpoints = [
    "https://huggingface.co",
    "https://hf-mirror.com",
    "https://mirror.sjtu.edu.cn",
    "https://mirrors.tuna.tsinghua.edu.cn",
    "https://mirrors.ustc.edu.cn",
    "https://gitee.com"
]

def install_package(package_name):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

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
parser.add_argument("--save_dir", "-S", default=None, type=str, help="Path to be saved after downloading")
parser.add_argument("--use_hf_transfer", default=True, type=eval, help="Use hf-transfer, default: True")
parser.add_argument("--use_mirror", default=True, type=eval, help="Download from mirror, default: True")
parser.add_argument("--username", default=None, type=str, help="Username for authentication if required")
parser.add_argument("--password", default=None, type=str, help="Password for authentication if required")
args = parser.parse_args()

# 设置环境变量
if args.use_hf_transfer:
    os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
    print("export HF_HUB_ENABLE_HF_TRANSFER=", os.getenv("HF_HUB_ENABLE_HF_TRANSFER"))

# 禁用 hf_transfer
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

if args.save_dir is not None:
    ensure_dir(args.save_dir)

def check_model_in_mirror(mirror_url, model_name):
    url = f"{mirror_url}/{model_name}"
    try:
        response = requests.head(url, timeout=10)
        if response.status_code == 200:
            print(f"Model {model_name} found at {mirror_url}")
            return True
        else:
            print(f"Model {model_name} not found at {mirror_url} (status code: {response.status_code})")
            return False
    except requests.RequestException as e:
        print(f"Error accessing {mirror_url}: {e}")
        return False

def run_command_with_retry(command, retries=3, delay=30, endpoints=None, model_name=None):
    for endpoint in endpoints:
        os.environ["HF_ENDPOINT"] = endpoint
        print(f"Trying endpoint: {endpoint}")
        if not check_model_in_mirror(endpoint, model_name):
            print(f"Model {model_name} not found at {endpoint}. Skipping.")
            continue
        for attempt in range(retries):
            try:
                # Execute the download command
                subprocess.run(command, check=True)
                return True
            except subprocess.CalledProcessError as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if "Authentication required" in e.stderr:
                    print("Authentication required. Please provide username and password.")
                if attempt < retries - 1:
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
            except requests.exceptions.ReadTimeout:
                print(f"Read timeout error for endpoint {endpoint}. Retrying in {delay} seconds...")
                time.sleep(delay)
    print("Download failed after multiple attempts.")
    return False

# Determine the model or dataset name and construct the command
if args.model is not None:
    model_name = args.model
    if args.save_dir is not None:
        save_path = os.path.join(args.save_dir, f"models--{args.model.replace('/', '--')}")
        save_dir_option = ["--local-dir", save_path]
    else:
        save_dir_option = []

    download_command = [
        "E:\\Python\\Scripts\\huggingface-cli.exe", "download",
        *token_option,
        *include_option,
        *exclude_option,
        "--local-dir-use-symlinks", "False", "--resume-download", args.model,
        *save_dir_option
    ]

elif args.dataset is not None:
    model_name = args.dataset
    if args.save_dir is not None:
        save_path = os.path.join(args.save_dir, f"datasets--{args.dataset.replace('/', '--')}")
        save_dir_option = ["--local-dir", save_path]
    else:
        save_dir_option = []

    download_command = [
        "E:\\Python\\Scripts\\huggingface-cli.exe", "download",
        *token_option,
        *include_option,
        *exclude_option,
        "--local-dir-use-symlinks", "False", "--resume-download",
        "--repo-type", "dataset", args.dataset,
        *save_dir_option
    ]

# Execute the download command with retry logic
if not run_command_with_retry(download_command, endpoints=download_endpoints, model_name=model_name):
    exit(1)