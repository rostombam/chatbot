# core/bi_analyzer/analyzer.py
import pandas as pd
import plotly.express as px

def create_analysis_chart(df: pd.DataFrame):
    """Génère un graphique simple à partir d'un DataFrame."""
    # S'il y a des colonnes numériques, crée un histogramme de la première
    numeric_cols = df.select_dtypes(include=['number']).columns
    if not numeric_cols.empty:
        col_to_plot = numeric_cols[0]
        # Tentative de trouver une colonne catégorielle pour la couleur
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        color_col = categorical_cols[0] if not categorical_cols.empty else None

        fig = px.histogram(df, x=col_to_plot, color=color_col, title=f"Distribution de {col_to_plot}")
        # Ensure plotly.js is embedded, not linked via CDN
        return fig.to_html(full_html=False, include_plotlyjs=True)

    return "Aucune colonne numérique trouvée dans les données pour créer un graphique."
