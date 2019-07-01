#!/usr/bin/env Rscript

library(tidyverse)
library(leaflet)
library(glue)

dat <- read_csv('samples.csv')

#    urlTemplate = "https://www.ncbi.nlm.nih.gov/biosample/{accession}",

#
# circles version
#
dat %>%
  leaflet() %>%
  addTiles(
  ) %>%
  addCircleMarkers(
    ~longitude,
    ~latitude,
    radius=1
  )


#
# marker version
#
