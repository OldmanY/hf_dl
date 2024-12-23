"""
@File      :hf_dl02.py
@Author:fayue yang
"""

import argparse
import os
import subprocess

def install_package(package_name):
    subprocess.check_call(["E:\\Python\\python.exe", "-m", "pip", "install", package_name])

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
parser.add_argument(
    "--model",
    "-M",
    default=None,
    type=str,
    help="model name in huggingface, e.g., baichuan-inc/Baichuan2-7B-Chat",
)
parser.add_argument(
    "--token",
    "-T",
    default=None,
    type=str,
    help="hugging face access token for download meta-llama/Llama-2-7b-hf, e.g., hf_***** ",
)
parser.add_argument(
    "--include",
    default=None,
    type=str,
    help="Specify the file to be downloaded",
)
parser.add_argument(
    "--exclude",
    default=None,
    type=str,
    help="Files you don't want to download",
)
parser.add_argument(
    "--dataset",
    "-D",
    default=None,
    type=str,
    help="dataset name in huggingface, e.g., zh-plus/tiny-imagenet",
)
parser.add_argument(
    "--save_dir",
    "-S",
    default=None,
    type=str,
    help="path to be saved after downloading.",
)
parser.add_argument(
    "--use_hf_transfer", default=True, type=eval, help="Use hf-transfer, default: True"
)
parser.add_argument(
    "--use_mirror", default=True, type=eval, help="Download from mirror, default: True"
)

args = parser.parse_args()

# Disable HF_HUB_ENABLE_HF_TRANSFER
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "0"

if args.use_mirror:
    os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
    print("export HF_ENDPOINT=", os.getenv("HF_ENDPOINT"))

if args.model is None and args.dataset is None:
    print("Specify the name of the model or dataset, e.g., --model baichuan-inc/Baichuan2-7B-Chat")
    exit(1)
elif args.model is not None and args.dataset is not None:
    print("Only one model or dataset can be downloaded at a time.")
    exit(1)

if args.token is not None:
    token_option = "--token"
    token_value = args.token
else:
    token_option = ""
    token_value = ""

if args.include is not None:
    include_option = "--include"
    include_value = args.include
else:
    include_option = ""
    include_value = ""

if args.exclude is not None:
    exclude_option = "--exclude"
    exclude_value = args.exclude
else:
    exclude_option = ""
    exclude_value = ""

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

if args.save_dir is not None:
    ensure_dir(args.save_dir)

if args.model is not None:
    model_name = args.model.split("/")
    save_dir_option = ""
    if args.save_dir is not None:
        if len(model_name) > 1:
            save_path = os.path.join(
                args.save_dir, "models--%s--%s" % (model_name[0], model_name[1])
            )
        else:
            save_path = os.path.join(
                args.save_dir, "models--%s" % (model_name[0])
            )
        save_dir_option = "--local-dir"
        save_dir_value = save_path

    download_shell = [
        "E:\\Python\\Scripts\\huggingface-cli.exe", "download",
        token_option, token_value,
        include_option, include_value,
        exclude_option, exclude_value,
        "--local-dir-use-symlinks", "False", "--resume-download", args.model,
        save_dir_option, save_dir_value
    ]

    # Remove empty string elements from the list
    download_shell = [arg for arg in download_shell if arg]

    subprocess.run(download_shell, check=True)

elif args.dataset is not None:
    dataset_name = args.dataset.split("/")
    save_dir_option = ""
    if args.save_dir is not None:
        if len(dataset_name) > 1:
            save_path = os.path.join(
                args.save_dir, "datasets--%s--%s" % (dataset_name[0], dataset_name[1])
            )
        else:
            save_path = os.path.join(
                args.save_dir, "datasets--%s" % (dataset_name[0])
            )
        save_dir_option = "--local-dir"
        save_dir_value = save_path

    download_shell = [
        "E:\\Python\\Scripts\\huggingface-cli.exe", "download",
        token_option, token_value,
        include_option, include_value,
        exclude_option, exclude_value,
        "--local-dir-use-symlinks", "False", "--resume-download",
        "--repo-type", "dataset", args.dataset,
        save_dir_option, save_dir_value
    ]

    # Remove empty string elements from the list
    download_shell = [arg for arg in download_shell if arg]

    subprocess.run(download_shell, check=True)