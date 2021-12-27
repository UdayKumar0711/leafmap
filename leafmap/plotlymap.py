import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from .basemaps import xyz_to_plotly
from .common import *
from .osm import *

plotly_basemaps = xyz_to_plotly()


class Map(go.FigureWidget):
    def __init__(
        self, center=(20, 0), zoom=1, basemap="open-street-map", height=600, **kwargs
    ):
        """Initializes a map. More info at https://plotly.com/python/mapbox-layers/

        Args:
            center (tuple, optional): Center of the map. Defaults to (20, 0).
            zoom (int, optional): Zoom level of the map. Defaults to 1.
            basemap (str, optional): Can be one of string from "open-street-map", "carto-positron", "carto-darkmatter", "stamen-terrain", "stamen-toner" or "stamen-watercolor" . Defaults to 'open-street-map'.
            height (int, optional): Height of the map. Defaults to 600.
        """
        super().__init__(**kwargs)
        self.add_scattermapbox()
        self.update_layout(
            {
                "mapbox": {
                    "style": basemap,
                    "center": {"lat": center[0], "lon": center[1]},
                    "zoom": zoom,
                },
                "margin": {"r": 0, "t": 0, "l": 0, "b": 0},
                "height": height,
            }
        )

    def clear_controls(self):
        """Removes all controls from the map."""
        config = {
            "scrollZoom": True,
            "displayModeBar": False,
            "editable": True,
            "showLink": False,
            "displaylogo": False,
        }
        self.show(config=config)

    def add_controls(self, controls):
        """Adds controls to the map.

        Args:
            controls (list): List of controls to add, e.g., ['drawline', 'drawopenpath', 'drawclosedpath', 'drawcircle', 'drawrect', 'eraseshape'] See https://bit.ly/33Tmqxr
        """
        if isinstance(controls, str):
            controls = [controls]
        elif not isinstance(controls, list):
            raise ValueError(
                "Controls must be a string or a list of strings. See https://bit.ly/33Tmqxr"
            )

        self.update_layout(modebar_add=controls)

    def remove_controls(self, controls):
        """Removes controls to the map.

        Args:
            controls (list): List of controls to remove, e.g., ["zoomin", "zoomout", "toimage", "pan", "resetview"]. See https://bit.ly/3Jk7wkb
        """
        if isinstance(controls, str):
            controls = [controls]
        elif not isinstance(controls, list):
            raise ValueError(
                "Controls must be a string or a list of strings. See https://bit.ly/3Jk7wkb"
            )

        self.update_layout(modebar_remove=controls)

    def set_center(self, lat, lon, zoom=None):
        """Sets the center of the map.

        Args:
            lat (float): Latitude.
            lon (float): Longitude.
            zoom (int, optional): Zoom level of the map. Defaults to None.
        """
        self.update_layout(
            mapbox=dict(
                center=dict(lat=lat, lon=lon),
                zoom=zoom if zoom is not None else self.layout.mapbox.zoom,
            )
        )

    def add_basemap(self, basemap="ROADMAP"):
        """Adds a basemap to the map.

        Args:
            basemap (str, optional): Can be one of string from plotly_basemaps. Defaults to 'ROADMAP'.
        """
        if basemap not in plotly_basemaps:
            raise ValueError(
                f"Basemap {basemap} not found. Choose from {','.join(plotly_basemaps.keys())}"
            )

        layers = list(self.layout.mapbox.layers) + [plotly_basemaps[basemap]]
        self.update_layout(mapbox_layers=layers)

    def add_mapbox_layer(self, style, access_token=None):
        """Adds a mapbox layer to the map.

        Args:
            layer (str | dict): Layer to add. Can be "basic", "streets", "outdoors", "light", "dark", "satellite", or "satellite-streets". See https://plotly.com/python/mapbox-layers/ and https://docs.mapbox.com/mapbox-gl-js/style-spec/
        """

        if access_token is None:
            access_token = os.environ.get("MAPBOX_TOKEN")

        self.update_layout(
            mapbox_style=style, mapbox_layers=[], mapbox_accesstoken=access_token
        )

    def add_layer(self, layer, name=None, **kwargs):
        """Adds a layer to the map.

        Args:
            layer (plotly.graph_objects): Layer to add.
            name (str, optional): Name of the layer. Defaults to None.
        """
        if isinstance(name, str):
            layer.name = name
        self.add_trace(layer, **kwargs)

    def remove_layer(self, name):
        """Removes a layer from the map.

        Args:
            name (str): Name of the layer to remove.
        """
        self.data = [layer for layer in self.data if layer.name != name]

    def clear_layers(self, clear_basemap=False):
        """Clears all layers from the map.

        Args:
            clear_basemap (bool, optional): If True, clears the basemap. Defaults to False.
        """
        if clear_basemap:
            self.data = []
        else:
            if len(self.data) > 1:
                self.data = self.data[:1]

    def add_tile_layer(
        self,
        url,
        name="TileLayer",
        attribution="",
        opacity=1.0,
        **kwargs,
    ):
        """Adds a TileLayer to the map.

        Args:
            url (str): The URL of the tile layer.
            attribution (str): The attribution to use. Defaults to "".
            opacity (float, optional): The opacity of the layer. Defaults to 1.
            shown (bool, optional): A flag indicating whether the layer should be on by default. Defaults to True.
        """

        layer = {
            "below": "traces",
            "sourcetype": "raster",
            "sourceattribution": attribution,
            "source": [url],
            "opacity": opacity,
            "name": name,
        }
        layers = list(self.layout.mapbox.layers) + [layer]
        self.update_layout(mapbox_layers=layers)

    def add_cog_layer(
        self,
        url,
        name="Untitled",
        attribution="",
        opacity=1.0,
        titiler_endpoint="https://titiler.xyz",
        **kwargs,
    ):
        """Adds a COG TileLayer to the map.

        Args:
            url (str): The URL of the COG tile layer, e.g., 'https://opendata.digitalglobe.com/events/california-fire-2020/pre-event/2018-02-16/pine-gulch-fire20/1030010076004E00.tif'
            name (str, optional): The layer name to use for the layer. Defaults to 'Untitled'.
            attribution (str, optional): The attribution to use. Defaults to ''.
            opacity (float, optional): The opacity of the layer. Defaults to 1.
            titiler_endpoint (str, optional): Titiler endpoint. Defaults to "https://titiler.xyz".
            **kwargs: Arbitrary keyword arguments, including bidx, expression, nodata, unscale, resampling, rescale, color_formula, colormap, colormap_name, return_mask. See https://developmentseed.org/titiler/endpoints/cog/ and https://cogeotiff.github.io/rio-tiler/colormap/. To select a certain bands, use bidx=[1, 2, 3]
        """
        tile_url = cog_tile(url, titiler_endpoint, **kwargs)
        center = cog_center(url, titiler_endpoint)  # (lon, lat)
        self.add_tile_layer(tile_url, name, attribution, opacity)
        self.set_center(lon=center[0], lat=center[1], zoom=10)

    def add_stac_layer(
        self,
        url=None,
        collection=None,
        items=None,
        assets=None,
        bands=None,
        titiler_endpoint=None,
        name="STAC Layer",
        attribution="",
        opacity=1.0,
        **kwargs,
    ):
        """Adds a STAC TileLayer to the map.

        Args:
            url (str): HTTP URL to a STAC item, e.g., https://canada-spot-ortho.s3.amazonaws.com/canada_spot_orthoimages/canada_spot5_orthoimages/S5_2007/S5_11055_6057_20070622/S5_11055_6057_20070622.json
            collection (str): The Microsoft Planetary Computer STAC collection ID, e.g., landsat-8-c2-l2.
            items (str): The Microsoft Planetary Computer STAC item ID, e.g., LC08_L2SP_047027_20201204_02_T1.
            assets (str | list): The Microsoft Planetary Computer STAC asset ID, e.g., ["SR_B7", "SR_B5", "SR_B4"].
            bands (list): A list of band names, e.g., ["SR_B7", "SR_B5", "SR_B4"]
            titiler_endpoint (str, optional): Titiler endpoint, e.g., "https://titiler.xyz", "planetary-computer", "pc". Defaults to None.
            name (str, optional): The layer name to use for the layer. Defaults to 'STAC Layer'.
            attribution (str, optional): The attribution to use. Defaults to ''.
            opacity (float, optional): The opacity of the layer. Defaults to 1.
        """
        tile_url = stac_tile(
            url, collection, items, assets, bands, titiler_endpoint, **kwargs
        )
        center = stac_center(url, collection, items, titiler_endpoint)
        self.add_tile_layer(tile_url, name, attribution, opacity)
        self.set_center(lon=center[0], lat=center[1], zoom=10)

    def save(self, file, format=None, width=None, height=None, scale=None, **kwargs):
        """Convert a map to a static image and write it to a file or writeable object

        Args:
            file (str): A string representing a local file path or a writeable object (e.g. a pathlib.Path object or an open file descriptor)
            format (str, optional): The desired image format. One of png, jpg, jpeg, webp, svg, pdf, eps. Defaults to None.
            width (int, optional): The width of the exported image in layout pixels. If the `scale` property is 1.0, this will also be the width of the exported image in physical pixels.. Defaults to None.
            height (int, optional): The height of the exported image in layout pixels. If the `scale` property is 1.0, this will also be the height of the exported image in physical pixels.. Defaults to None.
            scale (int, optional): The scale factor to use when exporting the figure. A scale factor larger than 1.0 will increase the image resolution with respect to the figure's layout pixel dimensions. Whereas as scale factor of less than 1.0 will decrease the image resolution.. Defaults to None.
        """
        self.write_image(
            file, format=format, width=width, height=height, scale=scale, **kwargs
        )

    def add_choropleth_map(
        self, data, name=None, z=None, colorscale="Viridis", **kwargs
    ):
        """Adds a choropleth map to the map.

        Args:
            data (str): File path to vector data, e.g., https://raw.githubusercontent.com/giswqs/leafmap/master/examples/data/countries.geojson
            name (str, optional): Name of the layer. Defaults to None.
            z (str, optional): Z value of the data. Defaults to None.
            colorscale (str, optional): Color scale of the data. Defaults to "Viridis".
        """
        check_package("geopandas")
        import json
        import geopandas as gpd

        gdf = gpd.read_file(data).to_crs(epsg=4326)
        geojson = json.loads(gdf.to_json())

        self.add_choroplethmapbox(
            geojson=geojson,
            locations=gdf.index,
            z=gdf[z],
            name=name,
            colorscale=colorscale,
            **kwargs,
        )

    def add_scatter_plot_demo(self, **kwargs):
        """Adds a scatter plot to the map."""
        lons = np.random.random(1000) * 360.0
        lats = np.random.random(1000) * 180.0 - 90.0
        z = np.random.random(1000) * 50.0
        self.add_scattermapbox(lon=lons, lat=lats, marker={"color": z})

    def add_heatmap(
        self,
        data,
        latitude="latitude",
        longitude="longitude",
        z="value",
        radius=10,
        colorscale=None,
        name="Heat map",
        **kwargs,
    ):
        """Adds a heat map to the map. Reference: https://plotly.com/python/mapbox-density-heatmaps

        Args:
            data (str | pd.DataFrame): File path or HTTP URL to the input file or a . For example, https://raw.githubusercontent.com/plotly/datasets/master/earthquakes-23k.csv
            latitude (str, optional): The column name of latitude. Defaults to "latitude".
            longitude (str, optional): The column name of longitude. Defaults to "longitude".
            z (str, optional): The column name of z values. Defaults to "value".
            radius (int, optional): Radius of each “point” of the heatmap. Defaults to 25.
            colorscale (str, optional): Color scale of the data, e.g., Viridis. See https://plotly.com/python/builtin-colorscales. Defaults to None.
            name (str, optional): Layer name to use. Defaults to "Heat map".

        """

        if isinstance(data, str):
            df = pd.read_csv(data)
        elif isinstance(data, pd.DataFrame):
            df = data
        else:
            raise ValueError("data must be a DataFrame or a file path.")

        heatmap = go.Densitymapbox(
            lat=df[latitude],
            lon=df[longitude],
            z=df[z],
            radius=radius,
            colorscale=colorscale,
            name=name,
            **kwargs,
        )
        self.add_trace(heatmap)

    def add_heatmap_demo(self, **kwargs):
        """Adds a heatmap to the map."""
        quakes = pd.read_csv(
            "https://raw.githubusercontent.com/plotly/datasets/master/earthquakes-23k.csv"
        )
        heatmap = go.Densitymapbox(
            lat=quakes.Latitude,
            lon=quakes.Longitude,
            z=quakes.Magnitude,
            radius=10,
            name="Earthquake",
        )

        self.add_basemap("Stamen.Terrain")
        self.add_trace(heatmap)


def fix_widget_error():
    """
    Fix FigureWidget - 'mapbox._derived' Value Error.
    Adopted from: https://github.com/plotly/plotly.py/issues/2570#issuecomment-738735816
    """
    basedatatypesPath = os.path.join(
        os.path.dirname(os.__file__), "site-packages", "plotly", "basedatatypes.py"
    )

    # read basedatatypes.py
    with open(basedatatypesPath, "r") as f:
        lines = f.read()

    find = "if not BaseFigure._is_key_path_compatible(key_path_str, self.layout):"

    replace = """if not BaseFigure._is_key_path_compatible(key_path_str, self.layout):
                    if key_path_str == "mapbox._derived":
                        return"""

    # add new text
    lines = lines.replace(find, replace)

    # overwrite old 'basedatatypes.py'
    with open(basedatatypesPath, "w") as f:
        f.write(lines)