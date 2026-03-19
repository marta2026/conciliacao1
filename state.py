import io
import locale
from datetime import datetime

import pandas as pd


MESES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]


def fmt_br(value: float) -> str:
    """Format number as Brazilian currency string."""
    if value is None:
        return "—"
    try:
        return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "—"


def parse_br(text: str) -> float:
    """Parse Brazilian number string to float."""
    if not text:
        return 0.0
    try:
        clean = text.strip().replace(".", "").replace(",", ".")
        return float(clean)
    except Exception:
        return 0.0


def calcular(campos: list, valores: list) -> dict:
    """
    Compute reconciliation.
    Last campo = Saldo Razão (sR).
    Remaining campos alternate D (+) / C (-) starting from D.
    """
    n = len(valores)
    sR = valores[-1] if n > 0 else 0.0
    campos_aux = campos[:-1]

    if len(campos_aux) == 1:
        # Simple: single auxiliary = saldo razão
        tA = valores[0] if n > 1 else 0.0
    else:
        tA = 0.0
        for i, v in enumerate(valores[:-1]):
            if i % 2 == 0:
                tA += v
            else:
                tA -= v

    diff = sR - tA
    ok = abs(diff) < 0.01
    return {"sR": sR, "tA": tA, "diff": diff, "ok": ok}


def get_mes_ano_label(mes: str, ano: str) -> str:
    try:
        return f"{MESES[int(mes)-1]}/{ano}"
    except Exception:
        return f"{mes}/{ano}"


def auto_fill(data_rows: list, campos: list) -> dict:
    """
    Try to auto-fill campos from rows of [label, value] pairs.
    Returns dict: {campo_name: float}
    """
    flat = []
    for row in data_rows:
        if not row:
            continue
        row = list(row)
        for ci in range(len(row)):
            cell = row[ci]
            if isinstance(cell, str) and cell.strip():
                for j in range(ci + 1, len(row)):
                    if isinstance(row[j], (int, float)):
                        flat.append({"lbl": cell.strip().lower(), "val": abs(float(row[j]))})
                        break

    def find_val(kws):
        for kw in kws:
            hit = next((f["val"] for f in flat if kw in f["lbl"]), None)
            if hit is not None:
                return hit
        return None

    kw_razao = ["saldo razão", "saldo razao", "razão ", "razao "]
    kw_aux   = ["saldo relat", "posição", "posicao", "saldo do relat", "saldo auxiliar", "saldo da conta", "saldo em conta", "saldo report"]
    kw_ini   = ["saldo inicial", "saldo anterior"]
    kw_entr  = ["adiantamento", "retenção", "retencao", "apurado", "emissão", "emissao", "transaç", "nf recebid"]
    kw_saida = ["baixa", "recolhimento", "compensaç", "resgate", "repasse", "pagamento realiz"]

    result = {}
    if len(campos) == 2:
        v_aux   = find_val(kw_aux) or find_val(kw_ini)
        v_razao = find_val(kw_razao)
        if v_aux   is not None: result[campos[0]] = v_aux
        if v_razao is not None: result[campos[1]] = v_razao
    else:
        vals = {
            "ini":   find_val(kw_ini),
            "entr":  find_val(kw_entr),
            "saida": find_val(kw_saida),
            "razao": find_val(kw_razao),
            "aux":   find_val(kw_aux),
        }
        for i, campo in enumerate(campos):
            nome = campo.lower()
            v = None
            if "razã" in nome or "razao" in nome:
                v = vals["razao"]
            elif "inicial" in nome or "anterior" in nome:
                v = vals["ini"]
            elif "auxiliar" in nome or "relat" in nome:
                v = vals["aux"]
            elif any(k in nome for k in ["saída", "saida", "baixa", "recolh", "compensaç", "resgate", "repasse"]):
                v = vals["saida"]
            else:
                v = vals["entr"]
            if v is not None:
                result[campo] = v
    return result


def gerar_excel(conta: dict, empresa: dict, valores: list, ref_label: str, calc: dict) -> bytes:
    """Generate XLSX bytes for download."""
    campos = conta["campos"]
    rows = [
        [f"CONCILIAÇÃO — {conta['nome'].upper()}", "", ""],
        [f"{empresa['razao']}  |  Conta: {conta['codigo']}  |  Ref.: {ref_label}", "", ""],
        ["", "", ""],
        ["Descrição", "Valor (R$)", "D/C"],
    ]
    for i, (campo, val) in enumerate(zip(campos[:-1], valores[:-1])):
        dc = "D" if i % 2 == 0 else "C"
        rows.append([campo, val, dc])
    rows.append(["Total Auxiliar", calc["tA"], ""])
    rows.append(["Saldo Razão", calc["sR"], ""])
    rows.append(["DIFERENÇA", calc["diff"], "✓ ZERADA" if calc["ok"] else "⚠ REVISAR"])
    rows.append(["", "", ""])
    rows.append([f"Emitido em: {datetime.now().strftime('%d/%m/%Y')}", "", ""])

    df = pd.DataFrame(rows, columns=["Descrição", "Valor (R$)", "D/C"])
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Conciliação")
    return buf.getvalue()


def read_xls(file_bytes: bytes, filename: str) -> list:
    """Read uploaded XLS/CSV/TXT and return rows."""
    try:
        ext = filename.rsplit(".", 1)[-1].lower()
        buf = io.BytesIO(file_bytes)
        if ext == "xlsx":
            df = pd.read_excel(buf, header=None, engine="openpyxl")
        elif ext == "xls":
            try:
                df = pd.read_excel(buf, header=None, engine="xlrd")
            except Exception:
                df = pd.read_excel(buf, header=None)
        elif ext in ("csv", "txt"):
            try:
                df = pd.read_csv(buf, header=None, sep=None, engine="python")
            except Exception:
                df = pd.read_csv(io.BytesIO(file_bytes), header=None, sep=";")
        elif ext == "json":
            import json
            data = json.loads(file_bytes)
            df = pd.DataFrame(data)
        else:
            df = pd.read_excel(buf, header=None, engine="openpyxl")
        return df.values.tolist()
    except Exception:
        return []
