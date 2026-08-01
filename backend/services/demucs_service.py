import os
import glob
import shutil
import subprocess

OUTPUT_FOLDER = "ai_output"


def convert_to_karaoke(input_file: str):
    """
    Converts an MP3 into karaoke (no vocals)
    using Demucs and returns the generated file path.
    """

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # ---------------------------------
    # Clean previous output
    # ---------------------------------
    for item in os.listdir(OUTPUT_FOLDER):
        path = os.path.join(OUTPUT_FOLDER, item)

        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
        except Exception:
            pass

    # ---------------------------------
    # Original filename
    # ---------------------------------
    original_name = os.path.splitext(
        os.path.basename(input_file)
    )[0]

    print("\n===================================")
    print("DEMUCS START")
    print("Input :", input_file)
    print("===================================")

    command = [
        "python",
        "-m",
        "demucs.separate",
        "--two-stems",
        "vocals",
        "-o",
        OUTPUT_FOLDER,
        input_file
    ]

    print("Running Command:")
    print(" ".join(command))

    process = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    print("\n========== STDOUT ==========")
    print(process.stdout)

    print("\n========== STDERR ==========")
    print(process.stderr)

    if process.returncode != 0:
        raise Exception(
            "Demucs failed.\n\n" +
            process.stderr
        )

    # ---------------------------------
    # Search generated no_vocals.wav
    # ---------------------------------
    files = glob.glob(
        os.path.join(
            OUTPUT_FOLDER,
            "**",
            "no_vocals.wav"
        ),
        recursive=True
    )

    if not files:
        raise Exception("no_vocals.wav not found.")

    generated_file = max(
        files,
        key=os.path.getmtime
    )

    # ---------------------------------
    # Rename output
    # ---------------------------------
    final_output = os.path.join(
        OUTPUT_FOLDER,
        f"{original_name}_Karaoke.wav"
    )

    shutil.copy2(generated_file, final_output)

    print("\n===================================")
    print("SUCCESS")
    print(final_output)
    print("===================================")

    return final_output


def delete_file(filepath):
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            print("Deleted :", filepath)
    except Exception as e:
        print(e)