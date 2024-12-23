Several test versions of hf_dl.py. config.py is an auxiliary script of hf_dl05.py. Your parameters and options are set in config.py.

I am a novice. When I use ComfyUI, I always use other people's integration packages. I feel that it is particularly difficult to download models and environment support with the integration package.
Environment support can also be solved directly using python, which is relatively easy to learn the solution.
However, I don't quite understand the principle of using the integration package to download models.
So the day before yesterday, I saw someone else's download script, but I tested it for 3 days and still couldn't use it. Maybe I am a fool.
So I made one myself based on the reference. I would like to thank @Author: Xiaojian Yuan/hf_download.py.
But after seeing @Author: padeoe/hfd.md today. I thought I wasted half a day again and gave up.


使用说明

项目结构
config.py：包含所有可配置的选项和镜像站点支持选项。
main_script.py：主脚本，用于根据配置和用户输入执行下载任务。
配置文件 (config.py)
在 config.py 文件中包含以下配置选项：

force_download：是否强制重新下载文件。默认为 False。
remove_incomplete：是否删除部分下载的文件。默认为 False。
retries：下载失败时的重试次数。默认为 3。
delay：每次重试之间的延迟时间，单位为秒。默认为 30。
save_dir：文件下载保存的目录。默认为 E:\\modelsDownloads\\save。
use_hf_transfer：是否启用 hf_transfer。默认为 True。
python_path：Python 的本地路径。默认为 E:\\Python\\python.exe。
此外，还包含镜像站点及其支持的选项：

Python
mirror_options = {
    "https://huggingface.co": ["resume_download"],
    "https://hf-mirror.com": ["resume_download"],
    "https://mirror.sjtu.edu.cn": [],
    "https://mirrors.tuna.tsinghua.edu.cn": [],
    "https://mirrors.ustc.edu.cn": [],
    "https://gitee.com": []
}
主脚本 (main_script.py)
主脚本读取 config.py 中的配置选项和镜像站点支持选项，并根据用户输入执行下载任务。

命令行参数
主脚本支持以下命令行参数：

--model, -M：在 HuggingFace 上的模型名称，例如 baichuan-inc/Baichuan2-7B-Chat。
--token, -T：Hugging Face 访问令牌，例如 hf_*****。
--include：指定要下载的文件。
--exclude：指定不想下载的文件。
--dataset, -D：在 HuggingFace 上的数据集名称，例如 zh-plus/tiny-imagenet。
--preferred_mirror：优先使用的镜像站点 URL。
环境变量
HF_HUB_ENABLE_HF_TRANSFER：根据 config.py 中的 use_hf_transfer 配置设置。


示例命令
示例 1：下载模型
E:\Python\python.exe main_script.py --model baichuan-inc/Baichuan2-7B-Chat --token hf_***** --preferred_mirror https://hf-mirror.com
此命令将下载指定的模型到配置文件中指定的保存目录，并优先使用 https://hf-mirror.com 镜像站点。

示例 2：下载数据集
E:\Python\python.exe main_script.py --dataset zh-plus/tiny-imagenet --token hf_***** --include data.zip
此命令将下载指定的数据集文件 data.zip 到配置文件中指定的保存目录。

示例 3：强制重新下载
在 config.py 中设置 force_download 为 True，然后运行以下命令：

E:\Python\python.exe main_script.py --model baichuan-inc/Baichuan2-7B-Chat --token hf_***** --preferred_mirror https://hf-mirror.com
此命令将强制重新下载指定的模型。

示例 4：删除部分下载文件
在 config.py 中设置 remove_incomplete 为 True，然后运行以下命令：

E:\Python\python.exe main_script.py --dataset zh-plus/tiny-imagenet --token hf_***** --preferred_mirror https://hf-mirror.com
此命令将删除保存目录中所有部分下载的文件，然后重新下载指定的数据集。

通过这些说明和示例，你可以根据需要配置和执行下载任务。如果有任何问题或需要进一步的帮助，请随时告诉我！
