import base64
import binascii
import json
import os
import struct
import warnings
from uuid import uuid4

import requests
from Crypto.Cipher import AES

from save_cover import save_cover, save_cover_mp3


def download_pic(url, save_fn):
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/100.0.4896.127 Safari/537.36"
    }
    response = requests.get(url=url, headers=headers)
    with open(save_fn, 'wb') as f:
        f.write(response.content)


def dump(file_path, output_dir):
    core_key = binascii.a2b_hex("687A4852416D736F356B496E62617857")
    meta_key = binascii.a2b_hex("2331346C6A6B5F215C5D2630553C2728")
    unpad = lambda s: s[0:-(s[-1] if type(s[-1]) == int else ord(s[-1]))]
    f = open(file_path, 'rb')
    header = f.read(8)
    assert binascii.b2a_hex(header) == b'4354454e4644414d'
    f.seek(2,1)
    key_length = f.read(4)
    key_length = struct.unpack('<I', bytes(key_length))[0]
    key_data = f.read(key_length)
    key_data_array = bytearray(key_data)
    for i in range(0, len(key_data_array)):
        key_data_array[i] ^= 0x64
    key_data = bytes(key_data_array)
    cryptor = AES.new(core_key, AES.MODE_ECB)
    key_data = unpad(cryptor.decrypt(key_data))[17:]
    key_length = len(key_data)
    key_data = bytearray(key_data)
    key_box = bytearray(range(256))
    c = 0
    last_byte = 0
    key_offset = 0
    for i in range(256):
        swap = key_box[i]
        c = (swap + last_byte + key_data[key_offset]) & 0xff
        key_offset += 1
        if key_offset >= key_length:
            key_offset = 0
        key_box[i] = key_box[c]
        key_box[c] = swap
        last_byte = c
    meta_length = f.read(4)
    meta_length = struct.unpack('<I', bytes(meta_length))[0]
    meta_data = f.read(meta_length)
    meta_data_array = bytearray(meta_data)
    for i in range(0, len(meta_data_array)):
        meta_data_array[i] ^= 0x63
    meta_data = bytes(meta_data_array)
    meta_data = base64.b64decode(meta_data[22:])
    cryptor = AES.new(meta_key, AES.MODE_ECB)
    meta_data = unpad(cryptor.decrypt(meta_data)).decode('utf-8')[6:]
    meta_data = json.loads(meta_data)
    cover_url = meta_data['albumPic']
    crc32 = f.read(4)
    crc32 = struct.unpack('<I', bytes(crc32))[0]
    f.seek(5, 1)
    image_size = f.read(4)
    image_size = struct.unpack('<I', bytes(image_size))[0]
    image_data = f.read(image_size)
    file_name = os.path.join(output_dir, os.path.basename(f.name).split(".ncm")[0] + '.' + meta_data['format'])
    m = open(file_name, 'wb')
    chunk = bytearray()
    while True:
        chunk = bytearray(f.read(0x8000))
        chunk_length = len(chunk)
        if not chunk:
            break
        for i in range(1, chunk_length+1):
            j = i & 0xff
            chunk[i-1] ^= key_box[(key_box[j] + key_box[(key_box[j] + j) & 0xff]) & 0xff]
        m.write(chunk)
    m.close()
    f.close()
    if cover_url.endswith("jpg"):
        image_name_uuid = uuid4()
        save_cover_jpg_name = f"./cache_image/{image_name_uuid}.jpg"
        download_pic(cover_url, save_cover_jpg_name)
        if file_name.endswith("flac"):
            save_cover(file_name, save_cover_jpg_name)
        else:
            save_cover_mp3(file_name, save_cover_jpg_name)
    else:
        warnings.warn(f"图片不是jpg格式 不支持添加封面: {cover_url}")

    return file_name

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Convert NCM files to standard format")
    parser.add_argument('-p', '--path', required=True, help='Path to the directory containing NCM files')
    parser.add_argument('-o', '--output', required=True, help='Output directory for converted files')
    args = parser.parse_args()

    if not os.path.exists(args.output):
        os.makedirs(args.output)

    for file in os.listdir(args.path):
        if file.endswith('.ncm'):
            file_path = os.path.join(args.path, file)
            try:
                converted_file = dump(file_path, args.output)
                print(f"{file_path} converted successfully to {converted_file}")
            except Exception as e:
                print(f"Error converting {file_path}: {e}")