# PV-GRIP (PV-Geographic Raster Image Processor)

[![Find a bird!](http://img.youtube.com/vi/GGpmm5at-a8/0.jpg)](http://www.youtube.com/watch?v=GGpmm5at-a8)

This is a fork of
[https://open-elevation.com](https://open-elevation.com) updated and
extended by few things I need in my project.

Below are described new commands introduced to the server. For general
references refer to the original project documentation.

## Running the server

Say
```
scripts/build_docker.sh
```
to build a docker image.

Say
```
scripts/run_docker.sh
```
to run the image exposing port 8080.

## Data

Unlike the original project multiple sources of data can be used. If
the data for a query is duplicated, a dataset with higher resolution
is selected.

Data can be placed in several subdirectories. It can be either a
directory with geotiff raster files (in arbitrary coordinate system)
or a directory containing `remote_meta.json` (see below).

All data should be placed in `data/current` directory.

Say
```
scripts/preprocess.sh
```
to preprocess data. That command converts splits files on smaller
chunks (maximum is 3000x3000 pixels).

Some parts of the scripts depends on the version of GDAL being used
(and also requires GDAL installed on the host machine). Hence, it is
possible to run the scripts from inside the docker image
```
scripts/run_docker.sh scripts/preprocess.sh
```

Preprocess script create a backup of the data using the
```
cp -rl data/current data/current.bak
```

On a active server, say
```
> curl localhost:8080/api/help
```
to see available commands.

To query help on any particular command call
```
> curl localhost:8080/api/raster/help
```

The server timeout is 30 seconds. In this time it either response with
a binary file or a json dictionary.

In case task is running the following message is returned:
```
{"message": "task is running"}
```

### NRW Lidar and Aerial data

The server gives access to [geospatial
datasets](https://www.opengeodata.nrw.de/produkte/geobasis/) provided
by NRW.

For the a special file `remote_meta.json` should be specified in the
corresponding directory. See examples in `templates` directory.

For example, for the Lidar data:
```
{
    "root_url": "https://www.opengeodata.nrw.de/produkte/geobasis/hm/3dm_l_las/3dm_l_las/3dm_32_%s_%s_1_nw.laz",
    "step": 1000,
    "box_resolution": 1,
    "epsg": 25832,
    "box_step": 1,
    "pdal_resolution": 0.3,
    "meta_url": "https://www.opengeodata.nrw.de/produkte/geobasis/hm/3dm_l_las/3dm_l_las/index.json",
    "meta_entry_regex": "^3dm_32_(.*)_(.*)_1_nw.*$",
    "las_stats": ["max","min","count","mean","idw","stdev"],
    "if_compute_las": "yes"
}
```
where `pdal_resolition` indicated that Lidar data is computed with a
resolution of 30cm, resolution is given in terms of EPSG:25832, and
hence in meters.

From a cloud point several statistic can be computed: `min`, `max` and
`count`. Those functions are taken for every region with a specified
resolution. See more info on available statistics
[here](https://pdal.io/stages/writers.gdal.html#writers-gdal).

If `if_compute_las` is not `"yes"`, then `las_stats` and
`pdal_resolution` arguments are ignored.

## Sample raster images

It is possible to query a coordinate from a bounding box. For example,
```
> curl localhost:8080/api/raster\?box="\[50.7731,6.0793,50.7780,6.0882\]" -o output_fn
```
the box argument is given either as a list (in POST query) or as a json string list (in GET query).

See
```
> curl localhost:8080/api/raster/help
```
to see default options.

## Shadows

To obtain shadows say
```
> curl localhost:8080/api/shadow\?box="\[50.6046,6.38,50.6098,6.3977\]"\&timestr="2020-05-01_5:3:00"
```
time must be UTC.

As usual
```
> curl localhost:8080/api/shadow/help
```
gives some help.

To compile a shadow video use `scripts/shadow_movie/query_data.sh`
script. It also allow to stress test the server.

## Caveats

 - Be aware that all floating arguments are cached with 6 digit
   accuracy. Hence querying box `[50,6,51,7]` and
   `[50.0000001,6,51,7]` will yield the same results

 - Some jobs require a tree of operations to be completed. Two queries
   producing: "message: task is running" does not imply that the
   second query will complete its job. It means that the second query
   hit a task dependency that is already being run for the first
   query. This might require running query more than 2 times.

 - Between getting results try to run queries, such that all data
   (also intermediate data, like generated geotiff, etc) required for
   those queries is less than 150GB.

   This value can be extended in the settings of the RESULTS_CACHE.

 - The value of a pixel of a raster image is selected as a maximum of
   all available data for this point. In case data is still missing in
   all datasets, the data is taken as a nearest neighbour from the
   generated raster image.

   Hence for more accurate shadows it is important to specify correct
   `data_re` argument.

 - For any non-laz remote data one has to specify stat="". For
   example, this applies for the aerial images:
   ```
   curl localhost:8081/api/raster\?box="\[50.6053,6.3835,50.6085,6.3922\]"\&step="1"\&data_re=".*_Aerial"\&output_type="png"\&stat="" -o test.png
   ```
