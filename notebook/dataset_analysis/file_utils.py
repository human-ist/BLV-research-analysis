from pathlib import Path

def get_filename(filepath: str):
    return Path(filepath).name


def get_file_extension(filename_or_path: str):
    """
    Get the extension of a file or a filepath.
    - img.jpg -> jpg
    """
    return Path(filename_or_path).suffix[1:]


def rename_with_clust(filepath: str, cluster:str) -> str:
    cluster_id = cluster[0] # First char
    file_ext = get_file_extension(filepath)
    cluster_filepath = filepath.replace(file_ext, '_clust' + cluster_id + file_ext)
    return cluster_filepath