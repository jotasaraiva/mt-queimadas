import streamlit as st
import geopandas as gpd
import leafmap.foliumap as leafmap
from src import fetch_data

class App:
    
    
    def __init__(self):
        self.title = "MT Queimadas"
        self.crs = "EPSG:4326"
        self.legend_url = (
            "https://terrabrasilis.dpi.inpe.br/geoserver/prodes-brasil-nb/ows"
            "?service=WMS"
            "&version=1.3.0"
            "&request=GetLegendGraphic"
            "&format=image/png"
            "&layer=prodes_brasil"
        )
    
    def run(self):
        
        st.set_page_config(
            page_title=self.title,
            page_icon="🔥",
            layout="wide"
        )
        
        st.markdown(
            """
            <style>
            .map-container {
                border-radius: 15px; /* Adjust the roundness here */
                overflow: hidden;      /* Hides map corners sticking out of the border */
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Optional: adds a soft shadow */
                border: 1px solid #ddd;  /* Optional: border color */
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        st.sidebar.title("MT Queimadas")
        st.sidebar.markdown("""
        Painel de dados para demonstração de focos de incêndios, 
        utilizando informações de Unidades de Conservação (UCs) do ICMBio/MMA e dados do Terrabrasilis, 
        plataforma do INPE.
        """)
        st.sidebar.divider()

        with st.spinner("Tratando feições..."):
            fires = fetch_data() 
        
        if fires is not None:

            uf = sorted(fires["uf"].dropna().unique().tolist())
            esferas = sorted(fires["esfera"].dropna().unique().tolist())
            municipios = sorted(fires["municipio"].dropna().unique().tolist())

            selected_uf = st.sidebar.multiselect(
                "Unidade de Conservação",
                options=uf,
                default=[],
            )

            selected_esferas = st.sidebar.multiselect(
                "Esfera",
                options=esferas,
                default=[],
            )

            selected_municipios = st.sidebar.multiselect(
                "Município",
                options=municipios,
                default=[],
            )

            # Apply filters
            fires_filtered = fires.copy()

            selected_uf = selected_uf or None
            selected_esferas = selected_esferas or None
            selected_municipios = selected_municipios or None

            if selected_uf is not None:
                fires_filtered = fires_filtered[
                    fires_filtered["uf"].isin(selected_uf)
                ]

            if selected_esferas is not None:
                fires_filtered = fires_filtered[
                    fires_filtered["esfera"].isin(selected_esferas)
                ]

            if selected_municipios is not None:
                fires_filtered = fires_filtered[
                    fires_filtered["municipio"].isin(selected_municipios)
                ]

            fires_agg = (
                fires.groupby(
                    ["uf", "esfera", "municipio", "bioma"],
                    dropna=False,
                )
                .size()
                .reset_index(name="FOCOS")
                .rename(
                    columns={
                        "uf": "UF",
                        "esfera": "ESFERA",
                        "municipio": "MUNICIPIO",
                        "bioma": "BIOMA",
                    }
                )
            )

            m = leafmap.Map()
            m.add_gdf(
                fires_filtered.drop(columns=["uc_geometry"]),
                layer_name="Focos de Fogo",
                zoom_to_layer=True,
            )
            uc_gdf = gpd.GeoDataFrame(
                fires_filtered[["name", "uc_geometry"]], 
                geometry="uc_geometry", 
                crs=self.crs
            )
            m.add_gdf(uc_gdf, layer_name="UFs")
            m.add_basemap("HYBRID")
            m.add_wms_layer(
                url="https://terrabrasilis.dpi.inpe.br/geoserver/prodes-brasil-nb/ows",
                layers="prodes-brasil-nb:prodes_brasil",
                name="PRODES",
                transparent=True,
                format="image/png",
            )

            with st.sidebar:
            
                sidebar_cols = st.columns(2)

                with sidebar_cols[0]:
                    with st.popover("🗺️ Legenda PRODES", use_container_width=True):
                        st.image(self.legend_url, width=220)

                with sidebar_cols[1]:
                    st.download_button(
                        label="⬇️ Baixar dados (CSV)",
                        data=fires_filtered.to_csv(index=False),
                        file_name="mt_focos_fogo.csv",
                        mime="text/csv",
                    )

            main_cols = st.columns(2)

            with main_cols[0]:
                with st.container(border=True):
                    m.to_streamlit(height=520)
                
            with main_cols[1]:
                metric_cols = st.columns(2)
                with metric_cols[0]:
                    st.metric("Total de Focos", len(fires_filtered), border=True)
                with metric_cols[1]:
                    st.metric("Municípios Afetados", fires_filtered["municipio"].nunique(), border=True)
                st.dataframe(fires_agg, width="stretch", height=425, hide_index=True)


if __name__ == "__main__":
    app = App()
    app.run()