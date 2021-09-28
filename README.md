# ogr2osm translation script

This project can be used translate waterways dataset of Finnish Transport Infrastructure Agency (Väylävirasto in Finnish) to osm format. Translation and import plan is documented in openstreetmap wiki.

This project contains `translation.py` ogr2osm translation script which translates original shapefile data to osm format. Following command can be used to start this translation process.

```shell
ogr2osm --encoding iso-8859-15 -t translation.py input.shp -o output.osm
```

See detailed documentation from [openstreetmap wiki page](https://wiki.openstreetmap.org/wiki/Import/Catalogue/Finland_waterways_import). Raw waterway data is available from [Oskari](https://julkinen.vayla.fi/oskari/) online service. You can learn more about ogr2osm from [ogr2osm project](https://github.com/roelderickx/ogr2osm).
