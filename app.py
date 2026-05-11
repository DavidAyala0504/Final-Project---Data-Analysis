# -----------------------------------------------------------------------------
# Superstore Analytics  -  Diagnostico de Rentabilidad
# Principios: STWD - Gestalt (proximidad, similitud, figura-fondo,
# cierre, continuidad) - jerarquia visual - reduccion de ruido
# -----------------------------------------------------------------------------
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# -- configuracion de pagina --------------------------------------------------
st.set_page_config(
    page_title="Superstore - Rentabilidad",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# PALETA - sistema de dos capas:
#   Neutros : fondo, superficies, texto  (escala de grises frios)
#   Senal   : un unico rojo semantico para perdida / riesgo
# =============================================================================
C_BG        = "#F7F8FA"   # fondo de pagina
C_SURFACE   = "#FFFFFF"   # tarjetas / graficos
C_BORDER    = "#E4E7ED"   # bordes sutiles
C_TEXT      = "#1A202C"   # texto primario
C_TEXT2     = "#4A5568"   # texto secundario / etiquetas de eje
C_MUTED     = "#A0AEC0"   # lineas de referencia, grid
C_NEUTRAL   = "#CBD5E0"   # barras sin alerta (gris azulado)
C_LOSS      = "#C53030"   # rojo semantico: perdida / riesgo
C_LOSS_BG   = "#FFF5F5"   # fondo suave de alertas
C_LOSS_PALE = "#FED7D7"   # relleno de zona de riesgo
C_GRID      = "#EDF2F7"   # grid de graficos
FONT        = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"

# -- CSS global ---------------------------------------------------------------
st.markdown(
    f"""
<style>
/* -- reset Streamlit -- */
section.main .block-container {{
    padding: 1.75rem 2.5rem 3rem 2.5rem;
    max-width: 1400px;
}}
[data-testid="stAppViewContainer"] > .main {{
    background: {C_BG};
}}
[data-testid="stSidebar"] {{
    background: {C_SURFACE};
    border-right: 1px solid {C_BORDER};
}}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
    font-size: 0.72rem;
    color: {C_TEXT2};
    text-transform: uppercase;
    letter-spacing: 0.09em;
    font-weight: 700;
    margin-top: 1.1rem;
    margin-bottom: 0.2rem;
}}

/* -- tipografia global -- */
html, body, [class*="css"] {{
    font-family: {FONT};
    color: {C_TEXT};
}}
h1, h2, h3, h4, h5 {{
    font-family: {FONT};
    font-weight: 700;
    letter-spacing: -0.02em;
    color: {C_TEXT};
}}

/* -- tarjetas de metricas -- */
.metric-card {{
    background: {C_SURFACE};
    border: 1px solid {C_BORDER};
    border-radius: 10px;
    padding: 1.1rem 1.4rem 1rem 1.4rem;
    height: 100%;
}}
.metric-label {{
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    color: {C_TEXT2};
    margin-bottom: 0.35rem;
}}
.metric-value {{
    font-size: 1.80rem;
    font-weight: 700;
    color: {C_TEXT};
    line-height: 1.1;
    letter-spacing: -0.03em;
}}
.metric-value.alert {{
    color: {C_LOSS};
    font-size: 1.25rem;
}}
.metric-sub {{
    font-size: 0.70rem;
    color: {C_MUTED};
    margin-top: 0.25rem;
}}

/* -- banner big idea -- */
.big-idea {{
    background: {C_LOSS_BG};
    border-left: 4px solid {C_LOSS};
    border-radius: 0 8px 8px 0;
    padding: 0.85rem 1.25rem;
    margin-bottom: 0.5rem;
}}
.big-idea p {{
    margin: 0;
    font-size: 0.92rem;
    font-weight: 600;
    color: {C_LOSS};
    line-height: 1.55;
}}

/* -- encabezado de seccion dentro de grafico -- */
.section-title {{
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.10em;
    color: {C_MUTED};
    margin: 0 0 0.1rem 0;
}}
.chart-headline {{
    font-size: 0.95rem;
    font-weight: 600;
    color: {C_TEXT};
    margin: 0 0 0.85rem 0;
    line-height: 1.35;
}}

/* -- cajas de insight -- */
.insight-box {{
    background: {C_SURFACE};
    border: 1px solid {C_BORDER};
    border-radius: 8px;
    padding: 0.70rem 1.1rem;
    font-size: 0.82rem;
    color: {C_TEXT2};
    margin-top: 0.4rem;
    line-height: 1.55;
}}
.insight-box strong {{
    color: {C_TEXT};
}}

/* -- tabs -- */
[data-testid="stTabs"] [role="tablist"] {{
    border-bottom: 2px solid {C_BORDER};
    gap: 0;
}}
[data-testid="stTabs"] [role="tab"] {{
    font-size: 0.80rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 0.55rem 1.2rem;
    color: {C_TEXT2};
    border: none;
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
    background: transparent;
}}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {{
    color: {C_TEXT};
    border-bottom: 2px solid {C_TEXT};
}}

/* -- separador -- */
.divider {{
    border: none;
    border-top: 1px solid {C_BORDER};
    margin: 1.5rem 0;
}}
</style>
""",
    unsafe_allow_html=True,
)


# =============================================================================
# HELPERS DE GRAFICOS
# =============================================================================
def _layout(height: int = 400, margin: dict | None = None) -> dict:
    """Layout base limpio para todos los graficos."""
    default_margin = {"t": 16, "b": 44, "l": 8, "r": 16}
    return {
        "plot_bgcolor": C_SURFACE,
        "paper_bgcolor": C_SURFACE,
        "font": {"family": FONT, "color": C_TEXT2, "size": 11},
        "height": height,
        "margin": margin if margin is not None else default_margin,
        "hoverlabel": {
            "bgcolor": C_SURFACE,
            "font_size": 12,
            "font_family": FONT,
            "bordercolor": C_BORDER,
        },
        "showlegend": False,
    }


def _ax(title: str | None = None, grid: bool = False, **kw) -> dict:
    """Eje limpio: sin zeroline, sin marco, grid opcional."""
    base: dict = {
        "title": (
            {"text": title, "font": {"size": 11, "color": C_TEXT2}}
            if title
            else None
        ),
        "showgrid": grid,
        "gridcolor": C_GRID,
        "zeroline": False,
        "showline": False,
        "tickcolor": C_BORDER,
        "tickfont": {"size": 10, "color": C_TEXT2},
        "title_standoff": 10,
    }
    base.update(kw)
    return base


def _section(label: str, headline: str) -> None:
    """Etiqueta de seccion + titular del grafico."""
    st.markdown(
        f'<p class="section-title">{label}</p>'
        f'<p class="chart-headline">{headline}</p>',
        unsafe_allow_html=True,
    )


def _insight(text: str) -> None:
    """Caja de insight con estilo consistente."""
    st.markdown(
        f'<div class="insight-box">{text}</div>',
        unsafe_allow_html=True,
    )


# =============================================================================
# CARGA Y ENRIQUECIMIENTO DEL DATASET
# =============================================================================
@st.cache_data
def cargar_datos() -> pd.DataFrame:
    """Carga y enriquece el dataset Superstore."""
    try:
        df = pd.read_csv("superstore.csv", encoding="latin-1")
    except FileNotFoundError:
        df = pd.read_csv("datos/superstore.csv", encoding="latin-1")

    df["Order Date"] = pd.to_datetime(df["Order Date"], format="%m/%d/%Y")
    df["year"]       = df["Order Date"].dt.year
    df["month"]      = df["Order Date"].dt.to_period("M").astype(str)
    df["tramo_desc"] = pd.cut(
        df["Discount"],
        bins=  [-0.01, 0,      0.10,     0.20,     0.30,     0.50,     1.00],
        labels=["0 %", "1-10%", "11-20%", "21-30%", "31-50%", ">50%"],
    )
    return df


superstore = cargar_datos()


# =============================================================================
# SIDEBAR - filtros globales
# =============================================================================
with st.sidebar:
    st.markdown("**Superstore Analytics**")
    st.markdown("Periodo")
    years = st.slider(
        "Anos",
        int(superstore["year"].min()),
        int(superstore["year"].max()),
        (int(superstore["year"].min()), int(superstore["year"].max())),
        label_visibility="collapsed",
    )
    st.markdown("Region")
    regions = st.multiselect(
        "Region",
        options=sorted(superstore["Region"].unique()),
        default=sorted(superstore["Region"].unique()),
        label_visibility="collapsed",
    )
    st.markdown("Categoria")
    categories = st.multiselect(
        "Categoria",
        options=sorted(superstore["Category"].unique()),
        default=sorted(superstore["Category"].unique()),
        label_visibility="collapsed",
    )
    st.markdown("Segmento")
    segments = st.multiselect(
        "Segmento",
        options=sorted(superstore["Segment"].unique()),
        default=sorted(superstore["Segment"].unique()),
        label_visibility="collapsed",
    )


# =============================================================================
# FILTRADO
# =============================================================================
ss = superstore.query(
    "year >= @years[0] and year <= @years[1]"
    " and Region in @regions"
    " and Category in @categories"
    " and Segment in @segments"
)

if ss.empty:
    st.warning("Sin datos para los filtros seleccionados.")
    st.stop()


# =============================================================================
# CABECERA
# =============================================================================
st.markdown("## Superstore Analytics")
st.markdown("#### Diagnostico de Rentabilidad")

st.markdown(
    '<div class="big-idea">'
    "<p>Superstore es un negocio sano que sangra margen en un solo punto: "
    "los descuentos por encima del 20% destruyen mas utilidad "
    "de la que capturan en volumen.</p>"
    "</div>",
    unsafe_allow_html=True,
)
st.markdown("<hr class='divider'>", unsafe_allow_html=True)


# =============================================================================
# KPIs
# =============================================================================
total_sales   = ss["Sales"].sum()
total_profit  = ss["Profit"].sum()
margen_global = total_profit / total_sales if total_sales else 0
peor_subcat   = ss.groupby("Sub-Category")["Profit"].sum().idxmin()
n_ordenes     = ss["Order ID"].nunique()


def _kpi(
    col,
    label: str,
    value: str,
    sub: str = "",
    alert: bool = False,
) -> None:
    """Renderiza una tarjeta KPI en la columna recibida."""
    cls = "metric-value alert" if alert else "metric-value"
    col.markdown(
        f'<div class="metric-card">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="{cls}">{value}</div>'
        f'<div class="metric-sub">{sub}</div>'
        "</div>",
        unsafe_allow_html=True,
    )


c1, c2, c3, c4, c5 = st.columns(5)
_kpi(c1, "Ventas totales",   f"${total_sales / 1e6:,.2f}M", f"{n_ordenes:,} ordenes")
_kpi(c2, "Profit total",     f"${total_profit / 1e3:,.0f}K", "acumulado del periodo")
_kpi(c3, "Margen global",    f"{margen_global * 100:.1f}%",  "sobre ventas netas")
_kpi(c4, "Peor sub-cat.",    peor_subcat, "ver analisis - El Mapa", alert=True)
_kpi(c5, "Anos analizados",  f"{years[0]}-{years[1]}",       "rango seleccionado")

st.markdown("<hr class='divider'>", unsafe_allow_html=True)


# =============================================================================
# PESTANAS
# =============================================================================
tab1, tab2, tab3 = st.tabs(["La Herida", "El Mapa", "La Cura"])


# =============================================================================
# TAB 1 - La Herida
# =============================================================================
with tab1:
    st.markdown("### Donde se pierde el dinero")
    left_col, right_col = st.columns(2, gap="large")

    # -- scatter descuento vs profit ------------------------------------------
    with left_col:
        _section(
            "Transacciones",
            "A partir del 20% de descuento, las perdidas dominan la distribucion",
        )

        muestra = ss.sample(n=min(2500, len(ss)), random_state=42).copy()
        muestra["color_punto"] = muestra["Profit"].apply(
            lambda x: C_LOSS if x < 0 else C_NEUTRAL
        )

        y_max      = float(muestra["Profit"].max())
        y_min      = float(muestra["Profit"].min())
        y_rng      = y_max - y_min
        x_max_disc = float(muestra["Discount"].max())

        fig_sc = go.Figure()

        # fondo zona de riesgo (Gestalt: figura-fondo)
        fig_sc.add_shape(
            type="rect",
            x0=0.20, x1=x_max_disc + 0.02,
            y0=y_min - y_rng * 0.02, y1=y_max + y_rng * 0.02,
            fillcolor=C_LOSS_BG, opacity=0.45, line_width=0,
            layer="below",
        )
        fig_sc.add_trace(go.Scatter(
            x=muestra["Discount"],
            y=muestra["Profit"],
            mode="markers",
            marker={
                "color": muestra["color_punto"],
                "size": 5,
                "opacity": 0.55,
                "line": {"width": 0},
            },
            hovertemplate=(
                "Descuento: %{x:.0%}<br>Profit: $%{y:,.0f}<extra></extra>"
            ),
        ))
        fig_sc.add_hline(y=0, line_color=C_MUTED, line_width=1)
        fig_sc.add_vline(x=0.20, line_dash="dash", line_color=C_LOSS, line_width=1.5)
        fig_sc.add_annotation(
            x=0.20, y=y_max * 0.88,
            text="Umbral critico: 20%",
            showarrow=True, arrowhead=2, arrowwidth=1.2, arrowcolor=C_LOSS,
            ax=62, ay=0, xanchor="left",
            font={"size": 11, "color": C_LOSS, "family": FONT},
            bgcolor="rgba(255,255,255,0.90)", borderpad=4,
        )
        fig_sc.update_layout(
            **_layout(420),
            xaxis=_ax("Descuento aplicado", tickformat=".0%"),
            yaxis=_ax("Profit por transaccion ($)"),
        )
        st.plotly_chart(fig_sc, use_container_width=True)

    # -- barras por tramo de descuento ----------------------------------------
    with right_col:
        _section(
            "Profit acumulado por tramo",
            "Cada dolar vendido con mas del 20% destruye margen, no lo crea",
        )

        agg_disc = (
            ss.groupby("tramo_desc", observed=True)
            .agg(profit=("Profit", "sum"), sales=("Sales", "sum"))
            .reset_index()
        )
        agg_disc["margen_pct"]  = agg_disc["profit"] / agg_disc["sales"] * 100
        agg_disc["color_barra"] = agg_disc["profit"].apply(
            lambda x: C_LOSS if x < 0 else C_NEUTRAL
        )

        y_rng_max = float(agg_disc["profit"].max()) * 1.22
        y_rng_min = float(agg_disc["profit"].min()) * 1.22

        fig_disc = go.Figure()
        fig_disc.add_trace(go.Bar(
            x=agg_disc["tramo_desc"].astype(str),
            y=agg_disc["profit"],
            marker_color=agg_disc["color_barra"],
            marker_line_width=0,
            text=[f"${v / 1_000:,.0f}K" for v in agg_disc["profit"]],
            textposition="outside",
            cliponaxis=False,
            textfont={"size": 10, "color": C_TEXT2},
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Profit: $%{y:,.0f}<br>"
                "Margen: %{customdata:.1f}%<extra></extra>"
            ),
            customdata=agg_disc["margen_pct"],
        ))
        fig_disc.add_hline(y=0, line_color=C_MUTED, line_width=1)
        fig_disc.add_annotation(
            x=4, y=float(agg_disc["profit"].min()) * 0.60,
            text="Zona de perdida operativa",
            showarrow=False,
            font={"size": 10, "color": C_LOSS, "family": FONT},
            bgcolor="rgba(255,255,255,0.80)", borderpad=4,
        )
        fig_disc.update_layout(
            **_layout(420),
            xaxis=_ax("Tramo de descuento"),
            yaxis=_ax("Profit acumulado ($)", range=[y_rng_min, y_rng_max]),
        )
        st.plotly_chart(fig_disc, use_container_width=True)

    _insight(
        "<strong>Lectura:</strong> los tramos 0-20% generan casi todo el profit. "
        "Por encima del 20%, cada tramo cierra en perdida acumulada. "
        "No es un problema de volumen: es una politica de precios mal calibrada."
    )


