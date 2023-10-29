import base64
import functools
import json
import os
import pathlib
import shutil
import sys
import urllib.error
import urllib.request
from typing import List, Optional

NEXUS_URL = "https://pkgs.nathanv.app"
NEXUS_USERNAME = os.environ["NEXUS_USERNAME"]
NEXUS_PASSWORD = os.environ["NEXUS_PASSWORD"]

base64_auth_string = base64.b64encode(
    bytes(f"{NEXUS_USERNAME}:{NEXUS_PASSWORD}", "ascii")
).decode("utf-8")
AUTHORIZATION_HEADER = f"Basic {base64_auth_string}"


def split_string(string: str) -> List[str]:
    """
    Split a string, maintaining items in square brackets
    """
    split_list = string.split(" ")
    result = []
    temp = ""
    open_bracket = False

    for element in split_list:
        if element.startswith("["):
            open_bracket = True

        if open_bracket:
            temp += f"{element} "
        else:
            result.append(element)

        if element.endswith("]"):
            open_bracket = False
            result.append(temp.strip())
            temp = ""

    # filter out empty items
    return [r for r in result if r]


@functools.lru_cache(maxsize=None)
def get_or_create_repo_name(upstream_url: str, distribution: str) -> str:
    """
    Get or create a repository from Nexus
    """
    repo_name = upstream_url.split("://")[1].replace("/", "-")

    # handle empty distro
    if distribution != "/":
        repo_name = f"{repo_name}_{distribution}"

    # see if repo exists
    get_request = urllib.request.Request(
        f"{NEXUS_URL}/service/rest/v1/repositories/apt/proxy/{repo_name}",
        headers={"Authorization": AUTHORIZATION_HEADER},
    )

    try:
        get_response = urllib.request.urlopen(get_request)
        if get_response.getcode() == 200:
            return repo_name
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise e

    # if not, create it
    print(f"Creating {repo_name}")
    post_request = urllib.request.Request(
        f"{NEXUS_URL}/service/rest/v1/repositories/apt/proxy",
        data=json.dumps(
            {
                "name": repo_name,
                "online": True,
                "storage": {
                    "blobStoreName": "default",
                    "strictContentTypeValidation": True,
                },
                "cleanup": {"policyNames": ["60-day-unused-cleanup"]},
                "proxy": {
                    "remoteUrl": upstream_url,
                    "contentMaxAge": 1440,
                    "metadataMaxAge": 1440,
                },
                "negativeCache": {"enabled": True, "timeToLive": 1440},
                "httpClient": {"blocked": False, "autoBlock": True},
                "apt": {"distribution": distribution, "flat": False},
            }
        ).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": AUTHORIZATION_HEADER,
        },
        method="POST",
    )
    urllib.request.urlopen(post_request)

    return repo_name


def process_line(line: str) -> Optional[str]:
    """
    Rewrites a single line of an apt source file.
    """
    # skip if the line is commented out
    if not line or line[0] == "#":
        return

    # split the source string into distinct chunks
    chunks = split_string(line)

    # index of the chunk that contains the url
    url_chunk_index = next(
        i for i, chunk in enumerate(chunks) if chunk.startswith("http")
    )

    # get the url
    url = chunks[url_chunk_index]
    # remove trailing slash with python 3.7 compatibility
    if url.endswith("/"):
        url = url[:-1]

    # get the distro
    distro = chunks[url_chunk_index + 1]

    # skip if it's already been processed
    if url.startswith(NEXUS_URL):
        return

    repo_name = get_or_create_repo_name(url, distro)
    new_url = f"{NEXUS_URL}/repository/{repo_name}"

    if not new_url.endswith("/"):
        new_url += "/"

    # reassemble
    print(f"\t Rewriting {url}")
    return " ".join(
        chunks[:url_chunk_index] + [new_url] + chunks[url_chunk_index + 1 :]
    )


def process_file(fileobj: pathlib.Path) -> bool:
    """
    Rewrites an apt sources file. Returns if changes were made.
    """
    print(f"Processing {fileobj.absolute()}")

    # create name for original copy of file
    backup_file = fileobj.parent.joinpath(f"{fileobj.name}.orig").absolute()

    # see if a backup already exists
    if backup_file.exists():
        return False

    # read file
    with open(fileobj, "r") as fp:
        original_lines = [l.strip() for l in fp.readlines()]

    # generate new lines
    new_lines = []

    for original_line in original_lines:
        result = process_line(original_line)
        if result is None:
            new_lines.append(original_line)
        else:
            new_lines.append(result)

    # skip if output is same
    if new_lines == original_lines:
        return False

    # create backup
    shutil.copyfile(fileobj, backup_file)

    # write new file
    with open(fileobj, "w") as fp:
        fp.writelines([f"{l}\n" for l in new_lines])

    return True


def main() -> bool:
    # record if we have made changes
    changes_made = False

    for source_list in pathlib.Path("/etc/apt/").glob("**/*.list"):
        # skip google chrome
        if "google" in source_list.name and "chrome" in source_list.name:
            continue
        # skip ubuntu esm
        if "ubuntu" in source_list.name and "esm" in source_list.name:
            continue

        # if a change was made, set that
        result = process_file(source_list)
        if result:
            changes_made = True

    return changes_made


if __name__ == "__main__":
    sys.exit(int(main()))
