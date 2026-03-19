import streamlit as st
from utils.config import CFG


def render():
    # ── Header ──
    st.markdown(
        """
        <div class="topbar">
          <div>
            <span class="topbar-title">📊 Conciliação Contábil</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div style="text-align:center"><span class="sec-title">Selecione a empresa</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="text-align:center;margin-bottom:32px"><span class="sec-sub">Escolha a empresa para acessar o módulo de conciliação contábil</span></div>',
        unsafe_allow_html=True,
    )

    # ── Cards ──
    col_l, col_nc, col_mf, col_r = st.columns([1, 2, 2, 1])

    with col_nc:
        st.markdown(
            """
            <div class="emp-card" style="border-color:#2196C4;">
              <div style="font-size:48px;margin-bottom:12px">🏢</div>
              <div style="font-size:18px;font-weight:700;color:#2D3748;margin-bottom:6px">Nutricash</div>
              <div style="font-size:12px;color:#718096;line-height:1.5;margin-bottom:20px">
                Benefícios, alimentação e gestão de pagamentos corporativos
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("ACESSAR → Nutricash", use_container_width=True, key="btn_nc",
                     type="primary"):
            st.session_state.empresa = "nc"
            st.session_state.page = "dashboard"
            st.rerun()

    with col_mf:
        st.markdown(
            """
            <div class="emp-card" style="border-color:#F5A800;">
              <div style="font-size:48px;margin-bottom:12px">🚛</div>
              <div style="font-size:18px;font-weight:700;color:#2D3748;margin-bottom:6px">MaxiFrota</div>
              <div style="font-size:12px;color:#718096;line-height:1.5;margin-bottom:20px">
                Gestão de frotas, abastecimento e mobilidade corporativa
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("ACESSAR → MaxiFrota", use_container_width=True, key="btn_mf"):
            st.session_state.empresa = "mf"
            st.session_state.page = "dashboard"
            st.rerun()

    # ── Footer info ──
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        '<div style="text-align:center;font-size:11px;color:#A0AEC0;">Sistema de Conciliação Contábil v4</div>',
        unsafe_allow_html=True,
    )
