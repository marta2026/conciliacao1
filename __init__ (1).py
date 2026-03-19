import io
import datetime
import streamlit as st
import pandas as pd
from utils.config import CFG
from utils.state import set_status, add_historico
from utils.helpers import (
    fmt_br, parse_br, calcular, get_mes_ano_label,
    auto_fill, gerar_excel, read_xls, MESES,
)


def render():
    emp_id = st.session_state.empresa
    emp = CFG["empresas"][emp_id]
    conta = st.session_state.conta

    if conta is None:
        st.session_state.page = "dashboard"
        st.rerun()

    hdr_color = emp["hdr"]
    acc_color = emp["acc"]

    # ── Topbar ──
    st.markdown(
        f"""
        <div class="topbar" style="background:#fff;border-bottom:3px solid {acc_color};color:#2D3748;">
          <div style="display:flex;align-items:center;gap:8px">
            <span style="font-size:11px;color:#718096">{emp['nome']} › {conta['tipo'].upper()} › {conta['nome']}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Sidebar ──
    with st.sidebar:
        if st.button("← Voltar ao Painel", use_container_width=True):
            st.session_state.page = "dashboard"
            st.session_state.conta = None
            st.rerun()
        st.markdown("---")
        st.markdown(f"**Empresa:** {emp['razao']}")
        st.markdown(f"**Conta:** {conta['nome']}")
        badge_txt = conta["tipo"].upper()
        st.markdown(f"**Tipo:** {badge_txt}")
        st.markdown(f"**Código:** `{conta['codigo']}`")

    # ── Content ──
    st.markdown("<div style='padding:20px 24px 60px'>", unsafe_allow_html=True)

    # Header
    tipo_color = "#1E40AF" if conta["tipo"] == "ativo" else "#9D174D"
    tipo_bg = "#DBEAFE" if conta["tipo"] == "ativo" else "#FCE7F3"
    st.markdown(
        f"""
        <span style="background:{tipo_bg};color:{tipo_color};padding:3px 10px;border-radius:3px;
              font-size:10px;font-weight:700;letter-spacing:.04em">{conta['tipo'].upper()}</span>
        <div class="sec-title" style="margin-top:6px">{conta['nome']}</div>
        <div style="font-family:monospace;font-size:11px;color:#718096;margin-bottom:22px">
          Conta: {conta['codigo']} · {emp['razao']}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── STEP 1 ──
    st.markdown(
        '<div class="step-card">'
        '<div class="step-n">Passo 01 de 02</div>'
        '<div class="step-h">Período e Dados</div>'
        '<div style="font-size:12px;color:#718096;margin-bottom:18px">'
        'Selecione o mês/ano de referência e preencha os valores para processar a conciliação.'
        '</div>',
        unsafe_allow_html=True,
    )

    # Period
    now = datetime.date.today()
    col_mes, col_ano, _ = st.columns([2, 1, 4])
    with col_mes:
        mes = st.selectbox(
            "Mês",
            options=[str(i).zfill(2) for i in range(1, 13)],
            format_func=lambda x: MESES[int(x) - 1],
            index=now.month - 1,
            key="ref_mes",
        )
    with col_ano:
        ano = st.number_input("Ano", min_value=2020, max_value=2099,
                              value=now.year, step=1, key="ref_ano")

    ref_label = get_mes_ano_label(mes, str(int(ano)))

    # ── Upload aux ──
    st.markdown("**📂 Relatório Auxiliar (opcional — preenchimento automático)**")
    uploaded = st.file_uploader(
        "Faça upload de XLSX, XLS, CSV, TXT ou JSON para auto-preencher os campos",
        type=["xlsx", "xls", "csv", "txt", "json"],
        key=f"upload_{conta['id']}",
        label_visibility="collapsed",
    )

    autofill_vals = {}
    if uploaded:
        rows = read_xls(uploaded.read(), uploaded.name)
        if rows:
            autofill_vals = auto_fill(rows, conta["campos"])
            if autofill_vals:
                st.success(f"✅ {len(autofill_vals)} campo(s) preenchido(s) automaticamente a partir de **{uploaded.name}**")
            else:
                st.info("ℹ️ Upload recebido, mas não foi possível identificar os valores automaticamente. Preencha manualmente.")

    # ── Manual fields ──
    st.markdown("**Valores da Conciliação**")
    campos = conta["campos"]
    n = len(campos)
    valores = []

    cols_per_row = 3
    rows_needed = (n + cols_per_row - 1) // cols_per_row
    campo_idx = 0

    for r in range(rows_needed):
        row_cols = st.columns(cols_per_row)
        for ci in range(cols_per_row):
            if campo_idx >= n:
                break
            campo = campos[campo_idx]
            default_val = autofill_vals.get(campo, None)
            if default_val is not None:
                default_str = fmt_br(default_val)
            else:
                default_str = ""
            with row_cols[ci]:
                raw = st.text_input(
                    campo,
                    value=default_str,
                    placeholder="0,00",
                    key=f"campo_{conta['id']}_{campo_idx}",
                )
                valores.append(parse_br(raw))
            campo_idx += 1

    # Pad if needed
    while len(valores) < n:
        valores.append(0.0)

    st.markdown("</div>", unsafe_allow_html=True)

    # Processar button
    all_filled = any(v != 0.0 for v in valores)
    col_btn, _ = st.columns([2, 5])
    with col_btn:
        processar = st.button(
            "⚡ Processar Conciliação",
            disabled=not all_filled,
            type="primary",
            use_container_width=True,
            key="btn_processar",
        )

    # ── STEP 2 — Results ──
    if processar and all_filled:
        calc = calcular(campos, valores)

        # Save to history
        hist_item = {
            "emp": emp_id,
            "id": conta["id"],
            "conta": conta["nome"],
            "codigo": conta["codigo"],
            "ico": conta["icon"],
            "ref": ref_label,
            "diff": abs(calc["diff"]),
            "ok": calc["ok"],
        }
        add_historico(hist_item)
        set_status(emp_id, conta["id"], "ok" if calc["ok"] else "pendente")
        st.session_state.resultado = {
            "calc": calc,
            "valores": valores,
            "campos": campos,
            "ref_label": ref_label,
            "conta": conta,
            "emp": emp,
        }

    res = st.session_state.get("resultado")
    # Only show result for current conta
    if res and res.get("conta", {}).get("id") == conta["id"]:
        _render_resultado(res, acc_color)

    st.markdown("</div>", unsafe_allow_html=True)


def _render_resultado(res, acc_color):
    calc = res["calc"]
    valores = res["valores"]
    campos = res["campos"]
    ref_label = res["ref_label"]
    conta = res["conta"]
    emp = res["emp"]

    st.markdown("---")
    st.markdown(
        '<div class="step-card">'
        '<div class="step-n">Passo 02 de 02</div>'
        '<div class="step-h">Resultado da Conciliação</div>',
        unsafe_allow_html=True,
    )

    # KPIs
    k1, k2, k3 = st.columns(3)
    k1.markdown(
        f'<div class="r-kpi"><div class="r-kpi-lbl">Saldo Razão</div>'
        f'<div class="r-kpi-val">{fmt_br(calc["sR"])}</div>'
        f'<div class="r-kpi-sub">{ref_label}</div></div>',
        unsafe_allow_html=True,
    )
    k2.markdown(
        f'<div class="r-kpi"><div class="r-kpi-lbl">Rel. Auxiliar</div>'
        f'<div class="r-kpi-val">{fmt_br(calc["tA"])}</div>'
        f'<div class="r-kpi-sub">Composição calculada</div></div>',
        unsafe_allow_html=True,
    )
    diff_color = "#27AE60" if calc["ok"] else "#E74C3C"
    diff_sub = "✓ Zerada" if calc["ok"] else "⚠ Divergência"
    k3.markdown(
        f'<div class="r-kpi"><div class="r-kpi-lbl">Diferença</div>'
        f'<div class="r-kpi-val" style="color:{diff_color}">{fmt_br(abs(calc["diff"]))}</div>'
        f'<div class="r-kpi-sub">{diff_sub}</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Composition table ──
    st.markdown(
        '<div style="font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;'
        'color:#A0AEC0;margin-bottom:8px;padding-bottom:8px;border-bottom:1px solid #E2E8F0">'
        'Composição do Saldo — Relatório Auxiliar</div>',
        unsafe_allow_html=True,
    )
    campos_aux = campos[:-1]
    is_simple = len(campos) == 2
    table_rows = []
    if is_simple:
        table_rows.append({"Descrição": campos[0], "Valor (R$)": fmt_br(calc["tA"]), "D/C": "D"})
    else:
        for i, (campo, val) in enumerate(zip(campos_aux, valores[:-1])):
            table_rows.append({
                "Descrição": campo,
                "Valor (R$)": fmt_br(val),
                "D/C": "D" if i % 2 == 0 else "C",
            })
        table_rows.append({"Descrição": "Total Auxiliar", "Valor (R$)": fmt_br(calc["tA"]), "D/C": ""})
    table_rows.append({"Descrição": "Saldo Razão", "Valor (R$)": fmt_br(calc["sR"]), "D/C": ""})

    df_table = pd.DataFrame(table_rows)
    st.dataframe(df_table, use_container_width=True, hide_index=True)

    # ── Diff box ──
    if calc["ok"]:
        st.markdown(
            f'<div class="diff-box-ok">'
            f'✓ Conciliação Zerada — Diferença: {fmt_br(abs(calc["diff"]))}'
            f' &nbsp;<strong>[APROVADA]</strong></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="diff-box-nok">'
            f'⚠ Conciliação com Divergência — Diferença: {fmt_br(abs(calc["diff"]))}'
            f' &nbsp;<strong>[REVISAR]</strong></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="note-box"><strong>⚠ Atenção:</strong> Divergência de '
            f'<strong>{fmt_br(abs(calc["diff"]))}</strong>. Verifique os lançamentos do período.</div>',
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Action buttons ──
    col_novo, col_xls, col_back = st.columns([2, 2, 5])

    with col_novo:
        if st.button("← Novo período", key="btn_novo"):
            st.session_state.resultado = None
            st.rerun()

    with col_xls:
        xls_bytes = gerar_excel(conta, emp, valores, ref_label, calc)
        st.download_button(
            label="⬇ Baixar Excel",
            data=xls_bytes,
            file_name=f"conc_{conta['id']}_{ref_label.replace('/', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="btn_xls",
        )