# =============================================================================
# TAB 2 - El Mapa
# =============================================================================
with tab2:
    st.markdown("### Donde esta la herida geograficamente")

    col_heat, col_rank = st.columns(2, gap="large")

    # -- heatmap categoria x region -------------------------------------------
    with col_heat:
        _section(
            "Profit por categoria y region",
            "Furniture pierde en Central; Technology gana en todas las regiones",
        )

        heat_data = ss.pivot_table(
            index="Category", columns="Region",
            values="Profit", aggfunc="sum", fill_value=0,
        )
        heat_data = heat_data.loc[
            heat_data.sum(axis=1).sort_values(ascending=False).index
        ]

        colorscale = [
            [0.0,  C_LOSS],
            [0.40, C_LOSS_PALE],
            [0.50, "#FFFFFF"],
            [1.0,  C_NEUTRAL],
        ]

        fig_heat = go.Figure(data=go.Heatmap(
            z=heat_data.values,
            x=heat_data.columns,
            y=heat_data.index,
            colorscale=colorscale,
            zmid=0,
            text=[[f"${v / 1_000:,.0f}K" for v in row] for row in heat_data.values],
            texttemplate="%{text}",
            textfont={"size": 12, "color": C_TEXT, "family": FONT},
            hovertemplate="<b>%{y} - %{x}</b><br>Profit: $%{z:,.0f}<extra></extra>",
            showscale=False,
        ))
        fig_heat.update_layout(
            **_layout(340, margin={"t": 8, "b": 36, "l": 90, "r": 12}),
            xaxis={
                "title": None, "side": "bottom", "tickangle": 0,
                "showline": False, "tickfont": {"size": 11, "color": C_TEXT2},
            },
            yaxis={
                "title": None, "automargin": True, "showline": False,
                "tickfont": {"size": 11, "color": C_TEXT2}, "zeroline": False,
            },
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    # -- ranking de sub-categorias por profit ---------------------------------
    with col_rank:
        _section(
            "Ranking sub-categorias",
            "Tres sub-categorias concentran toda la perdida operativa",
        )

        agg_subcat = (
            ss.groupby("Sub-Category", observed=True)
            .agg(profit=("Profit", "sum"))
            .reset_index()
            .sort_values("profit")
        )
        agg_subcat["color_barra"] = agg_subcat["profit"].apply(
            lambda x: C_LOSS if x < 0 else C_NEUTRAL
        )

        x_min = float(agg_subcat["profit"].min()) * 1.28
        x_max = float(agg_subcat["profit"].max()) * 1.28

        fig_rank = go.Figure()
        fig_rank.add_trace(go.Bar(
            y=agg_subcat["Sub-Category"],
            x=agg_subcat["profit"],
            orientation="h",
            marker_color=agg_subcat["color_barra"],
            marker_line_width=0,
            text=[f"${v / 1_000:,.1f}K" for v in agg_subcat["profit"]],
            textposition="outside",
            cliponaxis=False,
            textfont={"size": 9, "color": C_TEXT2},
            hovertemplate="<b>%{y}</b><br>Profit: $%{x:,.0f}<extra></extra>",
        ))
        fig_rank.add_vline(x=0, line_color=C_MUTED, line_width=1)
        fig_rank.update_layout(
            **_layout(400, margin={"t": 8, "b": 40, "l": 8, "r": 72}),
            xaxis=_ax("Profit acumulado ($)", range=[x_min, x_max]),
            yaxis={
                "title": None, "showgrid": False, "automargin": True,
                "tickfont": {"size": 10, "color": C_TEXT2},
                "showline": False, "zeroline": False,
            },
        )
        st.plotly_chart(fig_rank, use_container_width=True)

    _insight(
        "<strong>Lectura:</strong> Tables, Bookcases y Supplies acumulan perdidas "
        "que absorben el profit generado por el resto del portafolio. "
        "Furniture en la region Central es el cruce mas critico."
    )

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # -- bubble chart eficiencia ----------------------------------------------
    _section(
        "Eficiencia de precio",
        "Bookcases y Tables venden volumen importante pero con margen negativo",
    )

    eficiencia = (
        ss.groupby("Sub-Category", observed=True)
        .agg(
            sales=("Sales", "sum"),
            profit=("Profit", "sum"),
            quantity=("Quantity", "sum"),
        )
        .reset_index()
    )
    eficiencia["margen_pct"] = eficiencia["profit"] / eficiencia["sales"] * 100
    eficiencia["color_pt"]   = eficiencia["margen_pct"].apply(
        lambda x: C_LOSS if x < 0 else C_NEUTRAL
    )
    size_norm = eficiencia["quantity"] / eficiencia["quantity"].max() * 52 + 12

    fig_efic = go.Figure()

    # zona de ineficiencia: fondo rojo suave debajo de y=0
    fig_efic.add_shape(
        type="rect",
        x0=0,
        x1=float(eficiencia["sales"].max()) * 1.10,
        y0=float(eficiencia["margen_pct"].min()) * 1.18,
        y1=0,
        fillcolor=C_LOSS_BG, opacity=0.50, line_width=0, layer="below",
    )
    fig_efic.add_trace(go.Scatter(
        x=eficiencia["sales"],
        y=eficiencia["margen_pct"],
        mode="markers+text",
        marker={
            "size": size_norm,
            "color": eficiencia["color_pt"],
            "opacity": 0.75,
            "line": {"width": 1, "color": "white"},
        },
        text=eficiencia["Sub-Category"],
        textposition=[
            "top center" if i % 2 == 0 else "bottom center"
            for i in range(len(eficiencia))
        ],
        textfont={"size": 10, "color": C_TEXT, "family": FONT},
        hovertemplate=(
            "<b>%{text}</b><br>"
            "Ventas: $%{x:,.0f}<br>"
            "Margen: %{y:.1f}%<br>"
            "Unidades: %{customdata:,.0f}<extra></extra>"
        ),
        customdata=eficiencia["quantity"],
    ))
    fig_efic.add_hline(y=0, line_color=C_LOSS, line_width=1.5, line_dash="dash")
    fig_efic.add_hline(
        y=15, line_color=C_MUTED, line_width=1, line_dash="dot",
        annotation_text="Margen saludable: 15%",
        annotation_position="top right",
        annotation_font={"color": C_MUTED, "size": 10, "family": FONT},
        annotation_bgcolor="rgba(255,255,255,0.80)",
    )
    fig_efic.add_annotation(
        x=float(eficiencia["sales"].max()) * 0.12,
        y=float(eficiencia["margen_pct"].min()) * 0.65,
        text="Zona de ineficiencia",
        showarrow=False,
        font={"size": 10, "color": C_LOSS, "family": FONT},
        bgcolor="rgba(255,255,255,0.80)", borderpad=4,
    )
    fig_efic.update_layout(
        **_layout(480, margin={"t": 48, "b": 44, "l": 12, "r": 20}),
        xaxis=_ax("Ventas acumuladas ($)"),
        yaxis=_ax("Margen %", grid=True),
    )
    st.plotly_chart(fig_efic, use_container_width=True)

    _insight(
        "<strong>Lectura:</strong> el tamano de cada burbuja representa unidades vendidas. "
        "Tables y Bookcases son grandes en volumen pero con margen negativo, "
        "lo que indica un problema de precio base, no solo de descuentos."
    )


# =============================================================================
# TAB 3 - La Cura
# =============================================================================
with tab3:
    st.markdown("### Simulacion de politica de descuentos")

    col_ctrl, col_graph = st.columns([1, 4], gap="large")

    # -- control --------------------------------------------------------------
    with col_ctrl:
        st.markdown(
            '<p class="section-title">Parametro</p>',
            unsafe_allow_html=True,
        )
        umbral = st.slider(
            "Cap de descuento",
            min_value=10, max_value=50, value=20, step=5,
            format="%d%%",
            key="umbral_descuento",
        )
        st.caption(
            f"Profit estimado si los descuentos se limitan al {umbral}%."
        )

    # -- slopegraph antes / despues -------------------------------------------
    with col_graph:
        col_cap = f"Cap al {umbral}%"
        _section(
            "Escenario antes / despues",
            f"Capar descuentos al {umbral}% rescata las sub-categorias en perdida",
        )

        SUBCATS_FOCO = [
            "Tables", "Bookcases", "Supplies",
            "Machines", "Furnishings", "Appliances",
        ]

        comp_data = [
            {
                "Sub-Category": sc,
                "Politica actual": sub["Profit"].sum(),
                col_cap: sub.loc[
                    sub["Discount"] <= umbral / 100, "Profit"
                ].sum(),
            }
            for sc in SUBCATS_FOCO
            if len(sub := ss[ss["Sub-Category"] == sc]) > 0
        ]
        comp_df = pd.DataFrame(comp_data)

        fig_slope = go.Figure()

        for _, row in comp_df.iterrows():
            cruza = row["Politica actual"] < 0 and row[col_cap] > 0
            color = C_LOSS if cruza else C_NEUTRAL
            width = 2.5 if cruza else 1.2

            label_izq = (
                f"<b>{row['Sub-Category']}</b>"
                f"  ${row['Politica actual'] / 1_000:,.0f}K"
            )
            label_der = (
                f"${row[col_cap] / 1_000:,.0f}K"
                f"  <b>{row['Sub-Category']}</b>"
            )

            fig_slope.add_trace(go.Scatter(
                x=["Politica actual", col_cap],
                y=[row["Politica actual"], row[col_cap]],
                mode="lines+markers+text",
                line={"color": color, "width": width},
                marker={
                    "size": 8, "color": color,
                    "line": {"color": "white", "width": 1.5},
                },
                text=[label_izq, label_der],
                textposition=["middle left", "middle right"],
                textfont={
                    "size": 10,
                    "color": color if cruza else C_TEXT2,
                    "family": FONT,
                },
                hoverinfo="skip",
            ))

        fig_slope.add_hline(y=0, line_color=C_MUTED, line_width=1, line_dash="dot")
        fig_slope.update_layout(
            **_layout(460, margin={"l": 140, "r": 150, "t": 48, "b": 40}),
            xaxis={
                "showgrid": False, "side": "top",
                "zeroline": False, "showline": False,
                "tickfont": {"size": 12, "color": C_TEXT, "family": FONT},
            },
            yaxis=_ax("Profit ($)", grid=True),
        )
        st.plotly_chart(fig_slope, use_container_width=True)

    _insight(
        f"<strong>Lectura:</strong> las lineas en rojo son sub-categorias "
        f"que pasan de perdida a ganancia al limitar el descuento al {umbral}%. "
        "Las lineas grises ya son rentables con la politica actual."
    )

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # -- serie temporal mensual -----------------------------------------------
    _section(
        "Contexto temporal",
        "El negocio crece sano: el problema es la politica, no el mercado",
    )

    mensual = (
        ss.groupby("month", observed=True)
        .agg(profit=("Profit", "sum"))
        .reset_index()
    )
    mensual["month"] = pd.to_datetime(mensual["month"])
    mensual = mensual.sort_values("month").reset_index(drop=True)
    mensual_neg = mensual[mensual["profit"] < 0]

    fig_time = go.Figure()
    fig_time.add_trace(go.Scatter(
        x=mensual["month"],
        y=mensual["profit"],
        mode="lines",
        line={"color": C_NEUTRAL, "width": 2},
        fill="tozeroy",
        fillcolor="rgba(203, 213, 224, 0.18)",
        hovertemplate="<b>%{x|%b %Y}</b><br>Profit: $%{y:,.0f}<extra></extra>",
    ))

    if not mensual_neg.empty:
        fig_time.add_trace(go.Scatter(
            x=mensual_neg["month"],
            y=mensual_neg["profit"],
            mode="markers",
            marker={
                "color": C_LOSS, "size": 10,
                "line": {"color": "white", "width": 1.5},
            },
            hovertemplate="<b>%{x|%b %Y}</b>: mes en perdida<extra></extra>",
        ))

    fig_time.add_hline(y=0, line_color=C_MUTED, line_width=1)
    fig_time.update_layout(
        **_layout(310),
        xaxis=_ax(None),
        yaxis=_ax("Profit mensual ($)", grid=True),
    )
    st.plotly_chart(fig_time, use_container_width=True)

    n_neg   = len(mensual_neg)
    n_total = len(mensual)
    _insight(
        f"<strong>Lectura:</strong> solo <strong>{n_neg}</strong> de "
        f"<strong>{n_total}</strong> meses cerraron en negativo. "
        "La tendencia general es positiva y creciente: la politica de descuentos "
        "es el unico freno estructural."
    )