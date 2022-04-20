from PIL import Image, ImageColor
import argparse
import os
from termcolor import colored
from datetime import datetime


parser = argparse.ArgumentParser(description="Hidden content in image tool")
parser.add_argument('--image', help='Path to image file',
                    required=True, type=str)
parser.add_argument('--content', help='Path to content file',
                    required=True, type=str)
parser.add_argument('--bits', help='Number of using low bits to write in pixels',
                    default=2, type=int)
parser.add_argument('--output', help='Path to output image file',
                    required=True, type=str)

def message(title, text, color, _exit=False):
    if not _exit:
        print(colored(title + ": " + text, color))
    else:
        exit(colored(title + ": " + text, color))

def rgb2int(rgb):
    r, g, b = rgb
    return ((r&0x0ff)<<16)|((g&0x0ff)<<8)|(b&0x0ff)

def int2rgb(value):
    r = (value>>16)&0x0ff;
    g = (value>>8) &0x0ff;
    b = (value)    &0x0ff;
    return (r, g, b)

if __name__ == "__main__":
    args = parser.parse_args()
    op = 1
    if not os.path.exists(args.image):
        message("Error", "Image file not found", "red", True)
    if not os.path.exists(args.content):
        message("Error", "Content file not found", "red", True)

    image_file_size = os.path.getsize(args.image)
    content_file_size = os.path.getsize(args.content)

    if content_file_size * 8 / args.bits > image_file_size * 8:
        message("Error", "Image is too small to keep this amount of data", "red", True)

    start_time = datetime.now()
    message(f"- Operation #{op}", f"Reading image file \"{args.image}\" [{image_file_size} Bytes]", "blue")
    op += 1
    image = Image.open(args.image)
    output_image = Image.new("RGB", (image.width, image.height), color='white')
    pixels = image.load()
    out_pixels = output_image.load()

    message(f"- Operation #{op}", f"Reading content file \"{args.content}\" [{content_file_size} Bytes]", "blue")
    op += 1
    file = open(args.content, "rb")

    message(f"- Operation #{op}", f"Reordering content bytes", "blue")
    op += 1
    file_bytes = file.read()
    file_bin = "".join([bin(x)[2:] for x in list(file_bytes)])
    splitted_bytes = [file_bin[index : index + args.bits] for index in range(0, len(file_bin), args.bits)]

    message(f"- Operation #{op}", f"Writing content to image", "blue")
    op += 1
    index = 0
    for y in range(0, image.height):
        for x in range(0, image.width):
            write_pixel = pixels[x, y]
            current_bin = bin(rgb2int(write_pixel))[2:]
            if index < len(splitted_bytes):
                current_bin_list = list(current_bin)
                current_bin_list[-len(splitted_bytes[index]):] = list(splitted_bytes[index])
                new_pixel = "".join(current_bin_list)
                write_pixel = int2rgb(int(new_pixel, 2))
                index += 1
            out_pixels[x, y] = write_pixel

    finish_time = datetime.now()
    time_took = (finish_time - start_time).total_seconds()
    message(f"- Operation #{op}", f"Done! output: \"{args.output}\"", "green")
    message(f"- Took: ", f"{time_took} sec", "green")
    op += 1

    output_image.save(args.output)
    file.close()
    image.close()
