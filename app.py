import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import folium

# Cargar los datos
@st.cache_data
def cargar_dbOperational():
    dataOperational = pd.read_excel('db_operational.xlsx')
    return dataOperational

data_base_operational = cargar_dbOperational()

# Título de la página principal
st.title("Producción de Hidrógeno Verde")

# Mostrar primeros y últimos 5 datos de la tabla
st.write("**Resumen de los datos principales**:")
st.write("Base de datos resultante luego del proceso de extracción y limpieza")
st.dataframe(pd.concat([data_base_operational.head(), data_base_operational.tail()]))

# Calcular los KPIs
produccion_total_mundial = data_base_operational['Capacity_Nm³ H₂/y'].sum()

# Definir los países de interés para LATAM
countries_of_interest = ["Colombia", "Chile", "Argentina", "Peru", "Brazil"]
produccion_total_latam = data_base_operational[data_base_operational['Country'].isin(countries_of_interest)]['Capacity_Nm³ H₂/y'].sum()
produccion_total_colombia = data_base_operational[data_base_operational['Country'] == "Colombia"]['Capacity_Nm³ H₂/y'].sum()

# Definir el factor de emisión de CO2
factor_emision_gas_natural = 10.5  # kg CO2/kg H2
data_base_operational['Producción H₂ (toneladas)'] = data_base_operational['Capacity_Nm³ H₂/y'] / 1000  # Convertir Nm³ a toneladas
data_base_operational['Reducción CO₂ (toneladas)'] = data_base_operational['Producción H₂ (toneladas)'] * factor_emision_gas_natural  # Toneladas de CO₂ evitadas

co2_reducido_latam = data_base_operational[data_base_operational['Country'].isin(countries_of_interest)]['Reducción CO₂ (toneladas)'].sum()

# Mostrar KPIs
kpi1 = st.selectbox("Selecciona la unidad para Producción Total Mundial:", ["Nm³ H₂/y", "MW"], index=0)
kpi2 = st.selectbox("Selecciona la unidad para Producción Total en LATAM:", ["Nm³ H₂/y", "MW"], index=0)

produccion_mundial = produccion_total_mundial if kpi1 == "Nm³ H₂/y" else produccion_total_mundial * 0.000277778  # Convertir a MW
produccion_latam = produccion_total_latam if kpi2 == "Nm³ H₂/y" else produccion_total_latam * 0.000277778  # Convertir a MW
produccion_colombia_mw = produccion_total_colombia * 0.000277778  # Producción total de Colombia en MW

st.metric("Producción Total Mundial", f"{produccion_mundial:,.0f} {kpi1}")
st.metric("Producción Total en LATAM", f"{produccion_latam:,.0f} {kpi2}")
st.metric("Producción Total en Colombia (MW)", f"{produccion_colombia_mw:,.0f} MW")
st.metric("Cantidad de CO2 Reducido en LATAM (toneladas)", f"{co2_reducido_latam:,.0f}")

st.write("**Análisis de la base de datos**:")
# Crear las pestañas
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "Tipos de Tecnologías Usadas",
    "Distribución por Tecnología",
    "Evolución por Año",
    "Contribución de los Líderes",
    "Total Proyectos en LATAM",
    "Total Producción en LATAM",
    "Mapa LATAM",
    "Reducción CO2 America",
    "Proyectos de Colombia"
])

# Pestaña 1: Tipos de tecnologías usadas
with tab1:
    st.write("**Esta gráfica muestra los tipos de tecnologías usadas para la producción de hidrógeno a nivel mundial, excluyendo los datos desconocidos.**")
    filtered_data = data_base_operational[data_base_operational['Technology_electricity_details'] != 'Unknown']
    count_details = filtered_data.groupby('Technology_electricity_details').size().reset_index(name='Count')
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(count_details['Technology_electricity_details'], count_details['Count'], color='skyblue', edgecolor='black')
    ax.set_title('Tipos de Tecnologías Usadas a Nivel Mundial', fontsize=16)
    ax.set_xlabel('Tecnología', fontsize=14)
    ax.set_ylabel('Conteo', fontsize=14)
    ax.set_xticklabels(count_details['Technology_electricity_details'], rotation=45)
    ax.grid(axis='y')
    st.pyplot(fig)
    st.markdown("Esta gráfica muestra la cantidad de proyectos de hidrógeno verde a nivel mundial clasificados por tipo de tecnología.\nExcluye aquellos proyectos con tecnologías desconocidas.\nLa visualización permite observar las tecnologías dominantes en el sector.")
