"""Validacao da camada gold - Parte 3.

Este script executa a Parte 3 da entrega final: rastreabilidade e
validacao da camada gold usada pelo dashboard e pela analise estatistica.

Ele confere:
- presenca do arquivo e das colunas obrigatorias;
- valores ausentes, linhas duplicadas e valores invalidos;
- consistencia logica (quantidade, convidados e desperdicio);
- se os indicadores derivados batem com suas formulas
  (wastage_rate, wastage_per_guest, media por perfil e waste_risk_rank).

Uso esperado:
    python analysis/validacao_camada_gold.py

Por padrao, o script procura a base em:
    data/gold/food_wastage_gold.csv

O caminho e resolvido a partir da raiz do repositorio, de forma relativa,
para funcionar tanto na execucao local quanto dentro do container Docker.
Use --data CAMINHO_DO_CSV para apontar para outro arquivo.

Codigo de saida:
    0  -> todas as verificacoes criticas passaram;
    1  -> ao menos uma verificacao critica falhou.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path


# Raiz do repositorio (dois niveis acima deste arquivo: analysis/ -> raiz).
# Mantem o caminho padrao relativo e independente do diretorio de trabalho.
REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA_PATH = REPO_ROOT / "data" / "gold" / "food_wastage_gold.csv"

# Tolerancia usada na comparacao dos indicadores recalculados. A base gold
# armazena os indicadores arredondados em 4 casas decimais, entao uma pequena
# diferenca em relacao ao valor recalculado e esperada e nao indica erro.
INDICATOR_TOLERANCE = 1e-2

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
    "waste_risk_rank",
]

NUMERIC_COLUMNS = [
    "number_of_guests",
    "quantity_of_food",
    "wastage_food_amount",
    "wastage_rate",
    "wastage_per_guest",
    "waste_risk_rank",
]

pd = None


def ensure_dependencies() -> None:
    global pd
    try:
        import pandas as pandas_module
    except ModuleNotFoundError as exc:
        missing = exc.name or "dependencia desconhecida"
        raise SystemExit(
            f"Dependencia ausente: {missing}. Instale pandas antes de validar."
        ) from exc
    pd = pandas_module


@dataclass
class Check:
    """Resultado de uma verificacao individual.

    `critical` marca verificacoes que, ao falhar, invalidam a camada gold e
    fazem o script terminar com codigo 1.
    """

    nome: str
    passou: bool
    detalhe: str
    critical: bool = True


def load_data(path: Path) -> "pd.DataFrame":
    if not path.exists():
        raise FileNotFoundError(
            f"Arquivo de dados nao encontrado: {path}. "
            "Inclua a camada gold neste caminho ou use --data CAMINHO_DO_CSV."
        )

    df = pd.read_csv(path, encoding="utf-8")
    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def check_columns(df: "pd.DataFrame") -> Check:
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        return Check(
            "Colunas obrigatorias",
            False,
            "Faltam colunas: " + ", ".join(missing),
        )
    return Check(
        "Colunas obrigatorias",
        True,
        f"Todas as {len(REQUIRED_COLUMNS)} colunas obrigatorias estao presentes.",
    )


def check_missing_values(df: "pd.DataFrame") -> Check:
    total = int(df[REQUIRED_COLUMNS].isna().sum().sum())
    return Check(
        "Valores ausentes",
        total == 0,
        f"Valores ausentes nas colunas obrigatorias: {total}.",
    )


def check_duplicates(df: "pd.DataFrame") -> Check:
    total = int(df.duplicated().sum())
    return Check(
        "Linhas duplicadas",
        total == 0,
        f"Linhas duplicadas: {total}.",
        critical=False,
    )


def check_logical_consistency(df: "pd.DataFrame") -> list[Check]:
    invalid_qty = int((df["quantity_of_food"] <= 0).sum())
    invalid_guests = int((df["number_of_guests"] <= 0).sum())
    invalid_waste = int((df["wastage_food_amount"] < 0).sum())
    waste_gt_qty = int((df["wastage_food_amount"] > df["quantity_of_food"]).sum())

    return [
        Check(
            "quantity_of_food > 0",
            invalid_qty == 0,
            f"Registros com quantidade produzida <= 0: {invalid_qty}.",
        ),
        Check(
            "number_of_guests > 0",
            invalid_guests == 0,
            f"Registros com numero de convidados <= 0: {invalid_guests}.",
        ),
        Check(
            "wastage_food_amount >= 0",
            invalid_waste == 0,
            f"Registros com desperdicio negativo: {invalid_waste}.",
        ),
        Check(
            "wastage_food_amount <= quantity_of_food",
            waste_gt_qty == 0,
            f"Registros com desperdicio maior que a quantidade produzida: {waste_gt_qty}.",
        ),
    ]


def check_indicators(df: "pd.DataFrame") -> list[Check]:
    checks: list[Check] = []

    # wastage_rate = wastage_food_amount / quantity_of_food * 100
    calc_rate = 100 * df["wastage_food_amount"] / df["quantity_of_food"]
    max_rate_delta = float((df["wastage_rate"] - calc_rate).abs().max())
    checks.append(
        Check(
            "wastage_rate (formula)",
            max_rate_delta <= INDICATOR_TOLERANCE,
            f"Maior diferenca entre wastage_rate informado e recalculado: "
            f"{max_rate_delta:.6f} p.p. (tolerancia {INDICATOR_TOLERANCE}).",
        )
    )

    # wastage_per_guest = wastage_food_amount / number_of_guests
    calc_guest = df["wastage_food_amount"] / df["number_of_guests"]
    max_guest_delta = float((df["wastage_per_guest"] - calc_guest).abs().max())
    checks.append(
        Check(
            "wastage_per_guest (formula)",
            max_guest_delta <= INDICATOR_TOLERANCE,
            f"Maior diferenca entre wastage_per_guest informado e recalculado: "
            f"{max_guest_delta:.6f} (tolerancia {INDICATOR_TOLERANCE}).",
        )
    )

    # media de wastage_rate por event_profile (coluna auxiliar, se presente)
    if "mean_wastage_rate_by_profile" in df.columns:
        calc_profile_mean = df.groupby("event_profile", observed=True)[
            "wastage_rate"
        ].transform("mean")
        max_profile_delta = float(
            (df["mean_wastage_rate_by_profile"] - calc_profile_mean).abs().max()
        )
        checks.append(
            Check(
                "mean_wastage_rate_by_profile (media por perfil)",
                max_profile_delta <= INDICATOR_TOLERANCE,
                f"Maior diferenca entre a media por perfil informada e recalculada: "
                f"{max_profile_delta:.6f} (tolerancia {INDICATOR_TOLERANCE}).",
                critical=False,
            )
        )

    # waste_risk_rank: ranking (1 = maior risco) dos perfis pela taxa media
    # de desperdicio em ordem decrescente.
    profile_mean = (
        df.groupby("event_profile", observed=True)["wastage_rate"]
        .mean()
        .sort_values(ascending=False)
    )
    expected_rank = {
        profile: rank for rank, profile in enumerate(profile_mean.index, start=1)
    }
    calc_rank = df["event_profile"].map(expected_rank)
    rank_matches = bool((calc_rank == df["waste_risk_rank"]).all())
    checks.append(
        Check(
            "waste_risk_rank (ranking por perfil)",
            rank_matches,
            "waste_risk_rank corresponde ao ranking decrescente da taxa media por "
            f"perfil ({df['waste_risk_rank'].nunique()} perfis distintos)."
            if rank_matches
            else "waste_risk_rank NAO corresponde ao ranking decrescente da taxa "
            "media por perfil.",
        )
    )

    return checks


def run_all_checks(df: "pd.DataFrame") -> list[Check]:
    checks: list[Check] = [check_columns(df)]

    # Sem as colunas obrigatorias nao faz sentido seguir com as demais checagens.
    if not checks[0].passou:
        return checks

    checks.append(check_missing_values(df))
    checks.append(check_duplicates(df))
    checks.extend(check_logical_consistency(df))
    checks.extend(check_indicators(df))
    return checks


def print_report(path: Path, df: "pd.DataFrame", checks: list[Check]) -> bool:
    print("=" * 70)
    print("Validacao da camada gold - Parte 3")
    print("=" * 70)
    print(f"Arquivo: {path}")
    print(f"Linhas: {len(df)} | Colunas: {len(df.columns)}")
    print("-" * 70)

    ok = True
    for check in checks:
        status = "OK " if check.passou else ("FALHA" if check.critical else "AVISO")
        print(f"[{status}] {check.nome}: {check.detalhe}")
        if not check.passou and check.critical:
            ok = False

    print("-" * 70)
    if ok:
        print("Resultado: camada gold VALIDA (nenhuma verificacao critica falhou).")
    else:
        print("Resultado: camada gold INVALIDA (verificacoes criticas falharam).")
    print("=" * 70)
    return ok


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Valida a camada gold (food_wastage_gold.csv)."
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=DEFAULT_DATA_PATH,
        help="Caminho para food_wastage_gold.csv.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_dependencies()
    df = load_data(args.data)
    checks = run_all_checks(df)
    ok = print_report(args.data, df, checks)
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
