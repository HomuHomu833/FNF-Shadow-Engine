import os
import subprocess
import argparse
import shutil
import sys
import shutil as sh_util

temp_output = "temp_dds"

def get_texconv_path():
    """Return the path to texconv.exe in the same folder as this script."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    exe_name = "texconv.exe"
    texconv_path = os.path.join(script_dir, exe_name)
    if not os.path.isfile(texconv_path):
        print(f"Error: '{exe_name}' not found. Please install it from https://github.com/Microsoft/DirectXTex/releases")
        sys.exit(1)
    return texconv_path

def check_wine():
    """Check if wine is available on non-Windows systems."""
    if sh_util.which("wine") is None:
        print("Error: 'wine' not found on this system. Please install wine to run texconv.exe.")
        sys.exit(1)
    return "wine"

def run_command(command, use_wine=False):
    try:
        env = os.environ.copy()
        if use_wine:
            env["WINEDEBUG"] = "-all"
        subprocess.run(command, check=True, env=env)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")

def parse_args():
    parser = argparse.ArgumentParser(description="Compress images in a folder using texconv.")
    parser.add_argument('-i', '--input', required=True, help="Input folder containing PNG images.")
    parser.add_argument('-o', '--output', required=True, help="Output folder for DDS compressed images.")
    return parser.parse_args()

def main():
    args = parse_args()
    input_folder = args.input
    output_folder = args.output

    if not os.path.isdir(input_folder):
        print(f"The input folder '{input_folder}' does not exist.")
        return

    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(temp_output, exist_ok=True)

    texconv_tool = get_texconv_path()

    if os.name != "nt":
        wine_cmd = check_wine()
    else:
        wine_cmd = None

    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith(".png"):
                input_path = os.path.join(root, file)

                rel_path = os.path.relpath(root, input_folder)
                output_dir = os.path.join(output_folder, rel_path)
                os.makedirs(output_dir, exist_ok=True)

                final_dds_path = os.path.join(output_dir, os.path.splitext(file)[0] + ".dds")
                temp_dds_path = os.path.join(temp_output, os.path.splitext(file)[0] + ".dds")

                try:
                    command = [
                        texconv_tool,
                        "-f", "DXT5",
                        "-m", "1",
                        "-if", "CUBIC",
                        "-bc", "u",
                        "-y",
                        "-o", temp_output,
                        input_path
                    ]

                    if wine_cmd:
                        command = [wine_cmd] + command

                    print(f"Converting {file} -> {final_dds_path}...")
                    run_command(command)

                    if os.path.exists(temp_dds_path):
                        shutil.move(temp_dds_path, final_dds_path)
                    else:
                        print(f"Failed to find output DDS for {file}")

                except Exception as e:
                    print(f"Error processing image {input_path}: {e}")

    try:
        if os.path.exists(temp_output):
            shutil.rmtree(temp_output)
    except Exception as e:
        print(f"Could not remove temp folder: {e}")

    print("Processing complete.")

if __name__ == "__main__":
    main()
