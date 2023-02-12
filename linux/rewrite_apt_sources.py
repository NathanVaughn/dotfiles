import pathlib
from typing import Optional


def process_line(line: str) -> Optional[str]:
    """
    Rewrites a single line of an apt source file.
    """
    line = line.lstrip()

    # skip if the line is commented out
    if not line or line[0] == "#":
        return

    chunks = line.split()

    url_chunk_index = next(
        i for i, chunk in enumerate(chunks) if chunk.startswith("http")
    )

    url = chunks[url_chunk_index].removesuffix("/")
    distro = chunks[url_chunk_index + 1]

    if url.startswith("https://pkgs.nthnv.me"):
        return

    # rewrite url
    print(f"\t Rewriting {url}")
    new_url = (
        f'https://pkgs.nthnv.me/repository/{url.split("://")[1].replace("/", "-")}'
    )

    if distro != "/":
        new_url = f"{new_url}_{distro}"

    if not new_url.endswith("/"):
        new_url += "/"

    # reassemble
    return (
        " ".join(chunks[:url_chunk_index] + [new_url] + chunks[url_chunk_index + 1 :])
        + "\n"
    )


def process_file(fileobj: pathlib.Path) -> None:
    """
    Rewrites an apt sources file in-place.
    """
    print(f"Processing {fileobj.absolute()}")

    with open(fileobj, "r") as fp:
        original_lines = fp.readlines()

    new_lines = []

    for original_line in original_lines:
        result = process_line(original_line)

        # if no changes found, continue
        if result is None:
            new_lines.append(original_line)
            continue

        # if change found, comment out existing line
        new_lines.extend((result, f"# {original_line}"))

    with open(fileobj, "w") as fp:
        fp.writelines(new_lines)


def main():
    for source_list in pathlib.Path("/etc/apt/").glob("**/*.list"):
        process_file(source_list)


if __name__ == "__main__":
    main()
