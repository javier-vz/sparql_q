# -*- coding: utf-8 -*-
"""
Explorador SPARQL Qoyllur Rit'i - VERSIÓN PARA STREAMLIT CLOUD
"""

import streamlit as st
import pandas as pd
from rdflib import Graph
import os

# ===== CONFIGURACIÓN =====
st.set_page_config(
    page_title="Qoyllur Rit'i",
    page_icon="⛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("⛰️ Explorador SPARQL Qoyllur Rit'i")

# ===== CARGAR DATOS =====
@st.cache_resource
def cargar_ontologia():
    """Carga el archivo TTL"""
    try:
        g = Graph()
        # Streamlit Cloud necesita path relativo
        g.parse("qoyllurity.ttl", format='turtle')
        return g
    except Exception as e:
        st.error(f"Error al cargar la ontología: {str(e)}")
        st.info("Asegúrate de que 'qoyllurity.ttl' esté en la misma carpeta")
        return None

graph = cargar_ontologia()

if graph is None:
    st.stop()

st.sidebar.success(f"Ontología cargada: {len(graph)} triples")

# ===== CONSULTAS SPARQL =====
CONSULTA_1 = """PREFIX fest: <http://example.org/festividades#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?evento ?nombre ?fecha WHERE {
  ?evento a fest:EventoRitual ;
          rdfs:label ?nombre .
  OPTIONAL { ?evento fest:tieneFecha ?fecha . }
} ORDER BY ?fecha"""

CONSULTA_2 = """PREFIX fest: <http://example.org/festividades#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?lugar ?nombre WHERE {
  ?lugar a fest:Lugar ;
         rdfs:label ?nombre .
} ORDER BY ?nombre"""

CONSULTA_3 = """PREFIX fest: <http://example.org/festividades#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?participante ?nombre WHERE {
  {
    ?participante a fest:Ukumari
  } UNION {
    ?participante a fest:Nacion
  } UNION {
    ?participante a fest:Danzante
  } UNION {
    ?participante a fest:Individuo
  } UNION {
    ?participante a fest:Colectivo
  }
  ?participante rdfs:label ?nombre .
} ORDER BY ?nombre"""

CONSULTA_4 = """PREFIX fest: <http://example.org/festividades#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?danza ?nombre WHERE {
  ?danza a fest:Danza ;
         rdfs:label ?nombre .
} ORDER BY ?nombre"""

CONSULTA_5 = """PREFIX fest: <http://example.org/festividades#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?ukumari ?nombre ?cantidad WHERE {
  ?ukumari a fest:Ukumari ;
           rdfs:label ?nombre .
  OPTIONAL { ?ukumari fest:cantidadAproximada ?cantidad . }
} ORDER BY ?nombre"""

CONSULTA_6 = """PREFIX fest: <http://example.org/festividades#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?item ?nombre ?tipo WHERE {
  ?item rdfs:label ?nombre .
  ?item a ?tipo .
  FILTER(CONTAINS(STR(?tipo), "festividades"))
} LIMIT 50"""

# ===== INTERFAZ =====
st.sidebar.header("Consultas Predefinidas")

# Estado
if 'query_number' not in st.session_state:
    st.session_state.query_number = 1

# Botones en sidebar
if st.sidebar.button("Eventos Rituales", use_container_width=True):
    st.session_state.query_number = 1
    st.rerun()

if st.sidebar.button("Lugares", use_container_width=True):
    st.session_state.query_number = 2
    st.rerun()

if st.sidebar.button("Participantes", use_container_width=True):
    st.session_state.query_number = 3
    st.rerun()

if st.sidebar.button("Danzas", use_container_width=True):
    st.session_state.query_number = 4
    st.rerun()

if st.sidebar.button("Ukumaris", use_container_width=True):
    st.session_state.query_number = 5
    st.rerun()

if st.sidebar.button("Ver Todo", use_container_width=True):
    st.session_state.query_number = 6
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.info("**Cómo usar:**\n1. Selecciona una consulta\n2. Presiona 'Ejecutar'\n3. Descarga los resultados")

# ===== MOSTRAR CONSULTA ACTUAL =====
if st.session_state.query_number == 1:
    query_to_show = CONSULTA_1
    query_name = "Eventos Rituales"
elif st.session_state.query_number == 2:
    query_to_show = CONSULTA_2
    query_name = "Lugares"
elif st.session_state.query_number == 3:
    query_to_show = CONSULTA_3
    query_name = "Participantes"
elif st.session_state.query_number == 4:
    query_to_show = CONSULTA_4
    query_name = "Danzas"
elif st.session_state.query_number == 5:
    query_to_show = CONSULTA_5
    query_name = "Ukumaris"
elif st.session_state.query_number == 6:
    query_to_show = CONSULTA_6
    query_name = "Todos los elementos"

st.header(f"{query_name}")
st.code(query_to_show, language="sparql")

# ===== EJECUTAR CONSULTA =====
if st.button("▶️ Ejecutar Consulta", type="primary", use_container_width=True):
    with st.spinner("Ejecutando consulta SPARQL..."):
        try:
            resultados = graph.query(query_to_show)
            
            # Procesar resultados
            datos = []
            columnas = []
            
            for fila in resultados:
                if not columnas:
                    columnas = [str(v) for v in resultados.vars]
                
                fila_dict = {}
                for var in resultados.vars:
                    valor = fila[var]
                    if valor is not None:
                        valor_str = str(valor)
                        # Simplificar URIs
                        if 'festividades#' in valor_str:
                            fila_dict[str(var)] = valor_str.split('#')[-1]
                        elif 'http://' in valor_str:
                            fila_dict[str(var)] = valor_str.split('/')[-1]
                        else:
                            fila_dict[str(var)] = valor_str
                    else:
                        fila_dict[str(var)] = ""
                
                datos.append(fila_dict)
            
            if datos:
                df = pd.DataFrame(datos)
                
                # Mostrar resultados
                st.success(f"{len(df)} resultados encontrados")
                
                # Estadísticas
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Filas", len(df))
                with col2:
                    st.metric("Columnas", len(df.columns))
                
                # Tabla
                st.dataframe(df, use_container_width=True)
                
                # Descargar
                csv = df.to_csv(index=False, encoding='utf-8')
                st.download_button(
                    "📥 Descargar CSV",
                    data=csv,
                    file_name=f"qoyllur_riti_{query_name.lower().replace(' ', '_')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No se encontraron resultados")
                
        except Exception as e:
            st.error(f"Error: {str(e)}")

# ===== EDITOR PERSONALIZADO =====
st.markdown("---")
st.subheader("✏️ Editor Personalizado")

custom_query = st.text_area(
    "Escribe tu propia consulta SPARQL:",
    height=150,
    placeholder="""PREFIX fest: <http://example.org/festividades#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?s ?nombre WHERE {
  ?s rdfs:label ?nombre .
  ?s a fest:EventoRitual .
} LIMIT 10"""
)

if st.button("▶️ Ejecutar Consulta Personalizada"):
    if custom_query.strip():
        with st.spinner("Ejecutando..."):
            try:
                resultados = graph.query(custom_query)
                
                datos = []
                for fila in resultados:
                    fila_dict = {}
                    for var in resultados.vars:
                        valor = fila[var]
                        if valor is not None:
                            valor_str = str(valor)
                            if 'festividades#' in valor_str:
                                fila_dict[str(var)] = valor_str.split('#')[-1]
                            elif 'http://' in valor_str:
                                fila_dict[str(var)] = valor_str.split('/')[-1]
                            else:
                                fila_dict[str(var)] = valor_str
                        else:
                            fila_dict[str(var)] = ""
                    datos.append(fila_dict)
                
                if datos:
                    df = pd.DataFrame(datos)
                    st.success(f"{len(df)} resultados")
                    st.dataframe(df, use_container_width=True)
                else:
                    st.warning("No se encontraron resultados")
                    
            except Exception as e:
                st.error(f"Error en la consulta: {str(e)}")
    else:
        st.warning("Escribe una consulta SPARQL")

# ===== INFORMACIÓN =====
with st.expander("📖 Información de la aplicación"):
    st.markdown("""
    ## Explorador SPARQL Qoyllur Rit'i
    
    **Descripción:**
    Aplicación web para explorar la ontología de la festividad
    Qoyllur Rit'i mediante consultas SPARQL.
    
    **Características:**
    - Consultas predefinidas para diferentes categorías
    - Editor personalizado para consultas SPARQL
    - Exportación de resultados en CSV
    - Interfaz responsive y amigable
    
    **Tecnologías:**
    - Streamlit (interfaz web)
    - RDFLib (procesamiento RDF/SPARQL)
    - Pandas (manejo de datos)
    
    **Ontología:**
    - Formato: Turtle (.ttl)
    - Dominio: Festividades andinas
    - Clases principales: EventoRitual, Lugar, Participante, Danza
    
    **Desarrollado por:** Javier Vera Zúñiga
    **Repositorio:** https://github.com/javier-vz/sparql_q
    """)

# ===== PIE DE PÁGINA =====
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.9em;'>"
    "⛰️ Explorador SPARQL Qoyllur Rit'i • Ontología de festividades andinas • "
    "<a href='https://streamlit.io' target='_blank'>Hecho con Streamlit</a>"
    "</div>",
    unsafe_allow_html=True
)