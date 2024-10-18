
from save_cover import add_cover_to_m4a, save_cover, save_cover_mp3

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Convert NCM files to standard format")
    parser.add_argument('-f', '--filename', required=True, help='audio file name')
    parser.add_argument('-i', '--image', required=True, help='image file path')
    args = parser.parse_args()

    print(args.filename)
    print(args.image)
    file_name = args.filename
    if file_name.endswith("flac"):
        save_cover(file_name, args.image)
    elif file_name.endswith("mp3"):
        save_cover_mp3(file_name, args.image)
    elif file_name.endswith('m4a'):
        add_cover_to_m4a(file_name, args.image)
    else:
        print('unkown file format:', file_name)