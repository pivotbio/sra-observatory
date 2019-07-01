# :earth_americas: :earth_asia: :earth_africa: Short Read Observatory

Create a relational database from NCBI/SRA so that I can query SRA sample data
and extract SRA Run IDs

## Why not SRADB

I can't find documentation on how this database was built and I don't trust it.
There is very little documentation on how to query their API. I'd rather just
write database queries. Also, they didn't include the latitude and longitude
(or any of the other attributes in the Samples table).

## Why not NCBI's API?

Because I need to look up hundreds of thousands of samples.

## Why not NCBI's web search?

There is no straightforward way to export the list of sequencing run IDs for a
given set of samples and I need the run IDs to download the raw reads.

## ~Why Mongo?~

~NCBI's data is partially schema-less and I just wanted a quick way to query a
large quantity of mostly static documents.~

I switched back to PostgreSQL and JSONB for the schema-less metadata part.

# Instructions

Install requirements:

```
pip3 install -r requirements.txt
```

Fetch data from NCBI. This will fetch a ~ 2 Gb `.tar.gz` file containing XML
documents for SRA submissions. You do not need to extract this file!

Make sure you edit `fetch-data.sh` and `load.py` with the latest filename from
https://ftp-trace.ncbi.nih.gov/sra/reports/Metadata/

```
./fetch-data.sh
```

Set environment variables (same as genome observatory) for postgres database:

```sh
SOBS_DB_NAME=...
SOBS_DB_USER=...
SOBS_DB_PASSWORD=...
SOBS_DB_PORT=...
SOBS_DB_HOST=...
```

Load data into PostgreSQL

```
./load.py
```

This will build 3 tables in `sra-db`:

- `samples`
- `runs`
- `experiments`

The schema is roughly the same as the NCBI SRA ([see their
documentation](https://www.ncbi.nlm.nih.gov/sra/docs/submitmeta/)) although I
didn't extract everything from their XML dumps. To get from experiment to run,
you have to join on sample. In SQL, this would look like:

```sql
select
  scientific_name,
  count(*)
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
  scientific_name = "soil metagenome"
group by
  sample.scientific_name
order by
  count desc
```


Output a list of SRR IDs (needed to download the fastq files) with some relevant metadata:

```sql
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
  attributes->'geo_loc_name' as geo_loc_name,
  attributes->'study name' as study_name
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
```
