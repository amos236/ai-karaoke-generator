import subprocess
import os

OUTPUT_FOLDER = "ai_output"


def convert_to_karaoke(input_file):

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    command = [
        "demucs",
        "--two-stems",
        "vocals",
        input_file,
        "-o",
        OUTPUT_FOLDER
    ]

    print("\n==============================")
    print("Running Demucs...")
    print("Command:", " ".join(command))
    print("==============================")

    process = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    print(process.stdout)

    if process.returncode != 0:

        print(process.stderr)

        raise Exception(process.stderr)

    song_name = os.path.splitext(
        os.path.basename(input_file)
    )[0]

    karaoke_file = os.path.join(
        OUTPUT_FOLDER,
        "htdemucs",
        song_name,
        "no_vocals.wav"
    )

    if not os.path.exists(karaoke_file):

        raise Exception(
            "Karaoke file was not generated."
        )

    print("\n==============================")
    print("Karaoke created successfully.")
    print(karaoke_file)
    print("==============================")

    return karaoke_file