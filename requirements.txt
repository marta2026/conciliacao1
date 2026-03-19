/* ── Hide Streamlit default elements ── */
#MainMenu, footer, header {visibility: hidden;}
.stDeployButton {display: none;}
[data-testid="stToolbar"] {display: none;}

/* ── Root variables ── */
:root {
  --hdr: #1C3557;
  --acc: #2196C4;
  --acc2: #6EC6E6;
  --sb: #F5F6F7;
  --sb-bdr: #E0E4E8;
  --sb-act: #E3F4FA;
  --sb-hov: #ECEEF0;
  --tx: #2D3748;
  --tx2: #718096;
  --tx3: #A0AEC0;
  --bdr: #E2E8F0;
  --bg: #F7FAFC;
  --card: #FFFFFF;
  --ok: #27AE60;
  --ok-bg: #E8F8EF;
  --warn: #E67E22;
  --warn-bg: #FEF3E7;
  --err: #E74C3C;
  --err-bg: #FDEDEC;
  --r: 5px;
}

/* ── Body ── */
body, .stApp {
  background: var(--bg) !important;
  font-family: 'Inter', sans-serif;
  color: var(--tx);
  font-size: 13px;
}

/* ── Remove default padding ── */
.block-container {
  padding-top: 0 !important;
  padding-bottom: 0 !important;
  max-width: 100% !important;
}

/* ── Topbar ── */
.topbar {
  background: var(--hdr);
  padding: 12px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 8px rgba(0,0,0,.18);
  margin-bottom: 0;
}
.topbar-title {
  color: rgba(255,255,255,.85);
  font-size: 13px;
  font-weight: 700;
  letter-spacing: .06em;
  text-transform: uppercase;
}
.topbar-name {
  color: #fff;
  font-size: 15px;
  font-weight: 700;
}

/* ── KPI Cards ── */
.kpi-card {
  background: var(--card);
  border: 1px solid var(--bdr);
  border-radius: var(--r);
  padding: 14px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,.04);
}
.kpi-ico {
  width: 42px;
  height: 42px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}
.kpi-lbl {
  font-size: 10px;
  font-weight: 700;
  color: var(--tx3);
  text-transform: uppercase;
  letter-spacing: .04em;
  margin-bottom: 2px;
}
.kpi-val {
  font-size: 26px;
  font-weight: 700;
  line-height: 1;
}
.kpi-sub {
  font-size: 10px;
  color: var(--tx3);
  margin-top: 2px;
}

