#!/usr/bin/env python3
#
# Downloads artifacts from a build of tf-m-build-and-test
#

__copyright__ = """
/*
 * Copyright (c) 2020, Arm Limited. All rights reserved.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 *
 */
 """

import requests
import argparse
import os
from urllib.parse import urljoin
from html.parser import HTMLParser


class UrlExtracter(HTMLParser):
    def __init__(self):
        super().__init__()
        self.last_tag = None
        self.last_link = None
        self.last_config = None
        self.build_artifacts = {}
        self.build_logs = {}

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key == "href":
                self.last_link = value
        self.last_tag = tag

    def handle_endtag(self, tag):
        if tag == "br":
            self.last_tag = None

    def handle_data(self, data):
        if not self.last_tag:
            self.last_config = data.replace(": ", "").replace("\n", "")
            return

        if self.last_tag == "a":
            if data == "Artifacts":
                self.build_artifacts[self.last_config] = self.last_link
            elif data == "Logs":
                self.build_logs[self.last_config] = self.last_link


def download_artifacts(url, save_dir):
    if not url.endswith("/"):
        url += "/"
    job_page_req = requests.get(url)
    if job_page_req.status_code != requests.codes.ok:
        print("Issue contacting given URL")
        return
    print("Found build")
    build_links_req = requests.get(urljoin(url, "artifact/build_links.html"))
    if build_links_req.status_code != requests.codes.ok:
        print("Given build did not have an artifact called `build_links.html`")
        return
    parser = UrlExtracter()
    print("Extracting links from build_links.html")
    parser.feed(build_links_req.text)
    print("Links found")
    if not os.path.exists(save_dir):
        print("Creating directory at {}".format(save_dir))
        os.makedirs(save_dir)
    else:
        print("Reusing directory at {}.")
    for config, log_url in parser.build_logs.items():
        print("Downloading {}".format(log_url))
        log_req = requests.get(log_url)
        log_file_path = os.path.join(save_dir, "{}.log".format(config))
        with open(log_file_path, "w") as log_file:
            log_file.write(log_req.text)
        print("Saved log to {}".format(log_file_path))
    for config, artifacts_url in parser.build_artifacts.items():
        zip_url = urljoin(artifacts_url, "*zip*/archive.zip")
        print("Downloading {}".format(zip_url))
        artifact_zip_req = requests.get(zip_url, stream=True)
        zip_file = os.path.join(save_dir, "{}.zip".format(config))
        with open(zip_file, "wb") as artifact_zip:
            for chunk in artifact_zip_req.iter_content(chunk_size=8192):
                artifact_zip.write(chunk)
        print("Saved artifacts zip to {}".format(zip_file))
    print("Finished")


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "job_url", help="Url to a completed build of tf-m-build-and-test"
    )
    argparser.add_argument(
        "-o", "--output_dir", default="artifacts", help="Location to save artifacts to."
    )
    args = argparser.parse_args()
    download_artifacts(args.job_url, args.output_dir)


if __name__ == "__main__":
    main()
