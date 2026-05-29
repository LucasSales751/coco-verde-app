import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone

# ==========================================
# CONFIGURAÇÃO DE LAYOUT E IDENTIDADE VISUAL
# ==========================================
st.set_page_config(
    page_title="Coco Verde Express • Dashboard",
    page_icon="🥥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dicionário auxiliar para tradução dos dias da semana
DIAS_SEMANA = {
    "Monday": "Segunda-feira", "Tuesday": "Terça-feira", "Wednesday": "Quarta-feira",
    "Thursday": "Quinta-feira", "Friday": "Sexta-feira", "Saturday": "Sábado", "Sunday": "Domingo"
}

# INJEÇÃO DO MANIFESTO E METATAGS DE TELA CHEIA (ESTILO APLICATIVO IOS/ANDROID)
st.markdown("""
    <head>
        <link rel="manifest" href="manifest.json">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
        <meta name="mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-title" content="Coco Verde">
    </head>
""", unsafe_allow_html=True)

# Injeção de CSS - Modo Escuro Tecnológico Unificado (Sem Topo Branco)
st.markdown("""
    <style>
    /* CORREÇÃO DO TEXTO FANTASMA DO BOTÃO NATIVO */
    button[data-testid="sidebar-toggle"] span {
        display: none !important;
    }
    button[data-testid="sidebar-toggle"]::after {
        content: " ☰" !important;
        font-size: 18px !important;
        color: #00E676 !important;
    }

    /* REMOVE A FAIXA BRANCA DO TOPO - CORREÇÃO COMPLETA DE HEADER */
    header[data-testid="stHeader"], 
    .stHeader, 
    [data-testid="stHeader"] {
        background-color: #111622 !important;
        background: #111622 !important;
        border-bottom: 1px solid #1E293B !important;
    }
    
    /* Linha decorativa verde neon discreta no topo */
    div[data-testid="stDecoration"] {
        background-image: none !important;
        background-color: #00E676 !important;
        height: 3px !important;
    }

    /* 1. ESTILIZAÇÃO DO FUNDO DA APLICAÇÃO (DARK UNIFICADO) */
    .stApp {
        background-color: #0A0D14 !important;
    }
    
    /* 2. SIDEBAR LATERAL (GRAFITE ESCURO PREMIUM) */
    section[data-testid="stSidebar"] {
        background-color: #111622 !important;
        border-right: 1px solid #1E293B !important;
    }
    
    /* Forçar textos da barra lateral para Branco e Verde */
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] span, 
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p {
        color: #FFFFFF !important;
    }

    /* 3. BLOCO CENTRAL (CARD ESTILO PAINEL DE CONTROLE) */
    .main .block-container {
        background-color: #111622 !important;
        padding: 35px 45px !important;
        border-radius: 12px !important;
        border: 1px solid #1E293B !important;
        margin-top: 15px !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3) !important;
    }
    
    /* 4. TÍTULOS E TEXTOS DO PAINEL CENTRAL */
    h1 {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 2.2rem !important;
        border-bottom: 2px solid #00E676 !important;
        padding-bottom: 10px;
        margin-bottom: 20px !important;
    }
    h2, h3, label {
        color: #00E676 !important; /* Verde Cyberpunk */
    }
    .stMarkdown p, th, td {
        color: #E2E8F0 !important;
    }
    
    /* 5. CARDS DE MÉTRICAS OPERACIONAIS */
    [data-testid="stMetric"] {
        background-color: #1A202C !important;
        padding: 20px !important;
        border-radius: 8px !important;
        border: 1px solid #2D3748 !important;
    }
    [data-testid="stMetricValue"] {
        color: #00E676 !important;
        font-weight: 700 !important;
        font-size: 2.2rem !important;
        text-shadow: 0 0 10px rgba(0, 230, 118, 0.2);
    }
    [data-testid="stMetricLabel"] {
        color: #94A3B8 !important;
        font-weight: bold !important;
        text-transform: uppercase;
    }

    /* 6. INPUTS E SELETORES EM MODO DARK */
    div[data-baseweb="select"], div[data-baseweb="input"], input {
        background-color: #1A202C !important;
        color: #FFFFFF !important;
        border: 1px solid #2D3748 !important;
    }

    /* 7. BOTÕES OPERACIONAIS GLOW */
    .stButton>button {
        background-color: #00E676 !important;
        color: #0A0D14 !important;
        border-radius: 6px !important;
        font-weight: bold !important;
        border: none !important;
        padding: 12px;
        box-shadow: 0 4px 14px rgba(0, 230, 118, 0.3) !important;
        transition: all 0.2s ease;
    }
    .stButton>button:hover { 
        background-color: #00B248 !important;
        color: #FFFFFF !important;
        box-shadow: 0 6px 20px rgba(0, 178, 72, 0.4) !important;
    }
    
    /* Customização das Tabelas / Dataframes */
    .stDataFrame {
        background-color: #1A202C !important;
        border-radius: 6px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# BASE DE DADOS REAL - PREÇOS DO PRODUTOR
# ==========================================
PRODUTOS = {
    "🥥 Coco Normal no Canudo": {"preco": 4.00, "cocos": 1},
    "🍼 Garrafa de 300ml": {"preco": 4.00, "cocos": 1},
    "🍼 Garrafa de 500ml": {"preco": 6.00, "cocos": 2},
    "🍼 Garrafa de 1 Litro": {"preco": 10.00, "cocos": 3}
}

if 'estoque' not in st.session_state:
    st.session_state.estoque = 29  
if 'custo_unitario' not in st.session_state:
    st.session_state.custo_unitario = 2.40  
if 'vendas' not in st.session_state:
    st.session_state.vendas = [
        {
            "id": 1, 
            "data_hora": "29/05/2026 09:30", 
            "dia_semana": "Sexta-feira", 
            "atendente": "Mariana", 
            "produto": "🍼 Garrafa de 500ml", 
            "qtd_cocos": 2, 
            "total": 6.00, 
            "lucro": 6.00 - (2 * 2.40)
        },
        {
            "id": 2, 
            "data_hora": "29/05/2026 10:15", 
            "dia_semana": "Sexta-feira", 
            "atendente": "Carlos", 
            "produto": "🥥 Coco Normal no Canudo", 
            "qtd_cocos": 1, 
            "total": 4.00, 
            "lucro": 4.00 - (1 * 2.40)
        }
    ]

# ==========================================
# MENU LATERAL - NOMENCLATURA COCO VERDE EXPRESS
# ==========================================
st.sidebar.markdown("# 🥥 COCO VERDE EXPRESS")
st.sidebar.markdown("---")

st.sidebar.markdown("### Selecione o Módulo:")
area_selecionada = st.sidebar.radio(
    label="Navegação",
    options=["📊 Painel Geral", "📦 Gerenciar Estoque", "💸 Realizar Venda", "📜 Histórico de Vendas"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"🔋 **Estoque Operacional:** `{st.session_state.estoque} un`")

# ==========================================
# MÓDULO 1: 📊 PAINEL GERAL (DASHBOARD)
# ==========================================
if area_selecionada == "📊 Painel Geral":
    st.markdown("# 📊 Painel Geral de Desempenho")
    st.markdown("Métricas consolidadas de faturamento, vendas e fluxo.")
    
    faturamento = sum(v["total"] for v in st.session_state.vendas)
    total_pedidos = len(st.session_state.vendas)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="💰 Faturamento Bruto", value=f"R$ {faturamento:.2f}")
    with col2:
        st.metric(label="🤝 Pedidos Concluídos", value=f"{total_pedidos} vendas")
    with col3:
        st.metric(label="📦 Saldo em Depósito", value=f"{st.session_state.estoque} un")
        
    st.markdown("---")
    st.markdown("### 🏆 Rendimento por Atendente")
    
    ranking = {}
    for v in st.session_state.vendas:
        ranking[v["atendente"]] = ranking.get(v["atendente"], 0) + v["total"]
        
    if ranking:
        df_ranking = pd.DataFrame(list(ranking.items()), columns=["Atendente", "Faturamento Total (R$)"]).sort_values(by="Faturamento Total (R$)", ascending=False)
        st.dataframe(df_ranking, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma movimentação lançada.")

# ==========================================
# MÓDULO 2: 📦 GERENCIAR ESTOQUE
# ==========================================
elif area_selecionada == "📦 Gerenciar Estoque":
    st.markdown("# 📦 Controle de Inventário de Frutas")
    st.write(f"Capacidade física atual em depósito: **{st.session_state.estoque} cocos**")
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 📥 Entrada de Lote")
        qtd_nova = st.number_input("Quantidade de cocos recebidos:", min_value=1, step=1, value=50)
        if st.button("Salvar Nova Carga"):
            st.session_state.estoque += qtd_nova
            st.success(f"Entrada confirmada! +{qtd_nova} unidades inseridas.")
            st.rerun()
            
    with c2:
        st.markdown("### 🚨 Ajustes Extraordinários")
        st.caption("Ação crítica para sincronizar a contagem após auditoria de balanço.")
        if st.button("Zerar Contagem Manual"):
            st.session_state.estoque = 0
            st.warning("Estoque adjusted para zero.")
            st.rerun()

# ==========================================
# MÓDULO 3: 💸 REALIZAR VENDA (PDV)
# ==========================================
elif area_selecionada == "💸 Realizar Venda":
    st.markdown("# 💸 Terminal de Vendas (PDV)")
    st.markdown("---")
    
    if st.session_state.estoque <= 0:
        st.error("Alerta do Sistema: Terminal bloqueado por falta de insumos.")
    else:
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            atendente = st.text_input("Nome do Atendente:", placeholder="Digite quem está vendendo...").strip()
            produto_sel = st.selectbox("Selecione o Item:", list(PRODUTOS.keys()))
        with col_v2:
            cocos_necessarios = PRODUTOS[produto_sel]["cocos"]
            limite_maximo = int(st.session_state.estoque / cocos_necessarios)
            
            if limite_maximo < 1:
                st.error("Insumos insuficientes para preparar esta embalagem!")
                qtd_venda = 0
            else:
                qtd_venda = st.number_input("Quantidade Vendida:", min_value=1, max_value=limite_maximo, value=1, step=1)
                
        if qtd_venda > 0:
            valor_final = qtd_venda * PRODUTOS[produto_sel]["preco"]
            custo_venda = (qtd_venda * cocos_necessarios) * st.session_state.custo_unitario
            lucro_venda = valor_final - custo_venda
            
            st.markdown(f"### Total do Pedido: <span style='color:#00E676;'>**R$ {valor_final:.2f}**</span>", unsafe_allow_html=True)
            
            if not atendente:
                st.warning("Por favor, digite o nome do atendente antes de confirmar.")
                botao_desabilitado = True
            else:
                botao_desabilitado = False
                
            if st.button("Confirmar e Registrar", disabled=botao_desabilitado):
                fuso_br = timezone(timedelta(hours=-3))
                momento_atual = datetime.now(fuso_br)
                
                data_hora_texto = momento_atual.strftime("%d/%m/%Y %H:%M")
                dia_nome_en = momento_atual.strftime("%A")
                dia_pt = DIAS_SEMANA.get(dia_nome_en, dia_nome_en)
                
                st.session_state.estoque -= (qtd_venda * cocos_necessarios)
                novo_id = max([v["id"] for v in st.session_state.vendas]) + 1 if st.session_state.vendas else 1
                
                st.session_state.vendas.append({
                    "id": novo_id,
                    "data_hora": data_hora_texto,
                    "dia_semana": dia_pt,
                    "atendente": atendente,
                    "produto": produto_sel,
                    "qtd_cocos": qtd_venda * cocos_necessarios,
                    "total": valor_final,
                    "lucro": lucro_venda
                })
                st.success(f"Venda registrada com sucesso! ID #{novo_id}")
                st.rerun()

# ==========================================
# MÓDULO 4: 📜 HISTÓRICO DE VENDAS E EXCLUSÃO
# ==========================================
elif area_selecionada == "📜 Histórico de Vendas":
    st.markdown("# 📜 Relatório de Auditoria de Caixa")
    st.markdown("Verifique os registros cronológicos ou execute exclusões para estorno.")
    st.markdown("---")
    
    if not st.session_state.vendas:
        st.info("Nenhuma movimentação arquivada.")
    else:
        col_tabela, col_estorno = st.columns([3, 1])
        
        with col_tabela:
            df_historico = pd.DataFrame(st.session_state.vendas)
            df_historico = df_historico[["id", "data_hora", "dia_semana", "atendente", "produto", "qtd_cocos", "total"]]
            df_historico.columns = ["ID", "Data/Hora", "Dia da Semana", "Atendente", "Produto", "Cocos Usados", "Valor Total (R$)"]
            
            st.dataframe(df_historico.sort_values(by="ID", ascending=False), use_container_width=True, hide_index=True)
            
        with col_estorno:
            st.markdown("### 🚨 Painel de Estorno")
            
            lista_ids = [v["id"] for v in st.session_state.vendas]
            id_selecionado = st.selectbox("Selecione o ID:", lista_ids)
            confirmar = st.checkbox("Confirmar cancelamento.")
            
            if st.button("Remover Registro", disabled=not confirmar):
                venda_para_remover = next((v for v in st.session_state.vendas if v["id"] == id_selecionado), None)
                
                if venda_para_remover:
                    st.session_state.estoque += venda_para_remover["qtd_cocos"]
                    st.session_state.vendas = [v for v in st.session_state.vendas if v["id"] != id_selecionado]
                    st.success(f"Lançamento #{id_selecionado} deletado.")
                    st.rerun()
