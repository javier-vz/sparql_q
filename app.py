# -*- coding: utf-8 -*-
"""
Explorador SPARQL Qoyllur Rit'i - VERSIÓN FINAL CORREGIDA
"""

import streamlit as st
import pandas as pd
from rdflib import Graph
import os

# Configuración mínima
st.set_page_config(page_title="Qoyllur Rit'i", layout="wide")
st.title("⛰️ Explorador SPARQL Qoyllur Rit'i")

# Cargar datos
@st.cache_resource
def cargar_datos():
    g = Graph()
    g.parse("qoyllurity.ttl", format='turtle')
    return g

graph = cargar_datos()

# ===== LAS CONSULTAS SPARQL REALES Y CORRECTAS =====
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

# CONSULTA CORREGIDA - incluye todas las subclases de Participante
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

# ===== SIDEBAR CON BOTONES =====
st.sidebar.header("Seleccionar Consulta")

if 'query_number' not in st.session_state:
    st.session_state.query_number = 1

if st.sidebar.button("1. Eventos"):
    st.session_state.query_number = 1
    st.rerun()

if st.sidebar.button("2. Lugares"):
    st.session_state.query_number = 2
    st.rerun()

if st.sidebar.button("3. Participantes"):
    st.session_state.query_number = 3
    st.rerun()

if st.sidebar.button("4. Danzas"):
    st.session_state.query_number = 4
    st.rerun()

if st.sidebar.button("5. Ukumaris"):
    st.session_state.query_number = 5
    st.rerun()

# ===== MOSTRAR CONSULTA =====
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

st.header(query_name)
st.code(query_to_show, language="sparql")

# ===== EJECUTAR CONSULTA =====
if st.button("EJECUTAR CONSULTA"):
    with st.spinner("Ejecutando..."):
        try:
            resultados = graph.query(query_to_show)
            
            datos = []
            for fila in resultados:
                fila_dict = {}
                for var in resultados.vars:
                    valor = fila[var]
                    if valor:
                        valor_str = str(valor)
                        if 'festividades#' in valor_str:
                            fila_dict[str(var)] = valor_str.split('#')[-1]
                        else:
                            fila_dict[str(var)] = valor_str
                    else:
                        fila_dict[str(var)] = ""
                datos.append(fila_dict)
            
            if datos:
                df = pd.DataFrame(datos)
                st.success(f"✅ Resultados: {len(df)}")
                st.dataframe(df, use_container_width=True)
                
                csv = df.to_csv(index=False)
                st.download_button("📥 Descargar CSV", csv, "resultados.csv", "text/csv")
            else:
                st.warning("⚠️ Sin resultados")
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# ===== EDITOR PERSONAL =====
st.markdown("---")
st.subheader("Consulta Personalizada")

personal = st.text_area("Escribe tu consulta SPARQL:", height=150,
                       placeholder="""PREFIX fest: <http://example.org/festividades#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?s ?nombre WHERE {
  ?s rdfs:label ?nombre .
} LIMIT 10""")

if st.button("EJECUTAR PERSONALIZADA"):
    if personal:
        with st.spinner("Ejecutando..."):
            try:
                resultados = graph.query(personal)
                
                datos = []
                for fila in resultados:
                    fila_dict = {}
                    for var in resultados.vars:
                        valor = fila[var]
                        if valor:
                            fila_dict[str(var)] = str(valor)
                        else:
                            fila_dict[str(var)] = ""
                    datos.append(fila_dict)
                
                if datos:
                    df = pd.DataFrame(datos)
                    st.success(f"✅ {len(df)} resultados")
                    st.dataframe(df, use_container_width=True)
                else:
                    st.warning("⚠️ Sin resultados")
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    else:
        st.warning("⚠️ Escribe una consulta primero")

# ===== EXPLICACIÓN =====
with st.expander("📖 ¿Por qué esta consulta SÍ funciona?"):
    st.markdown("""
    **Problema original:**
    ```sparql
    SELECT ?participante ?nombre WHERE {
      ?participante a fest:Participante ;
                    rdfs:label ?nombre .
    }
    ```
    
    **No funciona porque:**
    - `:Ukumaris_Paucartambo_2025` es de tipo `:Ukumari` (NO `:Participante`)
    - `:NacionPaucartambo` es de tipo `:Nacion` (NO `:Participante`)
    - En RDF/OWL sin inferencia, las subclases no se propagan automáticamente
    
    **Solución:**
    ```sparql
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
    }
    ```
    
    **Esta consulta encontrará:**
    1. `Ukumaris_Paucartambo_2025` (como `fest:Ukumari`)
    2. `NacionPaucartambo` (como `fest:Nacion`)
    
    **Ambos son subclases de `fest:Participante` en la ontología.**
    """)