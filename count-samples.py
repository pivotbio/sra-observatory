#!/usr/bin/env python3

from load import load_sample_data, TAR_PATH
import tarfile

import xml.etree.ElementTree

def main():

    # clear pre-existing data

    samples_count = 0
    with tarfile.open(TAR_PATH, "r:gz") as tar:
        for n, member in enumerate(tar):
            h = tar.extractfile(member)

            if h is not None:

                if "sample" in member.name:
                    with tar.extractfile(member) as handle:
                        root = xml.etree.ElementTree.parse(handle)
                        for _id, sample_data in load_sample_data(root):
                            samples_count += 1
                            print(samples_count)

if __name__ == "__main__":
    main()
