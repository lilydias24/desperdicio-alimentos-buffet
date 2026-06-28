"""Etapa de Analise - Grupo 03.

Este script executa a Parte 1 da entrega final: analise estatistica e
validacao das hipoteses exploratorias sobre desperdicio de alimentos em
servicos de buffet.

Uso esperado:
    python analysis/analise_estatistica.py

Por padrao, o script procura a base em:
    data/gold/food_wastage_gold.csv

Saidas geradas:
    outputs/analise/resumo_analises.csv
    outputs/analise/estatisticas_grupos.csv
    outputs/analise/perfis_risco.csv
    outputs/analise/relatorio_analise.md
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Iterable


RANDOM_SEED = 42
DEFAULT_DATA_PATH = Path("data/gold/food_wastage_gold.csv")
DEFAULT_OUTPUT_DIR = Path("outputs/analise")

REQUIRED_COLUMNS = [
    "type_of_food",
    "event_type",
    "number_of_guests",
    "quantity_of_food",
    "wastage_food_amount",
    "preparation_method",
    "storage_conditions",
    "pricing",
    "wastage_rate",
    "wastage_per_guest",
    "event_size",
    "quantity_tier",
    "event_profile",
]

np = None
pd = None
stats = None


def ensure_dependencies() -> None:
    global np, pd, stats

    try:
        import numpy as numpy_module
        import pandas as pandas_module
        from scipy import stats as scipy_stats_module
    except ModuleNotFoundError as exc:
        missing = exc.name or "dependencia desconhecida"
        raise SystemExit(
            f"Dependencia ausente: {missing}. "
            "Instale numpy, pandas e scipy antes de executar a analise."
        ) from exc

    np = numpy_module
    pd = pandas_module
    stats = scipy_stats_module


@dataclass(frozen=True)
class TestResult:
    pergunta: str
    hipotese: str
    analise: str
    procedimento: str
    estimativa: float | None
    ic_inferior: float | None
    ic_superior: float | None
    p_valor: float | None
    tamanho_efeito: float | None
    interpretacao: str
    limitacao: str

    def as_dict(self) -> dict[str, object]:
        return {
            "pergunta": self.pergunta,
            "hipotese": self.hipotese,
            "analise": self.analise,
            "procedimento": self.procedimento,
            "estimativa": self.estimativa,
            "ic_inferior": self.ic_inferior,
            "ic_superior": self.ic_superior,
            "p_valor": self.p_valor,
            "tamanho_efeito": self.tamanho_efeito,
            "interpretacao": self.interpretacao,
            "limitacao": self.limitacao,
        }


def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"Arquivo de dados nao encontrado: {path}. "
            "Inclua a camada gold neste caminho ou use --data CAMINHO_DO_CSV."
        )

    df = pd.read_csv(path)
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(
            "A base gold nao contem as colunas obrigatorias: "
            + ", ".join(missing)
        )

    numeric_cols = [
        "number_of_guests",
        "quantity_of_food",
        "wastage_food_amount",
        "wastage_rate",
        "wastage_per_guest",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def validate_data(df: pd.DataFrame) -> list[str]:
    notes: list[str] = []

    missing_total = int(df[REQUIRED_COLUMNS].isna().sum().sum())
    duplicated_total = int(df.duplicated().sum())
    notes.append(f"Linhas analisadas: {len(df)}.")
    notes.append(f"Valores ausentes nas colunas obrigatorias: {missing_total}.")
    notes.append(f"Linhas duplicadas: {duplicated_total}.")

    invalid_qty = int((df["quantity_of_food"] <= 0).sum())
    invalid_guests = int((df["number_of_guests"] <= 0).sum())
    invalid_waste = int((df["wastage_food_amount"] < 0).sum())
    waste_gt_qty = int((df["wastage_food_amount"] > df["quantity_of_food"]).sum())

    notes.append(f"Quantidade produzida menor ou igual a zero: {invalid_qty}.")
    notes.append(f"Numero de convidados menor ou igual a zero: {invalid_guests}.")
    notes.append(f"Desperdicio negativo: {invalid_waste}.")
    notes.append(f"Desperdicio maior que a quantidade produzida: {waste_gt_qty}.")

    calculated_rate = 100 * df["wastage_food_amount"] / df["quantity_of_food"]
    max_delta_rate = (df["wastage_rate"] - calculated_rate).abs().max()
    notes.append(
        "Maior diferenca entre wastage_rate informado e recalculado: "
        f"{max_delta_rate:.6f} ponto percentual."
    )

    calculated_per_guest = df["wastage_food_amount"] / df["number_of_guests"]
    max_delta_guest = (df["wastage_per_guest"] - calculated_per_guest).abs().max()
    notes.append(
        "Maior diferenca entre wastage_per_guest informado e recalculado: "
        f"{max_delta_guest:.6f}."
    )

    return notes


def group_stats(df: pd.DataFrame, group_col: str, value_col: str) -> pd.DataFrame:
    stats_df = (
        df.groupby(group_col, observed=True)[value_col]
        .agg(["count", "mean", "median", "std", "min", "max"])
        .reset_index()
    )
    stats_df.insert(0, "variavel_grupo", group_col)
    stats_df.insert(2, "variavel_resposta", value_col)
    return stats_df


def bootstrap_ci_diff(
    values_a: Iterable[float],
    values_b: Iterable[float],
    n_boot: int = 3000,
    confidence: float = 0.95,
) -> tuple[float, float, float]:
    rng = np.random.default_rng(RANDOM_SEED)
    a = pd.Series(values_a).dropna().to_numpy()
    b = pd.Series(values_b).dropna().to_numpy()
    observed = float(a.mean() - b.mean())

    boot = np.array(
        [
            rng.choice(a, size=len(a), replace=True).mean()
            - rng.choice(b, size=len(b), replace=True).mean()
            for _ in range(n_boot)
        ]
    )
    alpha = 1 - confidence
    low, high = np.percentile(boot, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return observed, float(low), float(high)


def cohen_d(values_a: Iterable[float], values_b: Iterable[float]) -> float:
    a = pd.Series(values_a).dropna().to_numpy()
    b = pd.Series(values_b).dropna().to_numpy()
    n_a, n_b = len(a), len(b)
    pooled_var = ((n_a - 1) * a.var(ddof=1) + (n_b - 1) * b.var(ddof=1)) / (
        n_a + n_b - 2
    )
    return float((a.mean() - b.mean()) / np.sqrt(pooled_var))


def epsilon_squared_kruskal(h_stat: float, n: int, k: int) -> float:
    if n <= k:
        return np.nan
    return float((h_stat - k + 1) / (n - k))


def pairwise_welch(
    df: pd.DataFrame,
    group_col: str,
    value_col: str,
    pergunta: str,
    hipotese: str,
    label: str,
) -> list[TestResult]:
    results: list[TestResult] = []
    groups = sorted(df[group_col].dropna().unique())
    pairs = list(combinations(groups, 2))

    for group_a, group_b in pairs:
        values_a = df.loc[df[group_col] == group_a, value_col]
        values_b = df.loc[df[group_col] == group_b, value_col]
        if len(values_a.dropna()) < 2 or len(values_b.dropna()) < 2:
            continue

        test = stats.ttest_ind(values_a, values_b, equal_var=False, nan_policy="omit")
        diff, ci_low, ci_high = bootstrap_ci_diff(values_a, values_b)
        p_adj = min(float(test.pvalue) * len(pairs), 1.0)
        effect = cohen_d(values_a, values_b)

        direction = "maior" if diff > 0 else "menor"
        interpretation = (
            f"{group_a} apresentou media {abs(diff):.3f} {direction} que {group_b} "
            f"em {value_col}; p ajustado por Bonferroni = {p_adj:.4f}."
        )
        limitation = (
            "Comparacao observacional entre grupos; diferencas nao devem ser "
            "interpretadas como causalidade."
        )

        results.append(
            TestResult(
                pergunta=pergunta,
                hipotese=hipotese,
                analise=f"{label}: {group_a} vs {group_b}",
                procedimento="Teste t de Welch + IC bootstrap da diferenca",
                estimativa=diff,
                ic_inferior=ci_low,
                ic_superior=ci_high,
                p_valor=p_adj,
                tamanho_efeito=effect,
                interpretacao=interpretation,
                limitacao=limitation,
            )
        )

    return results


def kruskal_by_group(
    df: pd.DataFrame,
    group_col: str,
    value_col: str,
    pergunta: str,
    hipotese: str,
    label: str,
) -> TestResult | None:
    groups = [
        values.dropna().to_numpy()
        for _, values in df.groupby(group_col, observed=True)[value_col]
        if len(values.dropna()) >= 2
    ]
    if len(groups) < 2:
        return None

    test = stats.kruskal(*groups)
    effect = epsilon_squared_kruskal(float(test.statistic), len(df), len(groups))
    interpretation = (
        f"O teste Kruskal-Wallis avaliou diferencas de {value_col} entre "
        f"categorias de {group_col}; p = {test.pvalue:.4f}."
    )
    limitation = (
        "O teste indica diferenca global entre grupos, mas nao identifica sozinho "
        "quais pares diferem; use as comparacoes pareadas como apoio."
    )

    return TestResult(
        pergunta=pergunta,
        hipotese=hipotese,
        analise=label,
        procedimento="Kruskal-Wallis",
        estimativa=float(test.statistic),
        ic_inferior=None,
        ic_superior=None,
        p_valor=float(test.pvalue),
        tamanho_efeito=effect,
        interpretacao=interpretation,
        limitacao=limitation,
    )


def correlation_result(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    pergunta: str,
    hipotese: str,
    method: str,
) -> TestResult:
    clean = df[[x_col, y_col]].dropna()
    if method == "pearson":
        test = stats.pearsonr(clean[x_col], clean[y_col])
        procedure = "Correlacao de Pearson"
    elif method == "spearman":
        test = stats.spearmanr(clean[x_col], clean[y_col])
        procedure = "Correlacao de Spearman"
    else:
        raise ValueError(f"Metodo de correlacao desconhecido: {method}")

    r_value = float(test.statistic)
    interpretation = (
        f"A associacao entre {x_col} e {y_col} foi r = {r_value:.3f}, "
        f"com p = {test.pvalue:.4f}."
    )
    limitation = (
        "Correlacao descreve associacao entre variaveis numericas, mas nao "
        "demonstra relacao causal."
    )

    return TestResult(
        pergunta=pergunta,
        hipotese=hipotese,
        analise=f"{x_col} x {y_col}",
        procedimento=procedure,
        estimativa=r_value,
        ic_inferior=None,
        ic_superior=None,
        p_valor=float(test.pvalue),
        tamanho_efeito=abs(r_value),
        interpretacao=interpretation,
        limitacao=limitation,
    )


def storage_by_food_results(df: pd.DataFrame) -> list[TestResult]:
    results: list[TestResult] = []
    for food_type, subset in df.groupby("type_of_food", observed=True):
        groups = sorted(subset["storage_conditions"].dropna().unique())
        if len(groups) != 2:
            continue

        a, b = groups
        values_a = subset.loc[subset["storage_conditions"] == a, "wastage_rate"]
        values_b = subset.loc[subset["storage_conditions"] == b, "wastage_rate"]
        if len(values_a.dropna()) < 2 or len(values_b.dropna()) < 2:
            continue

        test = stats.ttest_ind(values_a, values_b, equal_var=False, nan_policy="omit")
        diff, ci_low, ci_high = bootstrap_ci_diff(values_a, values_b)
        effect = cohen_d(values_a, values_b)

        results.append(
            TestResult(
                pergunta="Q1",
                hipotese="HE-02",
                analise=f"Armazenamento em {food_type}: {a} vs {b}",
                procedimento="Teste t de Welch + IC bootstrap da diferenca",
                estimativa=diff,
                ic_inferior=ci_low,
                ic_superior=ci_high,
                p_valor=float(test.pvalue),
                tamanho_efeito=effect,
                interpretacao=(
                    f"Para {food_type}, a diferenca media entre {a} e {b} "
                    f"foi {diff:.3f} ponto percentual de wastage_rate."
                ),
                limitacao=(
                    "A comparacao e feita dentro de cada tipo de alimento e pode "
                    "ter tamanhos de grupo reduzidos."
                ),
            )
        )
    return results


def risk_profiles(df: pd.DataFrame) -> pd.DataFrame:
    profiles = (
        df.groupby("event_profile", observed=True)
        .agg(
            n_eventos=("wastage_rate", "size"),
            taxa_media=("wastage_rate", "mean"),
            taxa_mediana=("wastage_rate", "median"),
            desperdicio_medio=("wastage_food_amount", "mean"),
            convidados_medios=("number_of_guests", "mean"),
        )
        .reset_index()
        .sort_values(["taxa_media", "n_eventos"], ascending=[False, False])
    )
    profiles["rank_risco"] = np.arange(1, len(profiles) + 1)
    return profiles


def run_analysis(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    test_results: list[TestResult] = []
    stats_tables: list[pd.DataFrame] = []

    group_specs = [
        ("preparation_method", "wastage_rate", "Q1", "HE-01", "Metodo de preparo"),
        ("event_size", "wastage_per_guest", "Q2", "HE-06", "Porte do evento"),
        ("pricing", "wastage_rate", "Q3", "HE-03", "Faixa de preco"),
        ("quantity_tier", "wastage_rate", "Q3", "HE-04", "Quantidade produzida"),
    ]

    for group_col, value_col, pergunta, hipotese, label in group_specs:
        stats_tables.append(group_stats(df, group_col, value_col))
        global_test = kruskal_by_group(
            df, group_col, value_col, pergunta, hipotese, label
        )
        if global_test is not None:
            test_results.append(global_test)
        test_results.extend(
            pairwise_welch(df, group_col, value_col, pergunta, hipotese, label)
        )

    stats_tables.append(group_stats(df, "storage_conditions", "wastage_rate"))
    test_results.extend(storage_by_food_results(df))

    test_results.append(
        correlation_result(
            df,
            "quantity_of_food",
            "wastage_rate",
            "Q3",
            "HE-04",
            method="pearson",
        )
    )
    test_results.append(
        correlation_result(
            df,
            "quantity_of_food",
            "wastage_rate",
            "Q3",
            "HE-04",
            method="spearman",
        )
    )

    profiles = risk_profiles(df)
    top_profile = profiles.iloc[0]
    test_results.append(
        TestResult(
            pergunta="Q4",
            hipotese="HE-05",
            analise="Ranking de perfis operacionais de risco",
            procedimento="Agrupamento por event_profile",
            estimativa=float(top_profile["taxa_media"]),
            ic_inferior=None,
            ic_superior=None,
            p_valor=None,
            tamanho_efeito=None,
            interpretacao=(
                "O perfil com maior taxa media de desperdicio foi "
                f"{top_profile['event_profile']}, com media "
                f"{top_profile['taxa_media']:.3f}%."
            ),
            limitacao=(
                "Perfis com poucos eventos podem ter medias instaveis; interpretar "
                "o ranking junto com n_eventos."
            ),
        )
    )

    results_df = pd.DataFrame([result.as_dict() for result in test_results])
    stats_df = pd.concat(stats_tables, ignore_index=True)
    return results_df, stats_df, profiles


def format_float(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    return f"{float(value):.4f}"


def build_markdown_report(
    results: pd.DataFrame,
    stats_df: pd.DataFrame,
    profiles: pd.DataFrame,
    validation_notes: list[str],
) -> str:
    lines: list[str] = [
        "# Analise Estatistica Final - Parte 1",
        "",
        "Projeto: Investigacao do Desperdicio de Alimentos em Servicos de Buffet",
        "",
        "## Validacao inicial da base",
        "",
    ]
    lines.extend([f"- {note}" for note in validation_notes])
    lines.extend(
        [
            "",
            "## Hipoteses avaliadas",
            "",
            "- HE-01: Sit-down Dinner esta associado a maior taxa de desperdicio.",
            "- HE-02: O efeito do armazenamento depende do tipo de alimento.",
            "- HE-03: Eventos com pricing High apresentam maior taxa de desperdicio.",
            "- HE-04: Maior quantidade produzida se associa a maior taxa de desperdicio.",
            "- HE-05: Certos perfis operacionais concentram maior risco de desperdicio.",
            "- HE-06: Porte do evento nao e bom preditor isolado do desperdicio per capita.",
            "",
            "## Resumo dos procedimentos",
            "",
            "| Pergunta | Analise | Procedimento | Estimativa | IC 95% | p-valor | Efeito |",
            "|---|---|---|---:|---:|---:|---:|",
        ]
    )

    for _, row in results.iterrows():
        ci = ""
        if not pd.isna(row["ic_inferior"]) and not pd.isna(row["ic_superior"]):
            ci = f"[{format_float(row['ic_inferior'])}; {format_float(row['ic_superior'])}]"
        lines.append(
            "| {pergunta} | {analise} | {procedimento} | {estimativa} | {ci} | {p} | {efeito} |".format(
                pergunta=row["pergunta"],
                analise=row["analise"],
                procedimento=row["procedimento"],
                estimativa=format_float(row["estimativa"]),
                ci=ci,
                p=format_float(row["p_valor"]),
                efeito=format_float(row["tamanho_efeito"]),
            )
        )

    lines.extend(
        [
            "",
            "## Interpretacoes principais",
            "",
        ]
    )
    for _, row in results.iterrows():
        lines.append(f"- **{row['analise']}**: {row['interpretacao']}")

    lines.extend(
        [
            "",
            "## Limitacoes",
            "",
            "- O dataset e observacional; os resultados indicam associacoes, nao causalidade.",
            "- Algumas categorias podem ter poucos registros, tornando medias e testes menos estaveis.",
            "- O ranking de perfis deve ser lido junto com o numero de eventos de cada perfil.",
            "- Resultados com muitos testes pareados devem considerar o risco de falsos positivos.",
            "",
            "## Top 5 perfis de maior risco",
            "",
            "| Rank | Perfil | n_eventos | Taxa media | Taxa mediana |",
            "|---:|---|---:|---:|---:|",
        ]
    )

    for _, row in profiles.head(5).iterrows():
        lines.append(
            f"| {int(row['rank_risco'])} | {row['event_profile']} | "
            f"{int(row['n_eventos'])} | {row['taxa_media']:.4f} | "
            f"{row['taxa_mediana']:.4f} |"
        )

    lines.extend(
        [
            "",
            "## Arquivos gerados",
            "",
            "- `outputs/analise/resumo_analises.csv`: tabela para README e dashboard.",
            "- `outputs/analise/estatisticas_grupos.csv`: estatisticas descritivas por grupo.",
            "- `outputs/analise/perfis_risco.csv`: ranking de perfis operacionais.",
            "- `outputs/analise/relatorio_analise.md`: este relatorio.",
        ]
    )

    return "\n".join(lines) + "\n"


def save_outputs(
    output_dir: Path,
    results: pd.DataFrame,
    stats_df: pd.DataFrame,
    profiles: pd.DataFrame,
    validation_notes: list[str],
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    results.to_csv(output_dir / "resumo_analises.csv", index=False)
    stats_df.to_csv(output_dir / "estatisticas_grupos.csv", index=False)
    profiles.to_csv(output_dir / "perfis_risco.csv", index=False)

    report = build_markdown_report(results, stats_df, profiles, validation_notes)
    (output_dir / "relatorio_analise.md").write_text(report, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Executa a etapa de analise final.")
    parser.add_argument(
        "--data",
        type=Path,
        default=DEFAULT_DATA_PATH,
        help="Caminho para food_wastage_gold.csv.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Diretorio onde as saidas serao gravadas.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_dependencies()
    df = load_data(args.data)
    validation_notes = validate_data(df)
    results, stats_df, profiles = run_analysis(df)
    save_outputs(args.output_dir, results, stats_df, profiles, validation_notes)

    print("Analise concluida.")
    print(f"Resumo: {args.output_dir / 'resumo_analises.csv'}")
    print(f"Relatorio: {args.output_dir / 'relatorio_analise.md'}")


if __name__ == "__main__":
    main()
