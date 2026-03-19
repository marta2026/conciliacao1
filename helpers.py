import streamlit as st
import plotly.graph_objects as go
from utils.config import CFG
from utils.state import get_status


def get_contas(emp_id: str):
    return [c for c in CFG["contas"] if emp_id in c["empresas"]]


def render():
    emp_id = st.session_state.empresa
    emp = CFG["empresas"][emp_id]
    contas = get_contas(emp_id)

    acc_color = emp["acc"]
    hdr_color = emp["hdr"]

    # ── Topbar ──
    st.markdown(
        f"""
        <div class="topbar" style="background:{hdr_color}">
          <div style="display:flex;align-items:center;gap:12px">
            <span style="font-size:20px">📊</span>
            <span class="topbar-title">CONCILIAÇÃO CONTÁBIL</span>
            <span style="color:rgba(255,255,255,.4);font-size:14px">|</span>
            <span class="topbar-name">{emp['nome']}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Sidebar ──
    with st.sidebar:
        st.markdown(f"**{emp['razao']}**")
        st.markdown("---")

        # Navigation
        st.markdown("**Navegação**")
        tabs = ["📊 Painel", "🕐 Histórico"]
        nav = st.radio("nav", tabs, label_visibility="collapsed",
                       index=0 if st.session_state.tab == "dashboard" else 1)
        st.session_state.tab = "dashboard" if "Painel" in nav else "historico"

        st.markdown("---")
        st.markdown("**Contas — Ativo**")
        for c in [x for x in contas if x["tipo"] == "ativo" and not x["wip"]]:
            lbl = f"{c['icon']} {c['nome'][:22]}{'…' if len(c['nome'])>22 else ''}"
            if st.button(lbl, key=f"sb_{c['id']}", use_container_width=True):
                st.session_state.conta = c
                st.session_state.page = "modulo"
                st.rerun()

        st.markdown("**Contas — Passivo**")
        for c in [x for x in contas if x["tipo"] == "passivo" and not x["wip"]]:
            lbl = f"{c['icon']} {c['nome'][:22]}{'…' if len(c['nome'])>22 else ''}"
            if st.button(lbl, key=f"sb_{c['id']}", use_container_width=True):
                st.session_state.conta = c
                st.session_state.page = "modulo"
                st.rerun()

        st.markdown("---")
        if st.button("↩ Trocar Empresa", use_container_width=True):
            st.session_state.page = "empresa"
            st.session_state.empresa = None
            st.rerun()

    # ── Main content ──
    main_pad = "padding: 20px 24px 60px;"
    st.markdown(f'<div style="{main_pad}">', unsafe_allow_html=True)

    tab = st.session_state.tab

    if tab == "dashboard":
        _render_dashboard(emp, contas, emp_id, acc_color)
    else:
        _render_historico(emp, emp_id)

    st.markdown("</div>", unsafe_allow_html=True)


def _render_dashboard(emp, contas, emp_id, acc_color):
    st.markdown(f'<div class="sec-title">Painel — {emp["nome"]}</div>', unsafe_allow_html=True)
    contas_ativas = [c for c in contas if not c["wip"]]
    ok_count = sum(1 for c in contas_ativas if get_status(emp_id, c["id"]) == "ok")
    pend_count = sum(1 for c in contas_ativas if get_status(emp_id, c["id"]) == "pendente")
    wip_count = sum(1 for c in contas if c["wip"])
    hist = [h for h in st.session_state.historico if h["emp"] == emp_id]

    st.markdown(
        f'<div class="sec-sub">{emp["razao"]} · {len(contas)} contas · {ok_count} OK · {pend_count} pendentes</div>',
        unsafe_allow_html=True,
    )

    # ── Banner ──
    st.markdown(
        '<div class="banner">📌 Selecione uma conta no menu lateral ou nos cards abaixo. '
        'Preencha os valores manualmente ou faça upload da planilha auxiliar (XLSX/CSV) para processar a conciliação.</div>',
        unsafe_allow_html=True,
    )

    # ── KPIs ──
    k1, k2, k3, k4 = st.columns(4)
    _kpi(k1, "✅", "#E8F8EF", "#27AE60", "Contas OK", ok_count, "Conciliadas")
    _kpi(k2, "⏳", "#FEF3E7", "#E67E22", "Pendentes", pend_count, "Aguardando")
    _kpi(k3, "📁", "#EBF5FB", acc_color, "Total", len(contas), f"{wip_count} em construção")
    _kpi(k4, "🕐", "#F5F6F7", "#718096", "Histórico", len(hist), "Registros")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts row ──
    c_left, c_right = st.columns(2)

    with c_left:
        st.markdown("**Status das Contas**")
        total = ok_count + pend_count + wip_count or 1
        fig = go.Figure(data=[go.Pie(
            labels=["OK", "Pendente", "Em construção"],
            values=[ok_count, pend_count, wip_count],
            hole=0.55,
            marker_colors=["#27AE60", "#E67E22", "#CBD5E1"],
            textinfo="label+value",
            textfont_size=11,
        )])
        fig.update_layout(
            margin=dict(t=10, b=10, l=0, r=0),
            height=200,
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with c_right:
        st.markdown("**Últimas Conciliações**")
        rec = hist[-5:][::-1]
        if rec:
            for h in rec:
                pill_cls = "pill-ok" if h["ok"] else "pill-pend"
                pill_txt = "OK" if h["ok"] else "DIVERGÊNCIA"
                st.markdown(
                    f"""
                    <div class="hist-row">
                      <div>
                        <span>{h['ico']}</span>
                        <strong style="margin-left:6px;font-size:12px">{h['conta']}</strong>
                        <div style="font-size:10px;color:#A0AEC0;font-family:monospace">{h['ref']}</div>
                      </div>
                      <span class="pill {pill_cls}">{pill_txt}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                '<div class="empty-state"><div class="ico">📭</div>'
                '<div class="sub">Nenhuma conciliação realizada</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── All accounts ──
    st.markdown("**Todas as Contas**")
    _render_contas_grid(contas, emp_id)


def _kpi(col, ico, bg, color, lbl, val, sub):
    col.markdown(
        f"""
        <div class="kpi-card">
          <div class="kpi-ico" style="background:{bg}">{ico}</div>
          <div>
            <div class="kpi-lbl">{lbl}</div>
            <div class="kpi-val" style="color:{color}">{val}</div>
            <div class="kpi-sub">{sub}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_contas_grid(contas, emp_id):
    for tipo in ["ativo", "passivo"]:
        grupo = [c for c in contas if c["tipo"] == tipo]
        if not grupo:
            continue
        st.markdown(
            f'<div style="font-size:10px;font-weight:700;color:#A0AEC0;letter-spacing:.08em;'
            f'text-transform:uppercase;margin:16px 0 10px;border-bottom:1px solid #E2E8F0;padding-bottom:4px">'
            f'{tipo.upper()}</div>',
            unsafe_allow_html=True,
        )
        cols = st.columns(4)
        for i, c in enumerate(grupo):
            with cols[i % 4]:
                status = get_status(emp_id, c["id"]) if not c["wip"] else "wip"
                pill_cls = "pill-ok" if status == "ok" else ("pill-wip" if status == "wip" else "pill-pend")
                pill_txt = "OK" if status == "ok" else ("EM BREVE" if status == "wip" else "PENDENTE")
                badge_cls = "badge-ativo" if tipo == "ativo" else "badge-passivo"

                st.markdown(
                    f"""
                    <div class="cc {tipo}" style="{'opacity:.55;cursor:default' if c['wip'] else ''}">
                      <div style="display:flex;justify-content:space-between;margin-bottom:8px">
                        <span style="font-size:20px">{c['icon']}</span>
                        <span class="pill {pill_cls}">{pill_txt}</span>
                      </div>
                      <div style="font-size:12px;font-weight:700;color:#2D3748;margin-bottom:3px">{c['nome']}</div>
                      <div style="font-family:monospace;font-size:10px;color:#A0AEC0">{c['codigo']}</div>
                      <div style="margin-top:6px"><span class="{badge_cls}">{tipo.upper()}</span></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if not c["wip"]:
                    if st.button(f"Abrir", key=f"cc_{c['id']}", use_container_width=True):
                        st.session_state.conta = c
                        st.session_state.page = "modulo"
                        st.rerun()


def _render_historico(emp, emp_id):
    st.markdown(f'<div class="sec-title">Histórico de Conciliações</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sec-sub">{emp["razao"]}</div>', unsafe_allow_html=True)

    hist = [h for h in st.session_state.historico if h["emp"] == emp_id]
    hist = hist[::-1]

    if not hist:
        st.markdown(
            '<div class="empty-state"><div class="ico">📭</div>'
            '<div class="ttl">Nenhum histórico</div>'
            '<div class="sub">As conciliações processadas aparecerão aqui</div></div>',
            unsafe_allow_html=True,
        )
        return

    import pandas as pd
    df = pd.DataFrame([
        {
            "Conta": f"{h['ico']} {h['conta']}",
            "Código": h["codigo"],
            "Período": h["ref"],
            "Diferença (R$)": f"{h['diff']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "Status": "✅ OK" if h["ok"] else "⚠ DIVERGÊNCIA",
        }
        for h in hist
    ])
    st.dataframe(df, use_container_width=True, hide_index=True)
