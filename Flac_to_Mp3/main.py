import os
import argparse
from pydub import AudioSegment
import mutagen
import eyed3
import logging

def is_flac_file(file_path):
    """检查文件是否为FLAC文件"""
    return file_path.lower().endswith('.flac')

def convert_single_flac_to_mp3(input_file, output_dir):
    """将单个FLAC文件转换为MP3"""
    if not is_flac_file(input_file):
        logging.warning(f"跳过非FLAC文件: {input_file}")
        return None

    file_name = os.path.splitext(os.path.basename(input_file))[0]
    output_file = os.path.join(output_dir, file_name + '.mp3')

    flac_audio = AudioSegment.from_file(input_file, format="flac")
    original_bitrate = flac_audio.frame_rate
    original_sample_width = flac_audio.sample_width
    original_channels = flac_audio.channels

    mp3_audio = flac_audio.set_frame_rate(original_bitrate)
    mp3_audio = mp3_audio.set_sample_width(original_sample_width)
    mp3_audio = mp3_audio.set_channels(original_channels)

    mp3_audio.export(output_file, format="mp3", bitrate=f"{original_bitrate}k")
    return output_file

def copy_metadata(input_flac_file, output_mp3_file):
    """复制FLAC文件的元数据到MP3文件"""
    flac_metadata = mutagen.File(input_flac_file, easy=True)
    mp3_tag = eyed3.load(output_mp3_file)

    mp3_tag.tag.artist = flac_metadata["artist"][0]
    mp3_tag.tag.album = flac_metadata["album"][0]
    mp3_tag.tag.title = flac_metadata["title"][0]
    mp3_tag.tag.track_num = flac_metadata["tracknumber"][0]

    mp3_tag.tag.save()

def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description="将FLAC文件转换为MP3")

    # 添加源文件/目录参数
    parser.add_argument("source", help="源文件或目录")

    # 解析命令行参数
    args = parser.parse_args()

    # 检查输出目录是否存在，如果不存在则创建
    output_dir = os.path.join(os.getcwd(), 'Out_' + os.path.basename(os.path.normpath(args.source)))
    os.makedirs(output_dir, exist_ok=True)

    if os.path.isfile(args.source):
        output_file = convert_single_flac_to_mp3(args.source, output_dir)
        if output_file:
            copy_metadata(args.source, output_file)
            logging.info(f"{args.source}: 转换成功")
    elif os.path.isdir(args.source):
        for root, dirs, files in os.walk(args.source):
            for file in files:
                file_path = os.path.join(root, file)
                output_file = convert_single_flac_to_mp3(file_path, output_dir)
                if output_file:
                    copy_metadata(file_path, output_file)
                    logging.info(f"{file_path}: 转换成功")
    else:
        logging.error(f"无效的输入: {args.source}")

if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    main()