# Pestaña 2: Distribución por Tecnología
with tab2:
    st.write("**La siguiente gráfica presenta la cantidad de proyectos según la tecnología aplicada en cada uno.**")
    tech_counts = data_base_operational['Technology'].value_counts()
    fig, ax = plt.subplots()
    tech_counts.plot(kind='bar', ax=ax, color='orange')
    ax.set_title("Distribución de Proyectos por Tecnología")
    ax.set_xlabel("Tecnología")
    ax.set_ylabel("Conteo de Proyectos")
    st.pyplot(fig)
    st.markdown("En este gráfico de barras se presenta la cantidad de proyectos por cada tipo de tecnología utilizada.\nPermite identificar la tecnología más utilizada a nivel global y comparar la popularidad de las tecnologías.")
# Pestaña 3: Evolución por Año
with tab3:
    st.write("**A continuación, se observa la evolución anual en la capacidad de producción de hidrógeno, lo que permite ver el crecimiento de la industria.**")
    capacidad_por_anio = data_base_operational.groupby('Date online')['Capacity_Nm³ H₂/y'].sum()
    fig, ax = plt.subplots()
    capacidad_por_anio.plot(kind='line', ax=ax, marker='o', color='green')
    ax.set_title("Evolución de la Capacidad de Producción de Hidrógeno por Año")
    ax.set_xlabel("Año")
    ax.set_ylabel("Capacidad Total (Nm³ H₂/y)")
    st.pyplot(fig)
    st.markdown("Esta gráfica de línea muestra cómo ha evolucionado la capacidad total de producción de hidrógeno verde a lo largo de los años.\nEs útil para identificar tendencias de crecimiento en la producción.")
# Pestaña 4: Contribución de los líderes
with tab4:
    st.write("**Esta gráfica destaca los países con mayores aportes en la producción de hidrógeno, representando sus capacidades de producción.**")
    top_paises = data_base_operational.groupby('Country')['Capacity_Nm³ H₂/y'].sum().nlargest(5)
    fig, ax = plt.subplots()
    top_paises.plot(kind='bar', ax=ax, color='coral')
    ax.set_title("Contribución de los Principales Países en la Producción de Hidrógeno")
    ax.set_xlabel("País")
    ax.set_ylabel("Capacidad Total (Nm³ H₂/y)")
    st.pyplot(fig)
    st.markdown("Muestra los países líderes en producción de hidrógeno verde y su capacidad total.\nEste gráfico de barras destaca los países con mayor participación\nen la producción y permite ver su contribución relativa.")

# Pestaña 5: Total de proyectos en LATAM
with tab5:
    st.write("**Visualización del total de proyectos de producción de hidrógeno en los principales países de LATAM.**")
    filtered_df = data_base_operational[data_base_operational['Country'].isin(countries_of_interest)]
    grouped_df = filtered_df.groupby('Country').agg(
        total_capacity=('Capacity_Nm³ H₂/y', 'sum'),
        total_projects=('Country', 'count')
    ).reset_index()
    fig, ax = plt.subplots()
    ax.pie(grouped_df['total_projects'], labels=grouped_df['Country'], autopct='%1.1f%%', startangle=140)
    ax.set_title("Total de Proyectos por País")
    ax.axis('equal')
    st.pyplot(fig)
    st.markdown("Este gráfico de pastel desglosa la cantidad total de proyectos de hidrógeno\nen América Latina por país, proporcionando una vista clara de la distribución de\nproyectos en la región.")
