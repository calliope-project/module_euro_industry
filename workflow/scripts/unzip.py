"""Generic file unzipper."""
import sys
import zipfile
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    snakemake: Any
sys.stderr = open(snakemake.log[0], "w")



def unzip_path(input_path, output_path):
    """Download and unzip test files."""
    # If test suite has been downloaded, assume everything is OK.
    # Otherwise, cleanup and re-download.
    with zipfile.ZipFile(input_path, "r") as zfile:
        zfile.extractall(output_path)


if __name__ == "__main__":
    unzip_path(
        input_path=snakemake.input.zip_file,
        output_path=snakemake.output.file_dir
    )
