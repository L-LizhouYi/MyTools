# Read Flac mutagen
import mutagen
# 指定FLAC文件
flac_file = "11. 稻香.flac"

# 从FLAC文件中读取元数据信息
flac_metadata = mutagen.File(flac_file)

# 打印所有元数据键
print(flac_metadata.keys())
