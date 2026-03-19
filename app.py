import streamlit as st
import io
import os
import datetime
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="Conciliação Contábil",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}
.stDeployButton {display: none;}
[data-testid="stToolbar"] {display: none;}
body, .stApp { background: #F7FAFC !important; font-family: 'Inter', sans-serif; font-size: 13px; }
.block-container { padding-top: 0 !important; padding-bottom: 0 !important; max-width: 100% !important; }

.topbar {
  padding: 14px 24px; display: flex; align-items: center;
  justify-content: space-between; box-shadow: 0 2px 8px rgba(0,0,0,.18);
  margin-bottom: 4px;
}
.topbar-title { color: rgba(255,255,255,.85); font-size: 12px; font-weight: 700; letter-spacing:.06em; text-transform:uppercase; }
.topbar-name { color:#fff; font-size:15px; font-weight:700; }

.kpi-card {
  background:#fff; border:1px solid #E2E8F0; border-radius:5px;
  padding:14px 16px; display:flex; align-items:center; gap:12px;
  box-shadow:0 1px 3px rgba(0,0,0,.04);
}
.kpi-ico { width:42px; height:42px; border-radius:8px; display:flex; align-items:center; justify-content:center; font-size:20px; flex-shrink:0; }
.kpi-lbl { font-size:10px; font-weight:700; color:#A0AEC0; text-transform:uppercase; letter-spacing:.04em; margin-bottom:2px; }
.kpi-val { font-size:26px; font-weight:700; line-height:1; }
.kpi-sub { font-size:10px; color:#A0AEC0; margin-top:2px; }

.cc { background:#fff; border:1px solid #E2E8F0; border-radius:5px; padding:14px; box-shadow:0 1px 3px rgba(0,0,0,.04); position:relative; overflow:hidden; }
.cc::before { content:''; position:absolute; top:0; left:0; right:0; height:3px; }
.cc.ativo::before { background: linear-gradient(90deg,#1D4ED8,#60A5FA); }
.cc.passivo::before { background: linear-gradient(90deg,#9D174D,#EC4899); }

.pill { display:inline-flex; align-items:center; gap:4px; padding:3px 8px; border-radius:3px; font-size:10px; font-weight:700; }
.pill-ok { background:#E8F8EF; color:#27AE60; }
.pill-pend { background:#FEF3E7; color:#E67E22; }
.pill-wip { background:#F0F1F3; color:#9BA5B0; }

.badge-ativo { background:#DBEAFE; color:#1E40AF; padding:2px 6px; border-radius:3px; font-size:9px; font-weight:700; }
.badge-passivo { background:#FCE7F3; color:#9D174D; padding:2px 6px; border-radius:3px; font-size:9px; font-weight:700; }

.diff-ok { background:#E8F8EF; border:1px solid #A7F3D0; border-radius:5px; padding:16px 20px; color:#27AE60; font-weight:700; font-size:15px; }
.diff-nok { background:#FDEDEC; border:1px solid #FECACA; border-radius:5px; padding:16px 20px; color:#E74C3C; font-weight:700; font-size:15px; }
.note-box { background:#FFF8E1; border:1px solid #FFE082; border-left:4px solid #F59E0B; border-radius:4px; padding:10px 14px; font-size:12px; color:#78350F; line-height:1.7; }
.banner { background:#EBF8FF; border-left:4px solid #2196C4; border-radius:4px; padding:12px 16px; font-size:12px; color:#1A6980; line-height:1.6; margin-bottom:16px; }

.r-kpi { background:#F7FAFC; border:1px solid #E2E8F0; border-radius:4px; padding:12px 14px; }
.r-kpi-lbl { font-size:10px; font-weight:700; color:#A0AEC0; text-transform:uppercase; letter-spacing:.04em; margin-bottom:3px; }
.r-kpi-val { font-family:monospace; font-size:18px; font-weight:700; }
.r-kpi-sub { font-size:10px; color:#A0AEC0; margin-top:2px; }

.hist-row { display:flex; align-items:center; justify-content:space-between; padding:8px 10px; border-radius:4px; background:#F7FAFC; margin-bottom:6px; font-size:12px; }
.sec-title { font-size:18px; font-weight:700; color:#2D3748; letter-spacing:-.02em; margin-bottom:4px; }
.sec-sub { font-size:12px; color:#718096; margin-bottom:20px; }
.step-n { font-size:10px; font-weight:700; letter-spacing:.08em; text-transform:uppercase; color:#A0AEC0; margin-bottom:4px; }
.step-h { font-size:15px; font-weight:700; color:#2D3748; margin-bottom:4px; }
.empty-state { text-align:center; padding:40px 20px; color:#718096; }

[data-testid="stSidebar"] { background:#fff !important; border-right:1px solid #E2E8F0 !important; }
.stButton > button { border-radius:4px !important; font-weight:700 !important; font-size:13px !important; }
</style>
""", unsafe_allow_html=True)

# ── CONFIG ─────────────────────────────────────────────────────────────────────
EMPRESAS = {
    "nc": {"id":"nc","nome":"Nutricash","razao":"NUTRICASH LTDA","hdr":"#1C3557","acc":"#2196C4","desc":"Benefícios, alimentação e gestão de pagamentos corporativos"},
    "mf": {"id":"mf","nome":"MaxiFrota","razao":"MAXIFROTA LTDA","hdr":"#003D78","acc":"#F5A800","desc":"Gestão de frotas, abastecimento e mobilidade corporativa"},
}

CONTAS = [
    {"id":"adto-forn","nome":"Adiantamento a Fornecedores","codigo":"18805000003","tipo":"ativo","icon":"🏭","empresas":["nc","mf"],"campos":["Saldo Relatório Auxiliar (Contas a Pagar)","Saldo Razão"],"wip":False},
    {"id":"adto-fer","nome":"Adiantamento de Férias","codigo":"18803000003","tipo":"ativo","icon":"🏖️","empresas":["nc","mf"],"campos":["Saldo Inicial","Adiantamentos do Período","Baixas (Folha)","Saldo Razão"],"wip":False},
    {"id":"adto-sal","nome":"Adiantamento de Salários","codigo":"18803000001","tipo":"ativo","icon":"💼","empresas":["nc","mf"],"campos":["Saldo Inicial","Adiantamentos do Período","Baixas (Folha)","Saldo Razão"],"wip":False},
    {"id":"irrf-antec","nome":"IRRF Antecipado","codigo":"18845100003","tipo":"ativo","icon":"💰","empresas":["nc","mf"],"campos":["Saldo Inicial","Retenções do Período","Compensações / Baixas","Saldo Razão"],"wip":False},
    {"id":"irrf-serv","nome":"IRRF s/ Serviços a Recolher","codigo":"49420100001","tipo":"passivo","icon":"📋","empresas":["nc","mf"],"campos":["Saldo Inicial","IRRF Retido no Período","Recolhimentos (DARF)","Saldo Razão"],"wip":False},
    {"id":"irrf-com","nome":"IRRF s/ Comissões a Recolher","codigo":"49420100002","tipo":"passivo","icon":"📋","empresas":["nc","mf"],"campos":["Saldo Inicial","IRRF Retido no Período","Recolhimentos (DARF)","Saldo Razão"],"wip":False},
    {"id":"pis","nome":"PIS a Recolher","codigo":"49420900001","tipo":"passivo","icon":"🔖","empresas":["nc","mf"],"campos":["Saldo Inicial","PIS Apurado","Recolhimentos","Saldo Razão"],"wip":False},
    {"id":"cofins","nome":"COFINS a Recolher","codigo":"49420900002","tipo":"passivo","icon":"🔖","empresas":["nc","mf"],"campos":["Saldo Inicial","COFINS Apurado","Recolhimentos","Saldo Razão"],"wip":False},
    {"id":"iss","nome":"ISS a Recolher","codigo":"49420900003","tipo":"passivo","icon":"🏙️","empresas":["nc","mf"],"campos":["Saldo Inicial","ISS Apurado","Recolhimentos","Saldo Razão"],"wip":False},
    {"id":"forn","nome":"Fornecedores","codigo":"49992000001","tipo":"passivo","icon":"🤝","empresas":["nc","mf"],"campos":["Saldo Inicial","NF Recebidas","Pagamentos Realizados","Saldo Razão"],"wip":False},
    {"id":"rede-conv","nome":"Rede Conveniada a Pagar","codigo":"49992000002","tipo":"passivo","icon":"🏪","empresas":["nc"],"campos":["Saldo Inicial","Transações do Período","Repasses Realizados","Saldo Razão"],"wip":False},
    {"id":"moeda-pat","nome":"Moeda Eletrônica PAT Papel","codigo":"49992000022","tipo":"passivo","icon":"🃏","empresas":["nc"],"campos":["Saldo Inicial","Emissões do Período","Resgates / Utilizações","Saldo Razão"],"wip":False},
    {"id":"moeda-frt","nome":"Moeda Eletrônica Frota Papel","codigo":"49992000023","tipo":"passivo","icon":"⛽","empresas":["mf"],"campos":["Saldo Inicial","Emissões do Período","Resgates / Utilizações","Saldo Razão"],"wip":False},
]

MESES = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]

# ── HELPERS ────────────────────────────────────────────────────────────────────
def fmt_br(v):
    if v is None: return "—"
    try: return f"{v:,.2f}".replace(",","X").replace(".",",").replace("X",".")
    except: return "—"

def parse_br(t):
    if not t: return 0.0
    try: return float(t.strip().replace(".","").replace(",","."))
    except: return 0.0

def calcular(campos, valores):
    sR = valores[-1] if valores else 0.0
    if len(campos) == 2:
        tA = valores[0] if len(valores) > 1 else 0.0
    else:
        tA = 0.0
        for i, v in enumerate(valores[:-1]):
            tA = tA + v if i % 2 == 0 else tA - v
    diff = sR - tA
    return {"sR": sR, "tA": tA, "diff": diff, "ok": abs(diff) < 0.01}

def get_status(emp_id, conta_id):
    return st.session_state.status.get(f"{emp_id}_{conta_id}", "pendente")

def set_status(emp_id, conta_id, val):
    st.session_state.status[f"{emp_id}_{conta_id}"] = val

def add_historico(item):
    hist = [h for h in st.session_state.historico
            if not (h["emp"]==item["emp"] and h["id"]==item["id"] and h["ref"]==item["ref"])]
    hist.append(item)
    st.session_state.historico = hist

def get_contas(emp_id):
    return [c for c in CONTAS if emp_id in c["empresas"]]

def auto_fill(rows, campos):
    flat = []
    for row in rows:
        if not row: continue
        row = list(row)
        for ci in range(len(row)):
            cell = row[ci]
            if isinstance(cell, str) and cell.strip():
                for j in range(ci+1, len(row)):
                    if isinstance(row[j], (int, float)):
                        flat.append({"lbl": cell.strip().lower(), "val": abs(float(row[j]))})
                        break
    def find(kws):
        for kw in kws:
            hit = next((f["val"] for f in flat if kw in f["lbl"]), None)
            if hit is not None: return hit
        return None
    kw_razao = ["saldo razão","saldo razao","razão ","razao "]
    kw_aux   = ["saldo relat","posição","posicao","saldo auxiliar","saldo da conta","saldo em conta"]
    kw_ini   = ["saldo inicial","saldo anterior"]
    kw_entr  = ["adiantamento","retenção","retencao","apurado","emissão","emissao","transaç","nf recebid"]
    kw_saida = ["baixa","recolhimento","compensaç","resgate","repasse","pagamento realiz"]
    result = {}
    if len(campos) == 2:
        v = find(kw_aux) or find(kw_ini)
        if v is not None: result[campos[0]] = v
        v = find(kw_razao)
        if v is not None: result[campos[1]] = v
    else:
        vals = {"ini":find(kw_ini),"entr":find(kw_entr),"saida":find(kw_saida),"razao":find(kw_razao),"aux":find(kw_aux)}
        for i, campo in enumerate(campos):
            n = campo.lower()
            v = None
            if "razã" in n or "razao" in n: v = vals["razao"]
            elif "inicial" in n or "anterior" in n: v = vals["ini"]
            elif "auxiliar" in n or "relat" in n: v = vals["aux"]
            elif any(k in n for k in ["saída","saida","baixa","recolh","compensaç","resgate","repasse"]): v = vals["saida"]
            else: v = vals["entr"]
            if v is not None: result[campo] = v
    return result

def read_upload(file_bytes, filename):
    try:
        ext = filename.rsplit(".",1)[-1].lower()
        buf = io.BytesIO(file_bytes)
        if ext == "xlsx": df = pd.read_excel(buf, header=None, engine="openpyxl")
        elif ext == "xls":
            try: df = pd.read_excel(buf, header=None, engine="xlrd")
            except: df = pd.read_excel(buf, header=None)
        elif ext in ("csv","txt"):
            try: df = pd.read_csv(buf, header=None, sep=None, engine="python")
            except: df = pd.read_csv(io.BytesIO(file_bytes), header=None, sep=";")
        elif ext == "json":
            import json
            df = pd.DataFrame(json.loads(file_bytes))
        else: df = pd.read_excel(buf, header=None, engine="openpyxl")
        return df.values.tolist()
    except: return []

def gerar_excel(conta, emp, valores, ref_label, calc):
    campos = conta["campos"]
    rows = [
        [f"CONCILIAÇÃO — {conta['nome'].upper()}","",""],
        [f"{emp['razao']}  |  Conta: {conta['codigo']}  |  Ref.: {ref_label}","",""],
        ["","",""],
        ["Descrição","Valor (R$)","D/C"],
    ]
    for i,(campo,val) in enumerate(zip(campos[:-1],valores[:-1])):
        rows.append([campo, val, "D" if i%2==0 else "C"])
    rows += [["Total Auxiliar",calc["tA"],""],["Saldo Razão",calc["sR"],""],
             ["DIFERENÇA",calc["diff"],"✓ ZERADA" if calc["ok"] else "⚠ REVISAR"],
             ["","",""],
             [f"Emitido em: {datetime.date.today().strftime('%d/%m/%Y')}","",""]]
    buf = io.BytesIO()
    pd.DataFrame(rows).to_excel(buf, index=False, header=False, engine="openpyxl")
    return buf.getvalue()

# ── STATE INIT ─────────────────────────────────────────────────────────────────
for k,v in [("page","empresa"),("empresa",None),("conta",None),("tab","dashboard"),
            ("historico",[]),("status",{}),("resultado",None)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: EMPRESA
# ══════════════════════════════════════════════════════════════════════════════
def page_empresa():
    st.markdown('<div class="topbar" style="background:#1C3557"><span class="topbar-title">📊 Conciliação Contábil</span></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div style="text-align:center;font-size:22px;font-weight:700;color:#2D3748">Selecione a empresa</div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center;font-size:13px;color:#718096;margin-bottom:32px">Escolha a empresa para acessar o módulo de conciliação contábil</div>', unsafe_allow_html=True)

    _, col_nc, col_mf, _ = st.columns([1,2,2,1])
    with col_nc:
        st.markdown("""
        <div class="cc ativo" style="text-align:center;padding:36px 32px;border-radius:12px;border:1.5px solid #2196C4">
          <div style="font-size:48px;margin-bottom:12px">🏢</div>
          <div style="font-size:18px;font-weight:700;color:#2D3748;margin-bottom:6px">Nutricash</div>
          <div style="font-size:12px;color:#718096;line-height:1.5;margin-bottom:20px">Benefícios, alimentação e gestão de pagamentos corporativos</div>
        </div>""", unsafe_allow_html=True)
        if st.button("ACESSAR → Nutricash", use_container_width=True, type="primary", key="btn_nc"):
            st.session_state.empresa = "nc"
            st.session_state.page = "dashboard"
            st.rerun()

    with col_mf:
        st.markdown("""
        <div class="cc passivo" style="text-align:center;padding:36px 32px;border-radius:12px;border:1.5px solid #F5A800">
          <div style="font-size:48px;margin-bottom:12px">🚛</div>
          <div style="font-size:18px;font-weight:700;color:#2D3748;margin-bottom:6px">MaxiFrota</div>
          <div style="font-size:12px;color:#718096;line-height:1.5;margin-bottom:20px">Gestão de frotas, abastecimento e mobilidade corporativa</div>
        </div>""", unsafe_allow_html=True)
        if st.button("ACESSAR → MaxiFrota", use_container_width=True, key="btn_mf"):
            st.session_state.empresa = "mf"
            st.session_state.page = "dashboard"
            st.rerun()

    st.markdown('<div style="text-align:center;font-size:11px;color:#A0AEC0;margin-top:40px">Sistema de Conciliação Contábil v4</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def page_dashboard():
    emp_id = st.session_state.empresa
    emp = EMPRESAS[emp_id]
    contas = get_contas(emp_id)

    st.markdown(f'<div class="topbar" style="background:{emp["hdr"]}"><div style="display:flex;align-items:center;gap:12px"><span style="font-size:20px">📊</span><span class="topbar-title">CONCILIAÇÃO CONTÁBIL</span><span style="color:rgba(255,255,255,.4)">|</span><span class="topbar-name">{emp["nome"]}</span></div></div>', unsafe_allow_html=True)

    # ── Sidebar ──
    with st.sidebar:
        st.markdown(f"**{emp['razao']}**")
        st.markdown("---")
        tabs = ["📊 Painel", "🕐 Histórico"]
        nav = st.radio("nav", tabs, label_visibility="collapsed",
                       index=0 if st.session_state.tab == "dashboard" else 1)
        st.session_state.tab = "dashboard" if "Painel" in nav else "historico"
        st.markdown("---")
        st.markdown("**Ativo**")
        for c in [x for x in contas if x["tipo"]=="ativo" and not x["wip"]]:
            lbl = f"{c['icon']} {c['nome'][:22]}{'…' if len(c['nome'])>22 else ''}"
            if st.button(lbl, key=f"sb_{c['id']}", use_container_width=True):
                st.session_state.conta = c
                st.session_state.page = "modulo"
                st.rerun()
        st.markdown("**Passivo**")
        for c in [x for x in contas if x["tipo"]=="passivo" and not x["wip"]]:
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

    # ── Content ──
    if st.session_state.tab == "dashboard":
        _dash_content(emp, contas, emp_id)
    else:
        _hist_content(emp, emp_id)


def _dash_content(emp, contas, emp_id):
    contas_ativas = [c for c in contas if not c["wip"]]
    ok_n   = sum(1 for c in contas_ativas if get_status(emp_id,c["id"])=="ok")
    pend_n = sum(1 for c in contas_ativas if get_status(emp_id,c["id"])=="pendente")
    wip_n  = sum(1 for c in contas if c["wip"])
    hist   = [h for h in st.session_state.historico if h["emp"]==emp_id]

    st.markdown(f'<div class="sec-title">Painel — {emp["nome"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sec-sub">{emp["razao"]} · {len(contas)} contas · {ok_n} OK · {pend_n} pendentes</div>', unsafe_allow_html=True)
    st.markdown('<div class="banner">📌 Selecione uma conta no menu lateral ou nos cards abaixo para iniciar a conciliação.</div>', unsafe_allow_html=True)

    # KPIs
    k1,k2,k3,k4 = st.columns(4)
    for col, ico, bg, cor, lbl, val, sub in [
        (k1,"✅","#E8F8EF","#27AE60","Contas OK",ok_n,"Conciliadas"),
        (k2,"⏳","#FEF3E7","#E67E22","Pendentes",pend_n,"Aguardando"),
        (k3,"📁","#EBF5FB",emp["acc"],"Total",len(contas),f"{wip_n} em construção"),
        (k4,"🕐","#F5F6F7","#718096","Histórico",len(hist),"Registros"),
    ]:
        col.markdown(f'<div class="kpi-card"><div class="kpi-ico" style="background:{bg}">{ico}</div><div><div class="kpi-lbl">{lbl}</div><div class="kpi-val" style="color:{cor}">{val}</div><div class="kpi-sub">{sub}</div></div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts
    c_left, c_right = st.columns(2)
    with c_left:
        st.markdown("**Status das Contas**")
        fig = go.Figure(data=[go.Pie(
            labels=["OK","Pendente","Em construção"],
            values=[ok_n, pend_n, wip_n],
            hole=0.55,
            marker_colors=["#27AE60","#E67E22","#CBD5E1"],
            textinfo="label+value", textfont_size=11,
        )])
        fig.update_layout(margin=dict(t=10,b=10,l=0,r=0), height=200, showlegend=False, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    with c_right:
        st.markdown("**Últimas Conciliações**")
        rec = hist[-5:][::-1]
        if rec:
            for h in rec:
                pill = "pill-ok" if h["ok"] else "pill-pend"
                txt  = "OK" if h["ok"] else "DIVERGÊNCIA"
                st.markdown(f'<div class="hist-row"><div><span>{h["ico"]}</span><strong style="margin-left:6px">{h["conta"]}</strong><div style="font-size:10px;color:#A0AEC0;font-family:monospace">{h["ref"]}</div></div><span class="pill {pill}">{txt}</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="empty-state"><div style="font-size:32px">📭</div><div>Nenhuma conciliação realizada</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**Todas as Contas**")

    for tipo in ["ativo","passivo"]:
        grupo = [c for c in contas if c["tipo"]==tipo]
        if not grupo: continue
        st.markdown(f'<div style="font-size:10px;font-weight:700;color:#A0AEC0;text-transform:uppercase;letter-spacing:.08em;margin:16px 0 10px;border-bottom:1px solid #E2E8F0;padding-bottom:4px">{tipo.upper()}</div>', unsafe_allow_html=True)
        cols = st.columns(4)
        for i, c in enumerate(grupo):
            with cols[i%4]:
                status = get_status(emp_id,c["id"]) if not c["wip"] else "wip"
                pill_c = "pill-ok" if status=="ok" else ("pill-wip" if status=="wip" else "pill-pend")
                pill_t = "OK" if status=="ok" else ("EM BREVE" if status=="wip" else "PENDENTE")
                badge  = "badge-ativo" if tipo=="ativo" else "badge-passivo"
                st.markdown(f'<div class="cc {tipo}" style="{"opacity:.55" if c["wip"] else ""}"><div style="display:flex;justify-content:space-between;margin-bottom:8px"><span style="font-size:20px">{c["icon"]}</span><span class="pill {pill_c}">{pill_t}</span></div><div style="font-size:12px;font-weight:700;color:#2D3748;margin-bottom:3px">{c["nome"]}</div><div style="font-family:monospace;font-size:10px;color:#A0AEC0">{c["codigo"]}</div><div style="margin-top:6px"><span class="{badge}">{tipo.upper()}</span></div></div>', unsafe_allow_html=True)
                if not c["wip"]:
                    if st.button("Abrir", key=f"cc_{c['id']}", use_container_width=True):
                        st.session_state.conta = c
                        st.session_state.page = "modulo"
                        st.rerun()


def _hist_content(emp, emp_id):
    st.markdown(f'<div class="sec-title">Histórico de Conciliações</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sec-sub">{emp["razao"]}</div>', unsafe_allow_html=True)
    hist = [h for h in st.session_state.historico if h["emp"]==emp_id][::-1]
    if not hist:
        st.markdown('<div class="empty-state"><div style="font-size:32px">📭</div><div style="font-weight:700;margin-top:8px">Nenhum histórico</div><div>As conciliações processadas aparecerão aqui</div></div>', unsafe_allow_html=True)
        return
    df = pd.DataFrame([{
        "Conta": f"{h['ico']} {h['conta']}",
        "Código": h["codigo"],
        "Período": h["ref"],
        "Diferença (R$)": fmt_br(h["diff"]),
        "Status": "✅ OK" if h["ok"] else "⚠ DIVERGÊNCIA",
    } for h in hist])
    st.dataframe(df, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: MÓDULO
# ══════════════════════════════════════════════════════════════════════════════
def page_modulo():
    emp_id = st.session_state.empresa
    emp    = EMPRESAS[emp_id]
    conta  = st.session_state.conta
    if conta is None:
        st.session_state.page = "dashboard"
        st.rerun()

    st.markdown(f'<div class="topbar" style="background:#fff;border-bottom:3px solid {emp["acc"]};"><span style="font-size:11px;color:#718096">{emp["nome"]} › {conta["tipo"].upper()} › {conta["nome"]}</span></div>', unsafe_allow_html=True)

    with st.sidebar:
        if st.button("← Voltar ao Painel", use_container_width=True):
            st.session_state.page = "dashboard"
            st.session_state.conta = None
            st.session_state.resultado = None
            st.rerun()
        st.markdown("---")
        st.markdown(f"**Empresa:** {emp['razao']}")
        st.markdown(f"**Conta:** {conta['nome']}")
        st.markdown(f"**Código:** `{conta['codigo']}`")
        st.markdown(f"**Tipo:** {conta['tipo'].upper()}")

    # Header
    tipo_bg    = "#DBEAFE" if conta["tipo"]=="ativo" else "#FCE7F3"
    tipo_color = "#1E40AF" if conta["tipo"]=="ativo" else "#9D174D"
    st.markdown(f'<span style="background:{tipo_bg};color:{tipo_color};padding:3px 10px;border-radius:3px;font-size:10px;font-weight:700">{conta["tipo"].upper()}</span>', unsafe_allow_html=True)
    st.markdown(f'<div class="sec-title" style="margin-top:6px">{conta["nome"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-family:monospace;font-size:11px;color:#718096;margin-bottom:22px">Conta: {conta["codigo"]} · {emp["razao"]}</div>', unsafe_allow_html=True)

    # ── STEP 1 ──
    with st.container():
        st.markdown('<div class="step-n">Passo 01 de 02</div><div class="step-h">Período e Dados</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:12px;color:#718096;margin-bottom:14px">Selecione o mês/ano e preencha os valores. Faça upload de planilha para auto-preenchimento.</div>', unsafe_allow_html=True)

        now = datetime.date.today()
        col_mes, col_ano, _ = st.columns([2,1,4])
        with col_mes:
            mes = st.selectbox("Mês", [str(i).zfill(2) for i in range(1,13)],
                               format_func=lambda x: MESES[int(x)-1],
                               index=now.month-1, key="ref_mes")
        with col_ano:
            ano = st.number_input("Ano", min_value=2020, max_value=2099,
                                  value=now.year, step=1, key="ref_ano")
        ref_label = f"{MESES[int(mes)-1]}/{int(ano)}"

        # Upload
        st.markdown("**📂 Upload de planilha auxiliar (opcional)**")
        uploaded = st.file_uploader(
            "XLSX, XLS, CSV, TXT, JSON",
            type=["xlsx","xls","csv","txt","json"],
            key=f"upload_{conta['id']}",
            label_visibility="collapsed",
        )
        autofill_vals = {}
        if uploaded:
            rows = read_upload(uploaded.read(), uploaded.name)
            if rows:
                autofill_vals = auto_fill(rows, conta["campos"])
                if autofill_vals:
                    st.success(f"✅ {len(autofill_vals)} campo(s) preenchido(s) automaticamente de **{uploaded.name}**")
                else:
                    st.info("ℹ️ Arquivo recebido. Preencha os valores manualmente.")

        # Campos
        st.markdown("**Valores da Conciliação**")
        campos  = conta["campos"]
        valores = []
        cols_n  = 3
        rows_n  = (len(campos) + cols_n - 1) // cols_n
        idx = 0
        for _ in range(rows_n):
            row_cols = st.columns(cols_n)
            for ci in range(cols_n):
                if idx >= len(campos): break
                campo = campos[idx]
                default = fmt_br(autofill_vals[campo]) if campo in autofill_vals else ""
                with row_cols[ci]:
                    raw = st.text_input(campo, value=default, placeholder="0,00",
                                        key=f"campo_{conta['id']}_{idx}")
                    valores.append(parse_br(raw))
                idx += 1
        while len(valores) < len(campos):
            valores.append(0.0)

    # Processar
    all_filled = any(v != 0.0 for v in valores)
    col_btn, _ = st.columns([2,5])
    with col_btn:
        processar = st.button("⚡ Processar Conciliação", disabled=not all_filled,
                              type="primary", use_container_width=True, key="btn_proc")

    if processar and all_filled:
        calc = calcular(campos, valores)
        add_historico({"emp":emp_id,"id":conta["id"],"conta":conta["nome"],"codigo":conta["codigo"],
                       "ico":conta["icon"],"ref":ref_label,"diff":abs(calc["diff"]),"ok":calc["ok"]})
        set_status(emp_id, conta["id"], "ok" if calc["ok"] else "pendente")
        st.session_state.resultado = {"calc":calc,"valores":valores,"campos":campos,
                                       "ref_label":ref_label,"conta":conta,"emp":emp}

    # ── STEP 2 ──
    res = st.session_state.resultado
    if res and res.get("conta",{}).get("id") == conta["id"]:
        _resultado(res)


def _resultado(res):
    calc, valores, campos = res["calc"], res["valores"], res["campos"]
    ref_label, conta, emp = res["ref_label"], res["conta"], res["emp"]

    st.markdown("---")
    st.markdown('<div class="step-n">Passo 02 de 02</div><div class="step-h">Resultado da Conciliação</div>', unsafe_allow_html=True)

    k1,k2,k3 = st.columns(3)
    k1.markdown(f'<div class="r-kpi"><div class="r-kpi-lbl">Saldo Razão</div><div class="r-kpi-val">{fmt_br(calc["sR"])}</div><div class="r-kpi-sub">{ref_label}</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="r-kpi"><div class="r-kpi-lbl">Rel. Auxiliar</div><div class="r-kpi-val">{fmt_br(calc["tA"])}</div><div class="r-kpi-sub">Composição calculada</div></div>', unsafe_allow_html=True)
    diff_cor = "#27AE60" if calc["ok"] else "#E74C3C"
    k3.markdown(f'<div class="r-kpi"><div class="r-kpi-lbl">Diferença</div><div class="r-kpi-val" style="color:{diff_cor}">{fmt_br(abs(calc["diff"]))}</div><div class="r-kpi-sub">{"✓ Zerada" if calc["ok"] else "⚠ Divergência"}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div style="font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#A0AEC0;margin-bottom:8px;padding-bottom:8px;border-bottom:1px solid #E2E8F0">Composição do Saldo</div>', unsafe_allow_html=True)

    is_simple = len(campos) == 2
    table_rows = []
    if is_simple:
        table_rows.append({"Descrição":campos[0],"Valor (R$)":fmt_br(calc["tA"]),"D/C":"D"})
    else:
        for i,(campo,val) in enumerate(zip(campos[:-1],valores[:-1])):
            table_rows.append({"Descrição":campo,"Valor (R$)":fmt_br(val),"D/C":"D" if i%2==0 else "C"})
        table_rows.append({"Descrição":"Total Auxiliar","Valor (R$)":fmt_br(calc["tA"]),"D/C":""})
    table_rows.append({"Descrição":"Saldo Razão","Valor (R$)":fmt_br(calc["sR"]),"D/C":""})
    st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

    if calc["ok"]:
        st.markdown(f'<div class="diff-ok">✓ Conciliação Zerada — Diferença: {fmt_br(abs(calc["diff"]))} &nbsp;<strong>[APROVADA]</strong></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="diff-nok">⚠ Conciliação com Divergência — Diferença: {fmt_br(abs(calc["diff"]))} &nbsp;<strong>[REVISAR]</strong></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="note-box"><strong>⚠ Atenção:</strong> Divergência de <strong>{fmt_br(abs(calc["diff"]))}</strong>. Verifique os lançamentos do período.</div>', unsafe_allow_html=True)

    col_novo, col_xls, _ = st.columns([2,2,5])
    with col_novo:
        if st.button("← Novo período", key="btn_novo"):
            st.session_state.resultado = None
            st.rerun()
    with col_xls:
        xls = gerar_excel(conta, emp, valores, ref_label, calc)
        st.download_button("⬇ Baixar Excel", data=xls,
                           file_name=f"conc_{conta['id']}_{ref_label.replace('/','_')}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           key="btn_xls")


# ── ROUTER ─────────────────────────────────────────────────────────────────────
page = st.session_state.page
if page == "empresa":
    page_empresa()
elif page == "dashboard":
    page_dashboard()
elif page == "modulo":
    page_modulo()
