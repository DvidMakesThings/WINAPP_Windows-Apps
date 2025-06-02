import argparse
import os
from PIL import Image

def convert_to_ico(input_file, output_file="output.ico"):
    """Convert an image to ICO format."""
    try:
        img = Image.open(input_file)
        img = img.resize((256, 256), Image.LANCZOS)
        img.save(output_file, format="ICO")
        print(f"Converted '{input_file}' to '{output_file}'")
    except Exception as e:
        print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Convert an image to ICO format."
    )
    parser.add_argument("image", help="Path to the input image (PNG, JPG, etc.)")
    parser.add_argument("-o", "--output", help="Output ICO filename (default: output.ico)", default="output.ico")
    parser.add_argument("--delete", action="store_true", help="Delete the original image after conversion")
    
    args = parser.parse_args()
    
    convert_to_ico(args.image, args.output)

    if args.delete:
        os.remove(args.image)
        print(f"🗑 Deleted original image: {args.image}")

if __name__ == "__main__":
    main()