# Pestaña 6: Total producción en LATAM
with tab6:
    st.write("**Capacidad de producción total en LATAM agrupada por país, mostrando el potencial de cada uno.**")
    fig, ax = plt.subplots()
    ax.bar(grouped_df['Country'], grouped_df['total_capacity'], color='skyblue')
    ax.set_title("Capacidad Total por País (Nm³ H₂/y)")
    ax.set_xlabel("País")
    ax.set_ylabel("Capacidad Total (Nm³ H₂/y)")
    plt.xticks(rotation=45)
    st.pyplot(fig)
    st.markdown("Aquí se visualiza la capacidad de producción de hidrógeno\npor país en América Latina. Este gráfico de barras facilita la comparación\nde capacidad entre países de la región.")
# Pestaña 7: Mapa LATAM
with tab7:
    st.write("**Mapa de proyectos de producción de hidrógeno en LATAM. Cada círculo representa un país y su tamaño corresponde a la capacidad de producción.**")
    coordinates = {'Argentina': (-38.4161, -63.6167), 'Brazil': (-14.2350, -51.9253), 'Chile': (-35.6751, -71.5429), 'Colombia': (4.5709, -74.2973), 'Peru': (-9.1899, -75.0152)}
    filtered_df = data_base_operational[data_base_operational['Country'].isin(coordinates.keys())]
    grouped_df = filtered_df.groupby('Country').agg(total_capacity=('Capacity_Nm³ H₂/y', 'sum')).reset_index()
    grouped_df['Latitude'] = grouped_df['Country'].map(lambda x: coordinates[x][0])
    grouped_df['Longitude'] = grouped_df['Country'].map(lambda x: coordinates[x][1])
    map_center = [-8, -55]
    map_south_america = folium.Map(location=map_center, zoom_start=4)
    for idx, row in grouped_df.iterrows():
        folium.CircleMarker(
            location=(row['Latitude'], row['Longitude']),
            radius=row['total_capacity'] * 0.00001,
            color='blue', fill=True, fill_color='blue', fill_opacity=0.6,
            popup=f"{row['Country']}: {row['total_capacity']} Nm³ H₂/y"
        ).add_to(map_south_america)
    st.components.v1.html(map_south_america._repr_html_(), width=725, height=500)
    st.markdown("Este mapa muestra la ubicación y capacidad de producción de hidrógeno\nen países de América Latina. Los círculos indican la\nproducción por país, proporcionando una vista geográfica de la actividad en el sector.")
# Pestaña 8: Reducción de CO₂ por País
with tab8:
    st.write("**Este gráfico presenta la reducción total de CO₂ en cada país de LATAM debido a la producción de hidrógeno verde.**")
    co2_data = data_base_operational[data_base_operational['Country'].isin(countries_of_interest)]
    co2_reduction = co2_data.groupby('Country')['Reducción CO₂ (toneladas)'].sum()
    plt.bar(co2_reduction.index, co2_reduction.values, color='purple')
    plt.xlabel("País", fontsize=14)
    plt.ylabel("CO₂ Reducido (toneladas)", fontsize=14)
    plt.title("Reducción de CO₂ por País en LATAM", fontsize=16)
    st.pyplot(plt)
    st.markdown("La gráfica muestra la cantidad de CO₂ reducido en cada país de América Latina a través de\nla producción de hidrógeno verde. Resalta el impacto positivo en reducción de emisiones de CO₂ en la región.")
# Pestaña 9: Proyectos en Colombia
with tab9:
    st.write("**Detalle de proyectos específicos en Colombia.**")
    colombia_data = data_base_operational[data_base_operational['Country'] == "Colombia"]
    st.table(colombia_data[['Project name', 'Technology', 'Date online', 'Capacity_Nm³ H₂/y']])
    st.markdown("En esta tabla se detallan los proyectos de hidrógeno en Colombia, mostrando su capacidad\nde producción y el año en que iniciaron operaciones. Proporciona una vista específica\nde la actividad en Colombia en la actualidad.")
