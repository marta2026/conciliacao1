import streamlit as st
import io
import hashlib
import datetime
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="Conciliação Contábil",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# USUÁRIOS  —  perfil: "admin" | "nc" | "mf"
# Para trocar senha: hashlib.sha256("nova_senha".encode()).hexdigest()
# ══════════════════════════════════════════════════════════════════════════════
USUARIOS = {
    "admin": {
        "nome": "Administrador",
        "senha_hash": hashlib.sha256("admin123".encode()).hexdigest(),
        "perfil": "admin",
    },
    "nutricash": {
        "nome": "Analista Nutricash",
        "senha_hash": hashlib.sha256("nc2024".encode()).hexdigest(),
        "perfil": "nc",
    },
    "maxifrota": {
        "nome": "Analista MaxiFrota",
        "senha_hash": hashlib.sha256("mf2024".encode()).hexdigest(),
        "perfil": "mf",
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

#MainMenu, footer, header {visibility: hidden;}
.stDeployButton {display:none;}
[data-testid="stToolbar"] {display:none;}

body, .stApp {
  background: #F7FAFC !important;
  font-family: 'Inter', sans-serif;
  font-size: 13px;
  color: #2D3748;
}
.block-container {
  padding-top: 0 !important;
  padding-bottom: 0 !important;
  max-width: 100% !important;
}

/* ── TOPBAR ── */
.topbar {
  padding: 0 24px; height: 54px;
  display: flex; align-items: center; justify-content: space-between;
  box-shadow: 0 2px 8px rgba(0,0,0,.18);
}
.topbar-l { display: flex; align-items: center; gap: 12px; }
.topbar-title { color: rgba(255,255,255,.8); font-size: 11px; font-weight: 700; letter-spacing:.08em; text-transform:uppercase; }
.topbar-sep   { color: rgba(255,255,255,.3); font-size: 18px; }
.topbar-name  { color:#fff; font-size: 14px; font-weight: 700; }
.topbar-user  {
  display:flex; align-items:center; gap:6px;
  background:rgba(255,255,255,.12); border:1px solid rgba(255,255,255,.2);
  border-radius:20px; padding:4px 12px;
  color:rgba(255,255,255,.9); font-size:11px; font-weight:600;
}

/* ── KPI ── */
.kpi-card {
  background:#fff; border:1px solid #E2E8F0; border-radius:6px;
  padding:14px 16px; display:flex; align-items:center; gap:12px;
  box-shadow:0 1px 3px rgba(0,0,0,.04);
}
.kpi-ico  { width:42px; height:42px; border-radius:8px; display:flex; align-items:center; justify-content:center; font-size:20px; }
.kpi-lbl  { font-size:10px; font-weight:700; color:#A0AEC0; text-transform:uppercase; letter-spacing:.04em; margin-bottom:2px; }
.kpi-val  { font-size:26px; font-weight:700; line-height:1; }
.kpi-sub  { font-size:10px; color:#A0AEC0; margin-top:2px; }

/* ── CONTA CARD ── */
.cc {
  background:#fff; border:1px solid #E2E8F0; border-radius:6px;
  padding:14px; box-shadow:0 1px 3px rgba(0,0,0,.04);
  position:relative; overflow:hidden;
}
.cc::before { content:''; position:absolute; top:0; left:0; right:0; height:3px; }
.cc.ativo::before   { background: linear-gradient(90deg,#1D4ED8,#60A5FA); }
.cc.passivo::before { background: linear-gradient(90deg,#9D174D,#EC4899); }

/* ── PILLS / BADGES ── */
.pill     { display:inline-flex; align-items:center; gap:4px; padding:3px 8px; border-radius:3px; font-size:10px; font-weight:700; }
.pill-ok  { background:#E8F8EF; color:#27AE60; }
.pill-pend{ background:#FEF3E7; color:#E67E22; }
.pill-wip { background:#F0F1F3; color:#9BA5B0; }
.pdot     { width:5px; height:5px; border-radius:50%; background:currentColor; }

.badge-ativo   { background:#DBEAFE; color:#1E40AF; padding:2px 6px; border-radius:3px; font-size:9px; font-weight:700; }
.badge-passivo { background:#FCE7F3; color:#9D174D; padding:2px 6px; border-radius:3px; font-size:9px; font-weight:700; }

/* ── SIDEBAR STATUS DOTS ── */
.sb-conta {
  display:flex; align-items:center; justify-content:space-between;
  padding:5px 8px; border-radius:4px; font-size:11px; color:#718096;
  margin-bottom:2px;
}
.dot-ok   { width:7px; height:7px; border-radius:50%; background:#27AE60; flex-shrink:0; }
.dot-pend { width:7px; height:7px; border-radius:50%; background:#E67E22; flex-shrink:0; }

/* ── RESULTADO ── */
.diff-ok  { background:#E8F8EF; border:1px solid #A7F3D0; border-radius:6px; padding:16px 20px; color:#27AE60; font-weight:700; font-size:14px; display:flex; justify-content:space-between; align-items:center; }
.diff-nok { background:#FDEDEC; border:1px solid #FECACA; border-radius:6px; padding:16px 20px; color:#E74C3C; font-weight:700; font-size:14px; display:flex; justify-content:space-between; align-items:center; }
.diff-bdg { font-size:10px; font-weight:700; padding:4px 12px; border-radius:3px; color:#fff; letter-spacing:.04em; }
.bdg-ok   { background:#27AE60; }
.bdg-nok  { background:#E74C3C; }

.note-box { background:#FFF8E1; border:1px solid #FFE082; border-left:4px solid #F59E0B; border-radius:4px; padding:10px 14px; font-size:12px; color:#78350F; line-height:1.7; margin-top:10px; }
.banner   { background:#EBF8FF; border-left:4px solid #2196C4; border-radius:4px; padding:12px 16px; font-size:12px; color:#1A6980; line-height:1.6; margin-bottom:16px; }

/* ── R-KPI ── */
.r-kpi     { background:#F7FAFC; border:1px solid #E2E8F0; border-radius:4px; padding:12px 14px; }
.r-kpi-lbl { font-size:10px; font-weight:700; color:#A0AEC0; text-transform:uppercase; letter-spacing:.04em; margin-bottom:3px; }
.r-kpi-val { font-family:monospace; font-size:18px; font-weight:700; }
.r-kpi-sub { font-size:10px; color:#A0AEC0; margin-top:2px; }

/* ── MISC ── */
.hist-row  { display:flex; align-items:center; justify-content:space-between; padding:8px 10px; border-radius:4px; background:#F7FAFC; margin-bottom:6px; font-size:12px; }
.sec-title { font-size:18px; font-weight:700; color:#2D3748; letter-spacing:-.02em; margin-bottom:4px; }
.sec-sub   { font-size:12px; color:#718096; margin-bottom:18px; }
.step-n    { font-size:10px; font-weight:700; letter-spacing:.08em; text-transform:uppercase; color:#A0AEC0; margin-bottom:4px; }
.step-h    { font-size:15px; font-weight:700; color:#2D3748; margin-bottom:6px; }
.empty-state { text-align:center; padding:40px 20px; color:#718096; }

[data-testid="stSidebar"] { background:#fff !important; border-right:1px solid #E2E8F0 !important; }
.stButton > button { border-radius:4px !important; font-weight:700 !important; font-size:12px !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════════════════════
EMPRESAS = {
    "nc": {"id":"nc","nome":"Nutricash","razao":"NUTRICASH LTDA","hdr":"#1C3557","acc":"#2196C4"},
    "mf": {"id":"mf","nome":"MaxiFrota","razao":"MAXIFROTA LTDA","hdr":"#003D78","acc":"#F5A800"},
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

MESES = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
         "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]

# ══════════════════════════════════════════════════════════════════════════════
# STATE
# ══════════════════════════════════════════════════════════════════════════════
for k, v in [
    ("page","login"), ("logado",False), ("usuario_atual",None),
    ("empresa",None), ("conta",None), ("tab","dashboard"),
    ("historico",[]), ("status",{}), ("resultado",None), ("login_erro",False),
]:
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
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
    tA = valores[0] if len(campos)==2 else sum(
        v if i%2==0 else -v for i,v in enumerate(valores[:-1]))
    diff = sR - tA
    return {"sR":sR, "tA":tA, "diff":diff, "ok":abs(diff)<0.01}

def get_status(emp_id, conta_id):
    return st.session_state.status.get(f"{emp_id}_{conta_id}", "pendente")

def set_status(emp_id, conta_id, val):
    st.session_state.status[f"{emp_id}_{conta_id}"] = val

def add_historico(item):
    h = [x for x in st.session_state.historico
         if not (x["emp"]==item["emp"] and x["id"]==item["id"] and x["ref"]==item["ref"])]
    h.append(item)
    st.session_state.historico = h

def get_contas(emp_id):
    return [c for c in CONTAS if emp_id in c["empresas"]]

def perfil_ok(emp_id):
    u = USUARIOS.get(st.session_state.usuario_atual or "", {})
    p = u.get("perfil","")
    return p == "admin" or p == emp_id

def usuario_info():
    return USUARIOS.get(st.session_state.usuario_atual or "", {})

def auto_fill(rows, campos):
    flat = []
    for row in rows:
        if not row: continue
        row = list(row)
        for ci in range(len(row)):
            cell = row[ci]
            if isinstance(cell, str) and cell.strip():
                for j in range(ci+1, len(row)):
                    if isinstance(row[j], (int,float)):
                        flat.append({"lbl":cell.strip().lower(),"val":abs(float(row[j]))})
                        break
    def find(kws):
        for kw in kws:
            hit = next((f["val"] for f in flat if kw in f["lbl"]), None)
            if hit is not None: return hit
        return None
    kw_r = ["saldo razão","saldo razao","razão ","razao "]
    kw_a = ["saldo relat","posição","posicao","saldo auxiliar","saldo da conta","saldo em conta"]
    kw_i = ["saldo inicial","saldo anterior"]
    kw_e = ["adiantamento","retenção","retencao","apurado","emissão","emissao","transaç","nf recebid"]
    kw_s = ["baixa","recolhimento","compensaç","resgate","repasse","pagamento realiz"]
    result = {}
    if len(campos)==2:
        v = find(kw_a) or find(kw_i)
        if v is not None: result[campos[0]] = v
        v = find(kw_r)
        if v is not None: result[campos[1]] = v
    else:
        vals = {"ini":find(kw_i),"entr":find(kw_e),"saida":find(kw_s),"razao":find(kw_r),"aux":find(kw_a)}
        for i, campo in enumerate(campos):
            n = campo.lower(); v = None
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
        if ext=="xlsx": df = pd.read_excel(buf, header=None, engine="openpyxl")
        elif ext=="xls":
            try: df = pd.read_excel(buf, header=None, engine="xlrd")
            except: df = pd.read_excel(buf, header=None)
        elif ext in ("csv","txt"):
            try: df = pd.read_csv(buf, header=None, sep=None, engine="python")
            except: df = pd.read_csv(io.BytesIO(file_bytes), header=None, sep=";")
        elif ext=="json":
            import json; df = pd.DataFrame(json.loads(file_bytes))
        else: df = pd.read_excel(buf, header=None, engine="openpyxl")
        return df.values.tolist()
    except: return []

def gerar_excel(conta, emp, valores, ref_label, calc):
    campos = conta["campos"]
    rows = [
        [f"CONCILIAÇÃO — {conta['nome'].upper()}","",""],
        [f"{emp['razao']}  |  Conta: {conta['codigo']}  |  Ref.: {ref_label}","",""],
        ["","",""],["Descrição","Valor (R$)","D/C"],
    ]
    for i,(c,v) in enumerate(zip(campos[:-1],valores[:-1])):
        rows.append([c, v, "D" if i%2==0 else "C"])
    rows += [["Total Auxiliar",calc["tA"],""],["Saldo Razão",calc["sR"],""],
             ["DIFERENÇA",calc["diff"],"ZERADA" if calc["ok"] else "REVISAR"],
             ["","",""],
             [f"Emitido em: {datetime.date.today().strftime('%d/%m/%Y')}","",""]]
    buf = io.BytesIO()
    pd.DataFrame(rows).to_excel(buf, index=False, header=False, engine="openpyxl")
    return buf.getvalue()

def _topbar(bg, titulo, usuario_nome, empresa_nome=None):
    emp_part = f'<span class="topbar-sep">|</span><span class="topbar-name">{empresa_nome}</span>' if empresa_nome else ""
    st.markdown(f"""
    <div class="topbar" style="background:{bg}">
      <div class="topbar-l">
        <span style="font-size:20px">📊</span>
        <span class="topbar-title">{titulo}</span>
        {emp_part}
      </div>
      <div class="topbar-user">👤 {usuario_nome}</div>
    </div>
    """, unsafe_allow_html=True)

def _logout():
    for k in ["logado","usuario_atual","empresa","conta","tab",
              "historico","status","resultado","login_erro"]:
        st.session_state.pop(k, None)
    st.session_state.page = "login"
    st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: LOGIN
# ══════════════════════════════════════════════════════════════════════════════
def page_login():
    # Fundo colorido via div full-width
    st.markdown("""
    <div style="position:fixed;inset:0;
         background:linear-gradient(135deg,#1C3557 0%,#2c6694 55%,#2196C4 100%);
         z-index:-1"></div>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.1, 1])

    with col:
        # Card container
        st.markdown("""
        <div style="background:#fff;border-radius:16px;padding:44px 40px 36px;
             box-shadow:0 24px 64px rgba(0,0,0,.30);">
          <div style="text-align:center;margin-bottom:28px">
            <div style="font-size:52px;margin-bottom:8px">📊</div>
            <div style="font-size:21px;font-weight:700;color:#1C3557">Conciliação Contábil</div>
            <div style="font-size:12px;color:#718096;margin-top:4px">Acesso restrito — faça login para continuar</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.login_erro:
            st.markdown('<div style="background:#FDEDEC;border:1px solid #FECACA;border-left:4px solid #E74C3C;border-radius:4px;padding:10px 14px;font-size:12px;color:#C0392B;margin-bottom:8px">❌ Usuário ou senha incorretos. Tente novamente.</div>', unsafe_allow_html=True)

        with st.form("form_login"):
            usuario = st.text_input("Usuário", placeholder="Digite seu usuário")
            senha   = st.text_input("Senha",   placeholder="Digite sua senha", type="password")
            st.markdown("<br>", unsafe_allow_html=True)
            entrar  = st.form_submit_button("🔐  ENTRAR", use_container_width=True, type="primary")

        if entrar:
            u = USUARIOS.get(usuario.strip().lower())
            if u and u["senha_hash"] == hashlib.sha256(senha.encode()).hexdigest():
                st.session_state.logado        = True
                st.session_state.usuario_atual = usuario.strip().lower()
                st.session_state.login_erro    = False
                perfil = u["perfil"]
                if perfil == "admin":
                    st.session_state.page = "empresa"
                else:
                    st.session_state.empresa = perfil
                    st.session_state.page    = "dashboard"
                st.rerun()
            else:
                st.session_state.login_erro = True
                st.rerun()

        st.markdown("""
        <div style="background:#F0F9FF;border:1px solid #BAE6FD;border-radius:6px;
             padding:12px 14px;font-size:11px;color:#0369A1;margin-top:16px;line-height:2.1">
          <strong>Credenciais de demonstração:</strong><br>
          👤 <code>admin</code> &nbsp;·&nbsp; 🔒 <code>admin123</code> &nbsp;— Acesso total (ambas empresas)<br>
          👤 <code>nutricash</code> &nbsp;·&nbsp; 🔒 <code>nc2024</code> &nbsp;— Somente Nutricash<br>
          👤 <code>maxifrota</code> &nbsp;·&nbsp; 🔒 <code>mf2024</code> &nbsp;— Somente MaxiFrota
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: EMPRESA
# ══════════════════════════════════════════════════════════════════════════════
def page_empresa():
    u = usuario_info()
    _topbar("#1C3557", "Conciliação Contábil", u.get("nome",""))

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div style="text-align:center;font-size:22px;font-weight:700;color:#2D3748">Selecione a empresa</div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center;font-size:13px;color:#718096;margin-bottom:36px">Escolha a empresa para acessar o módulo de conciliação</div>', unsafe_allow_html=True)

    _, col_nc, col_mf, _ = st.columns([1,2,2,1])

    with col_nc:
        disabled = not perfil_ok("nc")
        opacity = "0.4" if disabled else "1"
        border  = "#CBD5E1" if disabled else "#2196C4"
        st.markdown(f"""
        <div style="background:#fff;border:1.5px solid {border};border-radius:12px;
             padding:36px 28px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,.06);opacity:{opacity}">
          <div style="font-size:46px;margin-bottom:12px">🏢</div>
          <div style="font-size:17px;font-weight:700;color:#2D3748;margin-bottom:6px">Nutricash</div>
          <div style="font-size:12px;color:#718096;line-height:1.5">
            Benefícios, alimentação e gestão de pagamentos corporativos
          </div>
        </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if not disabled:
            if st.button("ACESSAR → Nutricash", use_container_width=True, type="primary", key="btn_nc"):
                st.session_state.empresa = "nc"
                st.session_state.page    = "dashboard"
                st.rerun()
        else:
            st.button("⛔ Sem permissão", use_container_width=True, disabled=True, key="btn_nc_d")

    with col_mf:
        disabled = not perfil_ok("mf")
        opacity = "0.4" if disabled else "1"
        border  = "#CBD5E1" if disabled else "#F5A800"
        st.markdown(f"""
        <div style="background:#fff;border:1.5px solid {border};border-radius:12px;
             padding:36px 28px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,.06);opacity:{opacity}">
          <div style="font-size:46px;margin-bottom:12px">🚛</div>
          <div style="font-size:17px;font-weight:700;color:#2D3748;margin-bottom:6px">MaxiFrota</div>
          <div style="font-size:12px;color:#718096;line-height:1.5">
            Gestão de frotas, abastecimento e mobilidade corporativa
          </div>
        </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if not disabled:
            if st.button("ACESSAR → MaxiFrota", use_container_width=True, key="btn_mf"):
                st.session_state.empresa = "mf"
                st.session_state.page    = "dashboard"
                st.rerun()
        else:
            st.button("⛔ Sem permissão", use_container_width=True, disabled=True, key="btn_mf_d")

    st.markdown("<br><br>", unsafe_allow_html=True)
    _, mc, _ = st.columns([3,2,3])
    with mc:
        if st.button("🚪 Sair do sistema", use_container_width=True):
            _logout()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def page_dashboard():
    emp_id = st.session_state.empresa
    emp    = EMPRESAS[emp_id]
    contas = get_contas(emp_id)
    u      = usuario_info()

    _topbar(emp["hdr"], "Conciliação Contábil", u.get("nome",""), emp["nome"])

    with st.sidebar:
        st.markdown(f"<div style='font-size:11px;font-weight:700;color:#A0AEC0;text-transform:uppercase;letter-spacing:.06em'>Empresa</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:13px;font-weight:700;color:#2D3748;margin-bottom:10px'>{emp['razao']}</div>", unsafe_allow_html=True)

        tabs = ["📊 Painel", "🕐 Histórico"]
        nav  = st.radio("nav", tabs, label_visibility="collapsed",
                        index=0 if st.session_state.tab=="dashboard" else 1)
        st.session_state.tab = "dashboard" if "Painel" in nav else "historico"

        st.markdown("---")
        _sidebar_contas(contas, emp_id, "ativo",   "ATIVO")
        _sidebar_contas(contas, emp_id, "passivo", "PASSIVO")
        st.markdown("---")

        if usuario_info().get("perfil") == "admin":
            if st.button("↩ Trocar Empresa", use_container_width=True):
                st.session_state.page    = "empresa"
                st.session_state.empresa = None
                st.rerun()

        if st.button("🚪 Sair", use_container_width=True):
            _logout()

    if st.session_state.tab == "dashboard":
        _dash(emp, contas, emp_id)
    else:
        _historico(emp, emp_id)


def _sidebar_contas(contas, emp_id, tipo, titulo):
    grupo = [c for c in contas if c["tipo"]==tipo]
    if not grupo: return
    st.markdown(f"<div style='font-size:9px;font-weight:700;color:#A0AEC0;letter-spacing:.08em;text-transform:uppercase;margin:8px 0 4px'>{titulo}</div>", unsafe_allow_html=True)
    for c in grupo:
        nome_curto = c["nome"][:22]+("…" if len(c["nome"])>22 else "")
        if c["wip"]:
            st.markdown(f'<div class="sb-conta" style="opacity:.45">{c["icon"]} {nome_curto}<span style="font-size:9px;color:#CBD5E1">EM BREVE</span></div>', unsafe_allow_html=True)
            continue
        status = get_status(emp_id, c["id"])
        dot = '<span class="dot-ok"></span>' if status=="ok" else '<span class="dot-pend"></span>'
        st.markdown(f'<div class="sb-conta">{c["icon"]} {nome_curto} {dot}</div>', unsafe_allow_html=True)
        if st.button("→", key=f"sb_{c['id']}", help=c["nome"]):
            st.session_state.conta     = c
            st.session_state.page      = "modulo"
            st.session_state.resultado = None
            st.rerun()


def _dash(emp, contas, emp_id):
    contas_ativas = [c for c in contas if not c["wip"]]
    ok_n   = sum(1 for c in contas_ativas if get_status(emp_id,c["id"])=="ok")
    pend_n = sum(1 for c in contas_ativas if get_status(emp_id,c["id"])=="pendente")
    wip_n  = sum(1 for c in contas if c["wip"])
    hist   = [h for h in st.session_state.historico if h["emp"]==emp_id]

    st.markdown(f'<div class="sec-title" style="margin-top:16px">Painel — {emp["nome"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sec-sub">{emp["razao"]} · {len(contas)} contas · {ok_n} conciliadas · {pend_n} pendentes</div>', unsafe_allow_html=True)
    st.markdown('<div class="banner">📌 Selecione uma conta no menu lateral ou nos cards abaixo para iniciar a conciliação.</div>', unsafe_allow_html=True)

    k1,k2,k3,k4 = st.columns(4)
    for col,ico,bg,cor,lbl,val,sub in [
        (k1,"✅","#E8F8EF","#27AE60","Contas OK",ok_n,"Conciliadas"),
        (k2,"⏳","#FEF3E7","#E67E22","Pendentes",pend_n,"Aguardando"),
        (k3,"📁","#EBF5FB",emp["acc"],"Total",len(contas),f"{wip_n} em construção"),
        (k4,"🕐","#F5F6F7","#718096","Histórico",len(hist),"Registros"),
    ]:
        col.markdown(f'<div class="kpi-card"><div class="kpi-ico" style="background:{bg}">{ico}</div><div><div class="kpi-lbl">{lbl}</div><div class="kpi-val" style="color:{cor}">{val}</div><div class="kpi-sub">{sub}</div></div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    cl, cr = st.columns(2)

    with cl:
        st.markdown("**📊 Status das Contas**")
        fig = go.Figure(data=[go.Pie(
            labels=["OK","Pendente","Em construção"],
            values=[max(ok_n,0), max(pend_n,0), max(wip_n,0)],
            hole=0.55, marker_colors=["#27AE60","#E67E22","#CBD5E1"],
            textinfo="label+value", textfont_size=11,
        )])
        fig.update_layout(margin=dict(t=10,b=10,l=0,r=0), height=210,
                          showlegend=False, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    with cr:
        st.markdown("**🕐 Últimas Conciliações**")
        rec = hist[-5:][::-1]
        if rec:
            for h in rec:
                pill = "pill-ok" if h["ok"] else "pill-pend"
                txt  = "✓ OK" if h["ok"] else "⚠ DIVERG."
                st.markdown(f'<div class="hist-row"><div><span>{h["ico"]}</span><strong style="margin-left:6px">{h["conta"]}</strong><div style="font-size:10px;color:#A0AEC0;font-family:monospace">{h["ref"]}</div></div><span class="pill {pill}">{txt}</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="empty-state"><div style="font-size:32px">📭</div><div>Nenhuma conciliação realizada</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**📋 Todas as Contas**")
    for tipo in ["ativo","passivo"]:
        grupo = [c for c in contas if c["tipo"]==tipo]
        if not grupo: continue
        st.markdown(f'<div style="font-size:9px;font-weight:700;color:#A0AEC0;text-transform:uppercase;letter-spacing:.08em;margin:14px 0 8px;border-bottom:1px solid #E2E8F0;padding-bottom:4px">{tipo.upper()}</div>', unsafe_allow_html=True)
        cols = st.columns(4)
        for i,c in enumerate(grupo):
            with cols[i%4]:
                status = get_status(emp_id,c["id"]) if not c["wip"] else "wip"
                pill_c = "pill-ok" if status=="ok" else ("pill-wip" if status=="wip" else "pill-pend")
                pill_t = "✓ OK" if status=="ok" else ("EM BREVE" if status=="wip" else "PENDENTE")
                badge  = "badge-ativo" if tipo=="ativo" else "badge-passivo"
                st.markdown(f'<div class="cc {tipo}" style="{"opacity:.5" if c["wip"] else ""}"><div style="display:flex;justify-content:space-between;margin-bottom:8px"><span style="font-size:20px">{c["icon"]}</span><span class="pill {pill_c}"><span class="pdot"></span>{pill_t}</span></div><div style="font-size:12px;font-weight:700;color:#2D3748;margin-bottom:3px">{c["nome"]}</div><div style="font-family:monospace;font-size:10px;color:#A0AEC0">{c["codigo"]}</div><div style="margin-top:6px"><span class="{badge}">{tipo.upper()}</span></div></div>', unsafe_allow_html=True)
                if not c["wip"]:
                    if st.button("Abrir conta", key=f"cc_{c['id']}", use_container_width=True):
                        st.session_state.conta     = c
                        st.session_state.page      = "modulo"
                        st.session_state.resultado = None
                        st.rerun()


def _historico(emp, emp_id):
    st.markdown(f'<div class="sec-title" style="margin-top:16px">Histórico de Conciliações</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sec-sub">{emp["razao"]}</div>', unsafe_allow_html=True)

    hist = [h for h in st.session_state.historico if h["emp"]==emp_id]
    if not hist:
        st.markdown('<div class="empty-state"><div style="font-size:32px">📭</div><div style="font-weight:700;margin-top:8px">Nenhum histórico</div><div>As conciliações processadas aparecerão aqui</div></div>', unsafe_allow_html=True)
        return

    refs = sorted(set(h["ref"] for h in hist), reverse=True)
    fc, sc, _ = st.columns([2,2,4])
    filtro_ref    = fc.selectbox("Período", ["Todos"]+refs, key="h_ref")
    filtro_status = sc.selectbox("Status",  ["Todos","✅ OK","⚠ Divergência"], key="h_st")

    filtrado = hist[::-1]
    if filtro_ref != "Todos":
        filtrado = [h for h in filtrado if h["ref"]==filtro_ref]
    if filtro_status == "✅ OK":
        filtrado = [h for h in filtrado if h["ok"]]
    elif filtro_status == "⚠ Divergência":
        filtrado = [h for h in filtrado if not h["ok"]]

    if not filtrado:
        st.info("Nenhum registro com os filtros selecionados.")
        return

    df = pd.DataFrame([{
        "Conta":        f"{h['ico']} {h['conta']}",
        "Código":       h["codigo"],
        "Período":      h["ref"],
        "Diferença R$": fmt_br(h["diff"]),
        "Status":       "✅ OK" if h["ok"] else "⚠ DIVERGÊNCIA",
    } for h in filtrado])
    st.dataframe(df, use_container_width=True, hide_index=True)

    buf = io.BytesIO()
    df.to_excel(buf, index=False, engine="openpyxl")
    st.download_button("⬇ Exportar histórico (Excel)", data=buf.getvalue(),
                       file_name=f"historico_{emp_id}_{datetime.date.today()}.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       key="btn_hist_xls")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: MÓDULO
# ══════════════════════════════════════════════════════════════════════════════
def page_modulo():
    emp_id = st.session_state.empresa
    emp    = EMPRESAS[emp_id]
    conta  = st.session_state.conta
    if not conta:
        st.session_state.page = "dashboard"; st.rerun()
    u = usuario_info()

    st.markdown(f"""
    <div style="background:#fff;border-bottom:3px solid {emp['acc']};padding:0 24px;height:52px;
         display:flex;align-items:center;justify-content:space-between;
         box-shadow:0 1px 4px rgba(0,0,0,.06);">
      <div style="font-size:11px;color:#718096">
        <strong style="color:#2D3748">{emp['nome']}</strong> › {conta['tipo'].upper()} › {conta['nome']}
      </div>
      <div style="font-size:11px;color:#A0AEC0">👤 {u.get('nome','')}</div>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        if st.button("← Voltar ao Painel", use_container_width=True):
            st.session_state.page      = "dashboard"
            st.session_state.conta     = None
            st.session_state.resultado = None
            st.rerun()
        st.markdown("---")
        tipo_bg    = "#DBEAFE" if conta["tipo"]=="ativo" else "#FCE7F3"
        tipo_color = "#1E40AF" if conta["tipo"]=="ativo" else "#9D174D"
        st.markdown(f'<span style="background:{tipo_bg};color:{tipo_color};padding:2px 8px;border-radius:3px;font-size:10px;font-weight:700">{conta["tipo"].upper()}</span>', unsafe_allow_html=True)
        st.markdown(f"<br><strong>{conta['nome']}</strong>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-family:monospace;font-size:11px;color:#718096'>{conta['codigo']}</div>", unsafe_allow_html=True)
        st.markdown("---")
        if st.button("🚪 Sair", use_container_width=True):
            _logout()

    # Header
    st.markdown(f'<span style="background:{tipo_bg};color:{tipo_color};padding:3px 10px;border-radius:3px;font-size:10px;font-weight:700;margin-top:16px;display:inline-block">{conta["tipo"].upper()}</span>', unsafe_allow_html=True)
    st.markdown(f'<div class="sec-title" style="margin-top:6px">{conta["nome"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-family:monospace;font-size:11px;color:#718096;margin-bottom:20px">Conta: {conta["codigo"]} · {emp["razao"]}</div>', unsafe_allow_html=True)

    # Step 1
    st.markdown('<div class="step-n">Passo 01 de 02</div><div class="step-h">Período e Dados</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:12px;color:#718096;margin-bottom:16px">Selecione o mês/ano e preencha os valores. Opcionalmente, faça upload de planilha para auto-preenchimento.</div>', unsafe_allow_html=True)

    now = datetime.date.today()
    cm, ca, _ = st.columns([2,1,4])
    mes = cm.selectbox("Mês", [str(i).zfill(2) for i in range(1,13)],
                       format_func=lambda x: MESES[int(x)-1],
                       index=now.month-1, key="ref_mes")
    ano = ca.number_input("Ano", min_value=2020, max_value=2099,
                          value=now.year, step=1, key="ref_ano")
    ref_label = f"{MESES[int(mes)-1]}/{int(ano)}"

    st.markdown("**📂 Upload de planilha auxiliar (opcional)**")
    uploaded = st.file_uploader("XLSX / XLS / CSV / TXT / JSON",
                                type=["xlsx","xls","csv","txt","json"],
                                key=f"up_{conta['id']}",
                                label_visibility="collapsed")
    autofill_vals = {}
    if uploaded:
        rows = read_upload(uploaded.read(), uploaded.name)
        if rows:
            autofill_vals = auto_fill(rows, conta["campos"])
            if autofill_vals:
                st.success(f"✅ {len(autofill_vals)} campo(s) preenchido(s) de **{uploaded.name}**")
            else:
                st.info("ℹ️ Arquivo recebido — preencha os valores manualmente.")

    st.markdown("**Valores da Conciliação**")
    campos  = conta["campos"]
    valores = []
    idx = 0
    for _ in range((len(campos)+2)//3):
        rcols = st.columns(3)
        for ci in range(3):
            if idx >= len(campos): break
            campo   = campos[idx]
            default = fmt_br(autofill_vals[campo]) if campo in autofill_vals else ""
            with rcols[ci]:
                raw = st.text_input(campo, value=default, placeholder="0,00",
                                    key=f"f_{conta['id']}_{idx}")
                valores.append(parse_br(raw))
            idx += 1
    while len(valores) < len(campos):
        valores.append(0.0)

    all_filled = any(v != 0.0 for v in valores)
    cb, _ = st.columns([2,5])
    with cb:
        processar = st.button("⚡ Processar Conciliação", disabled=not all_filled,
                              type="primary", use_container_width=True, key="btn_proc")

    if processar and all_filled:
        calc = calcular(campos, valores)
        add_historico({"emp":emp_id,"id":conta["id"],"conta":conta["nome"],
                       "codigo":conta["codigo"],"ico":conta["icon"],
                       "ref":ref_label,"diff":abs(calc["diff"]),"ok":calc["ok"]})
        set_status(emp_id, conta["id"], "ok" if calc["ok"] else "pendente")
        st.session_state.resultado = {"calc":calc,"valores":valores,"campos":campos,
                                      "ref_label":ref_label,"conta":conta,"emp":emp}

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
    cor = "#27AE60" if calc["ok"] else "#E74C3C"
    k3.markdown(f'<div class="r-kpi"><div class="r-kpi-lbl">Diferença</div><div class="r-kpi-val" style="color:{cor}">{fmt_br(abs(calc["diff"]))}</div><div class="r-kpi-sub">{"✓ Zerada" if calc["ok"] else "⚠ Divergência"}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div style="font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#A0AEC0;margin-bottom:8px;padding-bottom:8px;border-bottom:1px solid #E2E8F0">Composição do Saldo — Relatório Auxiliar</div>', unsafe_allow_html=True)

    table_rows = []
    if len(campos)==2:
        table_rows.append({"Descrição":campos[0],"Valor (R$)":fmt_br(calc["tA"]),"D/C":"D"})
    else:
        for i,(c,v) in enumerate(zip(campos[:-1],valores[:-1])):
            table_rows.append({"Descrição":c,"Valor (R$)":fmt_br(v),"D/C":"D" if i%2==0 else "C"})
        table_rows.append({"Descrição":"Total Auxiliar","Valor (R$)":fmt_br(calc["tA"]),"D/C":""})
    table_rows.append({"Descrição":"Saldo Razão","Valor (R$)":fmt_br(calc["sR"]),"D/C":""})
    st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

    diff_cls = "diff-ok" if calc["ok"] else "diff-nok"
    diff_ico = "✓ Conciliação Zerada" if calc["ok"] else "⚠ Conciliação com Divergência"
    bdg_cls  = "bdg-ok" if calc["ok"] else "bdg-nok"
    bdg_txt  = "APROVADA" if calc["ok"] else "REVISAR"
    st.markdown(f'<div class="{diff_cls}"><span>{diff_ico} — Diferença: <strong>{fmt_br(abs(calc["diff"]))}</strong></span><span class="diff-bdg {bdg_cls}">{bdg_txt}</span></div>', unsafe_allow_html=True)

    if not calc["ok"]:
        st.markdown(f'<div class="note-box">⚠ <strong>Atenção:</strong> Divergência de <strong>{fmt_br(abs(calc["diff"]))}</strong>. Verifique os lançamentos do período {ref_label}.</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    cn, cx, _ = st.columns([2,2,5])
    with cn:
        if st.button("← Novo período", key="btn_novo"):
            st.session_state.resultado = None
            st.rerun()
    with cx:
        xls = gerar_excel(conta, emp, valores, ref_label, calc)
        st.download_button("⬇ Baixar Excel", data=xls,
                           file_name=f"conc_{conta['id']}_{ref_label.replace('/','_')}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           key="btn_xls")


# ══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.logado and st.session_state.page != "login":
    st.session_state.page = "login"

p = st.session_state.page
if p == "login":
    page_login()
elif p == "empresa":
    page_empresa()
elif p == "dashboard":
    if st.session_state.empresa and not perfil_ok(st.session_state.empresa):
        st.error("⛔ Sem permissão para esta empresa.")
        if st.button("Voltar"):
            st.session_state.page = "empresa"; st.rerun()
    else:
        page_dashboard()
elif p == "modulo":
    page_modulo()
