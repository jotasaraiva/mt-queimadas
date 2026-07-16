import streamlit as st
from owslib.wfs import WebFeatureService
import geopandas as gpd
import pandas as pd

CRS = "EPSG:4326"

@st.cache_data()
def fetch_conservation_units() -> gpd.GeoDataFrame:
    icmbio_url = "https://geoservicos.inde.gov.br/geoserver/ICMBio/ows"
    mma_url = "https://geoservicos.inde.gov.br/geoserver/MMA/ows"
    icmbio_wfs = WebFeatureService(icmbio_url, version="2.0.0").getfeature(typename="ICMBio:limiteucsfederais_a", outputFormat="application/json")
    mma_wfs = WebFeatureService(mma_url, version="2.0.0").getfeature(typename="MMA:cnuc_2026_03_atualizado", outputFormat="application/json")
    gdf_icmbio = gpd.read_file(icmbio_wfs)
    gdf_mma = gpd.read_file(mma_wfs)
    gdf_icmbio_f = gdf_icmbio[gdf_icmbio['uf'].str.contains(r"^MT$", regex=True, na=False)]
    gdf_mma_f = gdf_mma[gdf_mma['n18'].str.contains(r"^MATO GROSSO$", regex=True, na=False)]
    gdf_mma_f = gdf_mma_f[["n6", "n18", "n17", "geometry"]].rename(columns={"n6": "name", "n18": "uf", "n17": "esfera"})
    gdf_mma_f["uf"] = gdf_mma_f["uf"].str.replace("MATO GROSSO", "MT")
    gdf_icmbio_f = gdf_icmbio_f[["nomeuc", "uf", "esferaadm", "geometry"]].rename(columns={"nomeuc": "name", "esferaadm": "esfera"})
    gdf_ucs = pd.concat([gdf_mma_f, gdf_icmbio_f], ignore_index=True)
    return gdf_ucs
    
@st.cache_data()
def fetch_fires() -> gpd.GeoDataFrame:
    terrabras_url = "https://terrabrasilis.dpi.inpe.br/queimadas/geoserver/ows"
    terrabras_wfs = WebFeatureService(terrabras_url, version="2.0.0").getfeature(typename="dados_abertos:focos_48h_br_todosats", outputFormat="application/json")
    gdf_terrabras = gpd.read_file(terrabras_wfs)
    gdf_terrabras_f = gdf_terrabras[["municipio", "satelite", "bioma", "geometry"]]
    return gdf_terrabras_f

@st.cache_data(show_spinner=False)
def fetch_data():
    gdf_ucs = fetch_conservation_units()
    gdf_fires = fetch_fires()
    gdf_ucs.to_crs(CRS, inplace=True)
    gdf_fires.to_crs(CRS, inplace=True)
    gdf_ucs["uc_geometry"] = gdf_ucs.geometry
    gdf_fires = gpd.sjoin(gdf_fires, gdf_ucs, how="inner", predicate="within")
    gdf_fires = gdf_fires[["name", "uf", "esfera", "municipio", "satelite", "bioma", "geometry", "uc_geometry"]].reset_index(drop=True)
    return gdf_fires