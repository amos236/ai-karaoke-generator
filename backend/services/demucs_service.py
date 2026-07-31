import subprocess
import os
import glob

OUTPUT_FOLDER = "ai_output"


def convert_to_karaoke(input_file: str):

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    print("\n===================================")
    print("Starting Demucs")
    print("Input :", input_file)
    print("===================================")

    command = [
        "python",
        "-m",
        "demucs",
        "--two-stems",
        "vocals",
        input_file,
        "-o",
        OUTPUT_FOLDER
    ]

    print("Running Command:")
    print(" ".join(command))

    process = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    print("\n========== DEMUCS STDOUT ==========")
    print(process.stdout)

    print("\n========== DEMUCS STDERR ==========")
    print(process.stderr)

    if process.returncode != 0:

        raise Exception(
            "Demucs Error:\n" + process.stderr
        )

    print("\nSearching output file...")

    files = glob.glob(

        os.path.join(
            OUTPUT_FOLDER,
            "**",
            "no_vocals.wav"
        ),

        recursive=True

    )

    if len(files) == 0:

        raise Exception(
            "Demucs finished but no_vocals.wav not found."
        )

    karaoke_file = files[0]

    print("\n===================================")
    print("Karaoke Created Successfully")
    print(karaoke_file)
    print("===================================")

    return karaoke_file


def delete_file(filepath):

    try:

        if filepath and os.path.exists(filepath):

            os.remove(filepath)

            print("Deleted :", filepath)

    except Exception as e:

        print("Delete Error :", e)