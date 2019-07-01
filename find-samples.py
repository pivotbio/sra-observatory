#!/usr/bin/env python3

from models import get_database
import re

db = get_database()


def munge_item(item):
    if type(item) == list:
        return ";".join(i for i in item).replace(",", "_").replace("\n", "")
    else:
        return str(item).replace(",", "_").replace("\n", "")


def list_of_dictionaries_to_csv(lod, out_handle, sep=","):
    """
    Outputs a list of dictionaries to a CSV
    """

    lod = list(lod)

    headers = set()

    for row in lod:
        for k in row.keys():
            headers.add(k)

    headers = sorted([str(h) for h in headers])

    out_handle.write(sep.join(h for h in headers))
    out_handle.write("\n")

    for row in lod:

        assert len(headers) == len(row), row

        # if a row is an array, just get the first item in the array?
        out_handle.write(sep.join([munge_item(row.get(h, "")) for h in headers]))
        out_handle.write("\n")


def munge_lat_lon(lat_lon):
    regexes = {
        r"(?P<x>-?\d*\.\d*)\s*(?P<ns>[NS]),?\s*(?P<y>-?\d*\.\d*)\s*(?P<ew>[EW])": 1,
        r"(\d*)°\s*(\w),\s*(\d*)°\s*(\w)": 2,
        r"([NS])([\d\.]*)\s*([EW])([\d\.]*)": 3,
        r"(-?\d*\.\d*)[\s,]*(-?\d*\.\d*)": 4,
        r"\(([NS]):([EW])\) (-?\d*\.\d*):(-?\d*\.\d*)": 5,
    }

    if lat_lon in {
        "not applicable",
        "missing",
        "not collected",
        "Missing",
        "NA",
        "not available",
        "Not Collected",
    }:
        return None
    else:
        for regex, regex_id in regexes.items():
            # need to use named groups!
            if re.match(regex, lat_lon):
                if regex_id == 1:
                    m = re.match(regex, lat_lon)
                    return m.groupdict()
    return lat_lon


query = """
select
  experiment.id as experiment_accession,
  sample.id as sample_accession,
  sample.scientific_name,
  sample.taxid,
  run.id as run_accession,
  scientific_name,
  experiment.library_name,
  experiment.library_strategy,
  experiment.library_source,
  experiment.library_selection,
  experiment.library_layout,
  experiment.platform_type,
  experiment.platform_instrument_model,
  run.title,
  attributes->'lat_lon' as lat_lon,
  attributes->'geo_loc_name' as geo_loc_name
from
  experiment
left join
  sample
on
  experiment.sample_accession = sample.id
left join
  run
on
  run.experiment_accession = experiment.id
where
  scientific_name LIKE %s
"""


def convert_tude(number, direction):
    """
    Convert EW/NS latitude/longitude values to positive and negative integers
    """

    number = float(number)

    if direction in {"N", "E"}:
        multiplier = 1
    elif direction in {"S", "W"}:
        multiplier = -1

    new_number = number * multiplier

    return new_number


def fetch_rows():
    cursor = db.execute_sql(query, params=["soil metagenome"])

    # get nice dictionaries
    columns = [i.name for i in cursor.description]
    items = (dict(zip(columns, row)) for row in cursor)

    return items


def main():
    written = 0

    out_rows = []
    print("querying database")

    items = fetch_rows()
    print("munging coordinates")
    for item in items:
        if item["lat_lon"] is not None:
            munged_lat_lon = munge_lat_lon(item["lat_lon"][0])

            if type(munged_lat_lon) == dict:

                item["x"] = convert_tude(
                    float(munged_lat_lon["x"]), munged_lat_lon["ns"]
                )
                item["y"] = convert_tude(
                    float(munged_lat_lon["y"]), munged_lat_lon["ew"]
                )
                written += 1

                if written % 1000 == 0:
                    print(f"---> written {written} records")
                out_rows.append(item)

    print("writing results")
    with open("samples.csv", "w") as output:
        list_of_dictionaries_to_csv(out_rows, output)


if __name__ == "__main__":
    main()
