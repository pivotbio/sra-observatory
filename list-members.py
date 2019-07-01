#!/usr/bin/env python3

import tarfile

TAR_PATH = "NCBI_SRA_Metadata_Full_20181005.tar.gz"

with open("members.txt", "w") as handle:
    with tarfile.open(TAR_PATH, "r:gz") as tar:
        members = list(tar.getmembers())
        print(len(members))
        for member in members:
            handle.write(member)
            handle.write("\n")
