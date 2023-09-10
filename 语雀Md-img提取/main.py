import os
import re
import urllib.request
import argparse

def extract_image_urls_from_md(md_content):
    # 正则表达式匹配图片链接
    pattern = r"!\[.*\]\((.*?)\)"
    image_urls = re.findall(pattern, md_content)

    # 去除链接后面的参数部分
    cleaned_image_urls = [url.split('#')[0] for url in image_urls]

    return cleaned_image_urls

def download_image(url, image_path, total_images, image_idx):
    with urllib.request.urlopen(url) as response, open(image_path, 'wb') as out_file:
        total_size = int(response.info().get('Content-Length'))
        downloaded_size = 0
        chunk_size = 8192
        while True:
            data = response.read(chunk_size)
            if not data:
                break
            downloaded_size += len(data)
            out_file.write(data)
            progress = downloaded_size / total_size * 100
            print(f"\rDownloading image {image_idx}/{total_images} - {progress:.2f}% completed", end="")

def download_images_to_folder(image_urls, folder_path):
    total_images = len(image_urls)
    image_names = []
    for idx, url in enumerate(image_urls, 1):
        image_name = os.path.basename(url)
        image_path = os.path.join(folder_path, image_name)
        download_image(url, image_path, total_images, idx)
        image_names.append(image_name)
    print("\nDownload completed.")
    return image_names

def replace_image_urls_with_filenames(md_content, image_names):
    for idx, url in enumerate(re.findall(r"!\[.*\]\((.*?)\)", md_content), 1):
        md_content = md_content.replace(url, image_names[idx - 1])
    return md_content

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download images from Markdown file and replace URLs with filenames.")
    parser.add_argument("md_file_path", help="Path to the Markdown file")
    args = parser.parse_args()

    # 读取Markdown文件内容
    with open(args.md_file_path, "r", encoding="utf-8") as file:
        md_content = file.read()

    # 提取图片链接
    image_urls = extract_image_urls_from_md(md_content)

    # 获取Markdown文件名（不包含扩展名）
    md_file_name = os.path.splitext(os.path.basename(args.md_file_path))[0]

    # 创建与Markdown文件同名的文件夹
    output_folder = f"{md_file_name}_images"
    os.makedirs(output_folder, exist_ok=True)

    # 下载图片并获取图片文件名列表
    image_names = download_images_to_folder(image_urls, output_folder)

    # 将Markdown中的图片地址替换为文件名
    modified_md_content = replace_image_urls_with_filenames(md_content, image_names)

    # 将修改后的Markdown保存到下载路径下的index.md文件
    output_file_path = os.path.join(output_folder, "index.md")
    with open(output_file_path, "w", encoding="utf-8") as file:
        file.write(modified_md_content)

    print("Images downloaded and Markdown file modified successfully.")
