from mutagen.flac import FLAC, Picture
from mutagen.id3 import APIC, ID3, error
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4, AtomDataType, MP4Cover


def save_cover(file_path, image_path):
    audio = FLAC(file_path)
    image = Picture()
    image.type = 3
    image.mime = 'image/jpeg'
    image.desc = 'Cover (front)'
    with open(image_path, 'rb') as img:
        image.data = img.read()
    audio.add_picture(image)
    audio.save()


def save_cover_mp3(file_path, image_path):
    audio = MP3(file_path, ID3=ID3)
    try:
        audio.add_tags()
    except error:
        pass

    with open(image_path, 'rb') as img:
        audio.tags.add(
            APIC(
                encoding=3,
                mime='image/jpeg',
                type=3,
                desc='Cover (front)',
                data=img.read()
            )
        )

    audio.save()



def add_cover_to_m4a(m4a_file_path, cover_image_path):
    audio = MP4(m4a_file_path)

    # 读取封面图片文件
    with open(cover_image_path, 'rb') as img_file:
        img_data = img_file.read()

    # 创建一个 MP4Cover 对象，指定图片类型
    # AtomDataType.JPEG 或 AtomDataType.PNG 根据你的图片类型选择
    cover = MP4Cover(img_data, imageformat=AtomDataType.JPEG)

    # 添加封面到标签
    audio.tags['covr'] = [cover]

    # 保存更改
    audio.save()
