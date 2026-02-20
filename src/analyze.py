"""Statistical analysis and visualization for Bridge 6."""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


def compute_correlations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute pairwise Spearman correlations between numeric columns.

    Args:
        df: DataFrame with numeric columns (assembly_index, order, molecular_weight, etc.)

    Returns:
        Correlation matrix
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    corr = df[numeric_cols].corr(method='spearman')
    return corr


def test_ma_vs_symmetry(df: pd.DataFrame) -> dict:
    """
    Test correlation between molecular assembly index and point group order.

    Args:
        df: DataFrame with columns: assembly_index, order

    Returns:
        dict with: correlation coefficient, p-value, n_samples
    """
    df_clean = df[['assembly_index', 'order']].dropna()

    if len(df_clean) < 3:
        return {
            "rho": np.nan,
            "p_value": np.nan,
            "n": len(df_clean),
            "status": "insufficient_data"
        }

    rho, p_value = stats.spearmanr(df_clean['assembly_index'], df_clean['order'])

    return {
        "rho": rho,
        "p_value": p_value,
        "n": len(df_clean),
        "status": "computed"
    }


def plot_ma_vs_symmetry(df: pd.DataFrame, output_path: str = None) -> None:
    """
    Create scatter plot: MA vs point group order.

    Args:
        df: DataFrame with columns: assembly_index, order, molecular_weight (optional)
        output_path: if provided, save figure to this path
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Color by molecular weight if available
    if 'molecular_weight' in df.columns:
        scatter = ax.scatter(
            df['order'],
            df['assembly_index'],
            c=df['molecular_weight'],
            cmap='viridis',
            alpha=0.6,
            s=50
        )
        plt.colorbar(scatter, ax=ax, label='Molecular Weight')
    else:
        ax.scatter(df['order'], df['assembly_index'], alpha=0.6, s=50)

    ax.set_xlabel('Point Group Order', fontsize=12)
    ax.set_ylabel('Assembly Index', fontsize=12)
    ax.set_title('Molecular Assembly Index vs Symmetry (Point Group Order)', fontsize=14)
    ax.grid(True, alpha=0.3)

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved plot to {output_path}")

    plt.show()


def plot_distribution(df: pd.DataFrame, column: str, output_path: str = None) -> None:
    """
    Plot histogram + KDE of a column.

    Args:
        df: DataFrame
        column: column name to plot
        output_path: if provided, save figure
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    df[column].hist(bins=30, ax=ax, edgecolor='black', alpha=0.7)
    ax.set_xlabel(column, fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title(f'Distribution of {column}', fontsize=14)
    ax.grid(True, alpha=0.3, axis='y')

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved plot to {output_path}")

    plt.show()


def plot_symmetry_box(df: pd.DataFrame, output_path: str = None) -> None:
    """
    Create box plot: MA distribution across different point groups.

    Args:
        df: DataFrame with columns: assembly_index, point_group
        output_path: if provided, save figure
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    # Filter to point groups with at least 5 samples
    pg_counts = df['point_group'].value_counts()
    common_pg = pg_counts[pg_counts >= 5].index

    df_filtered = df[df['point_group'].isin(common_pg)]

    df_filtered.boxplot(column='assembly_index', by='point_group', ax=ax)
    ax.set_xlabel('Point Group', fontsize=12)
    ax.set_ylabel('Assembly Index', fontsize=12)
    ax.set_title('Assembly Index Distribution by Point Group', fontsize=14)
    plt.suptitle('')  # Remove automatic title
    plt.xticks(rotation=45)

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved plot to {output_path}")

    plt.show()


def pca_analysis(df: pd.DataFrame, output_path: str = None) -> dict:
    """
    Perform PCA on numeric features.

    Args:
        df: DataFrame with numeric columns
        output_path: if provided, save plot

    Returns:
        dict with: explained_variance, pca_object, transformed_data
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    X = df[numeric_cols].dropna()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(X_pca[:, 0], X_pca[:, 1], alpha=0.6, s=50)
    ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)', fontsize=12)
    ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)', fontsize=12)
    ax.set_title('PCA: First Two Principal Components', fontsize=14)
    ax.grid(True, alpha=0.3)

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved plot to {output_path}")

    plt.show()

    return {
        "explained_variance": pca.explained_variance_ratio_,
        "pca": pca,
        "transformed_data": X_pca
    }


def compute_summary_stats(df: pd.DataFrame) -> dict:
    """
    Compute summary statistics.

    Args:
        df: DataFrame

    Returns:
        dict with summary stats
    """
    return {
        "n_molecules": len(df),
        "n_point_groups": df['point_group'].nunique(),
        "point_groups": list(df['point_group'].unique()),
        "ma_mean": df['assembly_index'].mean(),
        "ma_std": df['assembly_index'].std(),
        "ma_min": df['assembly_index'].min(),
        "ma_max": df['assembly_index'].max(),
        "order_mean": df['order'].mean(),
        "order_std": df['order'].std(),
    }