/* ── Conta Card ── */
.cc {
  background: var(--card);
  border: 1px solid var(--bdr);
  border-radius: var(--r);
  padding: 14px;
  cursor: pointer;
  transition: all .18s;
  box-shadow: 0 1px 3px rgba(0,0,0,.04);
  position: relative;
  overflow: hidden;
  height: 100%;
}
.cc::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
}
.cc.ativo::before { background: linear-gradient(90deg, #1D4ED8, #60A5FA); }
.cc.passivo::before { background: linear-gradient(90deg, #9D174D, #EC4899); }
.cc:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,.10); }

/* ── Status Pills ── */
.pill {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  border-radius: 3px;
  font-size: 10px;
  font-weight: 700;
}
.pill-ok { background: var(--ok-bg); color: var(--ok); }
.pill-pend { background: var(--warn-bg); color: var(--warn); }
.pill-wip { background: #F0F1F3; color: #9BA5B0; }

/* ── Badge ── */
.badge-ativo { background: #DBEAFE; color: #1E40AF; padding: 2px 6px; border-radius: 3px; font-size: 9px; font-weight: 700; }
.badge-passivo { background: #FCE7F3; color: #9D174D; padding: 2px 6px; border-radius: 3px; font-size: 9px; font-weight: 700; }

/* ── Result boxes ── */
.diff-box-ok {
  background: var(--ok-bg);
  border: 1px solid #A7F3D0;
  border-radius: var(--r);
  padding: 16px 20px;
  color: var(--ok);
  font-weight: 700;
  font-size: 15px;
}
.diff-box-nok {
  background: var(--err-bg);
  border: 1px solid #FECACA;
  border-radius: var(--r);
  padding: 16px 20px;
  color: var(--err);
  font-weight: 700;
  font-size: 15px;
}
.note-box {
  background: #FFF8E1;
  border: 1px solid #FFE082;
  border-left: 4px solid #F59E0B;
  border-radius: 4px;
  padding: 10px 14px;
  font-size: 12px;
  color: #78350F;
  line-height: 1.7;
}

/* ── Banner ── */
.banner {
  background: #EBF8FF;
  border-left: 4px solid #2196C4;
  border-radius: 4px;
  padding: 12px 16px;
  font-size: 12px;
  color: #1A6980;
  line-height: 1.6;
  margin-bottom: 16px;
}

/* ── Sidebar custom ── */
[data-testid="stSidebar"] {
  background: #fff !important;
  border-right: 1px solid var(--bdr) !important;
}
[data-testid="stSidebar"] .stSelectbox label {
  font-size: 10px !important;
  font-weight: 700 !important;
  text-transform: uppercase;
  letter-spacing: .06em;
  color: var(--tx3) !important;
}

/* ── Streamlit overrides ── */
.stButton > button {
  border-radius: 4px !important;
  font-weight: 700 !important;
  font-size: 13px !important;
  letter-spacing: .02em;
  transition: all .15s;
}
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div {
  border-radius: 4px !important;
  font-size: 13px !important;
  border: 1.5px solid var(--bdr) !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
  border-color: var(--acc) !important;
  box-shadow: 0 0 0 3px rgba(33,150,196,.1) !important;
}

/* ── Dataframe ── */
.stDataFrame {
  border: 1px solid var(--bdr) !important;
  border-radius: var(--r) !important;
}

/* ── Upload area ── */
[data-testid="stFileUploader"] {
  border: 2px dashed #CBD5E1;
  border-radius: var(--r);
  padding: 8px;
  background: var(--bg);
  transition: all .18s;
}
[data-testid="stFileUploader"]:hover {
  border-color: var(--acc);
  background: #EBF8FF;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
  background: transparent;
  border-bottom: 1px solid var(--bdr);
}
.stTabs [data-baseweb="tab"] {
  font-size: 12px !important;
  font-weight: 600 !important;
  color: var(--tx2) !important;
}
.stTabs [aria-selected="true"] {
  color: var(--acc) !important;
  border-bottom-color: var(--acc) !important;
}

/* ── Section title ── */
.sec-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--tx);
  letter-spacing: -.02em;
  margin-bottom: 4px;
}
.sec-sub {
  font-size: 12px;
  color: var(--tx2);
  margin-bottom: 20px;
}

/* ── Step card ── */
.step-card {
  background: var(--card);
  border: 1px solid var(--bdr);
  border-radius: var(--r);
  padding: 22px;
  margin-bottom: 14px;
  box-shadow: 0 1px 3px rgba(0,0,0,.04);
}
.step-n {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: .08em;
  text-transform: uppercase;
  color: var(--tx3);
  margin-bottom: 4px;
}
.step-h {
  font-size: 15px;
  font-weight: 700;
  color: var(--tx);
  margin-bottom: 4px;
}

/* ── R-KPI ── */
.r-kpi {
  background: var(--bg);
  border: 1px solid var(--bdr);
  border-radius: 4px;
  padding: 12px 14px;
}
.r-kpi-lbl {
  font-size: 10px;
  font-weight: 700;
  color: var(--tx3);
  text-transform: uppercase;
  letter-spacing: .04em;
  margin-bottom: 3px;
}
.r-kpi-val {
  font-family: 'JetBrains Mono', monospace;
  font-size: 18px;
  font-weight: 700;
}
.r-kpi-sub {
  font-size: 10px;
  color: var(--tx3);
  margin-top: 2px;
}

/* ── Hist row ── */
.hist-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 10px;
  border-radius: 4px;
  background: var(--bg);
  margin-bottom: 6px;
  font-size: 12px;
}

/* ── Empty state ── */
.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--tx2);
}
.empty-state .ico { font-size: 36px; margin-bottom: 10px; }
.empty-state .ttl { font-size: 14px; font-weight: 700; color: var(--tx); }
.empty-state .sub { font-size: 12px; margin-top: 4px; }

/* ── Empresa cards ── */
.emp-card {
  background: var(--card);
  border: 1.5px solid var(--bdr);
  border-radius: 12px;
  padding: 36px 32px;
  text-align: center;
  transition: all .2s;
  box-shadow: 0 2px 8px rgba(0,0,0,.06);
  cursor: pointer;
}
.emp-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0,0,0,.10);
}

/* ── Mono font ── */
.mono { font-family: 'JetBrains Mono', 'Courier New', monospace; }
