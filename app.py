import streamlit as st
import pandas as pd
import sqlite3
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

# Injeção de CSS para Modo Escuro Premium
st.markdown("""
    <style>
    button[data-testid="sidebar-toggle"] span { display: none !important; }
    button[data-testid="sidebar-toggle"]::after {
        content: " ☰" !important; font-size: 18px !important; color: #00E676 !important;
    }
    header[data-testid="stHeader"], .stHeader, [data-testid="stHeader"] {
        background-color: #111622 !important; background: #111622 !important; border-bottom: 1px solid #1E293B !important;
    }
    div[data-testid="stDecoration"] {
        background-image: none !important; background-color: #00E676 !important; height: 3px !important;
    }
    .stApp { background-color: #0A0D14 !important; }
    section[data-testid="stSidebar"] {
        background-color: #111622 !important; border-right: 1px solid #1E293B !important;
    }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] span, 
    section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] p {
        color: #FFFFFF !important;
    }
    .main .block-container {
        background-color: #111622 !important; padding: 35px 45px !important;
        border-radius: 12px !important; border: 1px solid #1E293B !important;
        margin-top: 15px !important; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3) !important;
    }
    h1 {
        color: #FFFFFF !important; font-weight: 700 !important; font-size: 2.2rem !important;
        border-bottom: 2px solid #00E676 !important; padding-bottom: 10px; margin-bottom: 20px !important;
    }
    h2, h3, label { color: #00E676 !important; }
    .stMarkdown p, th, td { color: #E2E8F0 !important; }
    [data-testid="stMetric"] {
        background-color: #1A202C !important; padding: 20px !important; border-radius: 8px !important; border: 1px solid #2D3748 !important;
    }
    [data-testid="stMetricValue"] {
        color: #00E676 !important; font-weight: 700 !important; font-size: 2.2rem !important; text-shadow: 0 0 10px rgba(0, 230, 118, 0.2);
    }
    [data-testid="stMetricLabel"] { color: #94A3B8 !important; font-weight: bold !important; text-transform: uppercase; }
    div[data-baseweb="select"], div[data-baseweb="input"], input {
        background-color: #1A202C !important; color: #FFFFFF !important; border: 1px solid #2D3748 !important;
    }
    .stButton>button {
        background-color: #00E676 !important; color: #0A0D14 !important; border-radius: 6px !important;
        font-weight: bold !important; border: none !important; padding: 12px;
        box-shadow: 0 4px 14px rgba(0, 230, 118, 0.3) !important; transition: all 0.2s ease;
    }
    .stButton>button:hover { 
        background-color: #00B248 !important; color: #FFFFFF !important; box-shadow: 0 6px 20px rgba(0, 178, 72, 0.4) !important;
    }
    .stDataFrame { background-color: #1A202C !important; border-radius: 6px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# GERENCIAMENTO DE BANCO DE DADOS (SQLITE)
# ==========================================
DB_FILE = "banco_coco_verde.db"

def conectar_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_banco():
    conn = conectar_db()
    cursor = conn.cursor()
    # Criar tabela de vendas se não existir
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_hora TEXT,
            dia_semana TEXT,
            semana_ano TEXT,
            atendente TEXT,
            produto TEXT,
            qtd_cocos INTEGER,
            total REAL,
            lucro REAL
        )
    """)
    # Criar tabela de estoque se não existir
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estoque (
            id INTEGER PRIMARY KEY,
            quantidade INTEGER,
            custo_unitario REAL
        )
    """)
    
    # Verificar se o estoque já foi configurado alguma vez, senão insere o inicial padrão (100 unidades)
    cursor.execute("SELECT COUNT(*) FROM estoque")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO estoque (id, quantidade, custo_unitario) VALUES (1, 100, 2.40)")
        
        # Inserir vendas iniciais fictícias apenas para o primeiro carregamento do sistema
        cursor.execute("""
            INSERT INTO vendas (data_hora, dia_semana, semana_ano, atendente, produto, qtd_cocos, total, lucro)
            VALUES ('29/05/2026 09:30', 'Sexta-feira', 'Semana 22 (2026)', 'Mariana', '🍼 Garrafa de 500ml', 2, 6.00, 1.20)
        """)
        cursor.execute("""
            INSERT INTO vendas (data_hora, dia_semana, semana_ano, atendente, produto, qtd_cocos, total, lucro)
            VALUES ('29/05/2026 10:15', 'Sexta-feira', 'Semana 22 (2026)', 'Carlos', '🥥 Coco Normal no Canudo', 1, 4.00, 1.60)
        """)
        
    conn.commit()
    conn.close()

# Executa a inicialização automática do banco
inicializar_banco()

def obter_dados_estoque():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT quantidade, custo_unitario FROM estoque WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    return row["quantidade"], row["custo_unitario"]

def atualizar_dados_estoque(nova_qtd):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE estoque SET quantidade = ? WHERE id = 1", (nova_qtd,))
    conn.commit()
    conn.close()

def obter_todas_vendas():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vendas")
    rows = cursor.fetchall()
    conn.close()
    
    lista_vendas = []
    for row in rows:
        lista_vendas.append({
            "id": row["id"],
            "data_hora": row["data_hora"],
            "dia_semana": row["dia_semana"],
            "semana_ano": row["semana_ano"],
            "atendente": row["atendente"],
            "produto": row["produto"],
            "qtd_cocos": row["qtd_cocos"],
            "total": row["total"],
            "lucro": row["lucro"]
        })
    return lista_vendas

def salvar_nova_venda(data_hora, dia, semana, atendente, produto, qtd_cocos, total, lucro):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO vendas (data_hora, dia_semana, semana_ano, atendente, produto, qtd_cocos, total, lucro)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (data_hora, dia, semana, atendente, produto, qtd_cocos, total, lucro))
    conn.commit()
    conn.close()

def remover_venda_db(id_venda):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vendas WHERE id = ?", (id_venda,))
    conn.commit()
    conn.close()

# Carregar variáveis dinâmicas do Banco SQLite estável
estoque_atual, custo_unitario = obter_dados_estoque()
lista_vendas_atual = obter_todas_vendas()

# ==========================================
# CARDÁPIO OPERACIONAL DE PREÇOS
# ==========================================
PRODUTOS = {
    "🥥 Coco Normal no Canudo": {"preco": 4.00, "cocos": 1},
    "🍼 Garrafa de 300ml": {"preco": 4.00, "cocos": 1},
    "🍼 Garrafa de 500ml": {"preco": 6.00, "cocos": 2},
    "🍼 Garrafa de 1 Litro": {"preco": 10.00, "cocos": 3}
}

# ==========================================
# MENU LATERAL - COCO VERDE EXPRESS
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
st.sidebar.markdown(f"🔋 **Estoque Operacional:** `{estoque_atual} un`")

# ==========================================
# MÓDULO 1: 📊 PAINEL GERAL (DASHBOARD)
# ==========================================
if area_selecionada == "📊 Painel Geral":
    st.markdown("# 📊 Painel Geral de Desempenho")
    
    if lista_vendas_atual:
        semanas_disponiveis = sorted(list(set(v["semana_ano"] for v in lista_vendas_atual)), reverse=True)
        semanas_disponiveis.insert(0, "Todas as Semanas")
        semana_selecionada = st.selectbox("📅 Filtrar Visualização por Período / Semana:", semanas_disponiveis)
        
        if semana_selecionada == "Todas as Semanas":
            vendas_filtradas = lista_vendas_atual
        else:
            vendas_filtradas = [v for v in lista_vendas_atual if v["semana_ano"] == semana_selecionada]
    else:
        vendas_filtradas = []
        st.info("Nenhuma movimentação lançada no sistema.")

    st.markdown("---")
    
    faturamento = sum(v["total"] for v in vendas_filtradas)
    total_pedidos = len(vendas_filtradas)
    lucro_total = sum(v["lucro"] for v in vendas_filtradas)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="💰 Faturamento Bruto", value=f"R$ {faturamento:.2f}")
    with col2:
        st.metric(label="📈 Lucro Líquido Estimado", value=f"R$ {lucro_total:.2f}")
    with col3:
        st.metric(label="🤝 Pedidos no Período", value=f"{total_pedidos} vendas")
        
    st.markdown("---")
    st.markdown("### 🏆 Rendimento por Atendente no Período Filtrado")
    
    ranking = {}
    for v in vendas_filtradas:
        ranking[v["atendente"]] = ranking.get(v["atendente"], 0) + v["total"]
        
    if ranking:
        df_ranking = pd.DataFrame(list(ranking.items()), columns=["Atendente", "Faturamento Total (R$)"]).sort_values(by="Faturamento Total (R$)", ascending=False)
        st.dataframe(df_ranking, use_container_width=True, hide_index=True)
    else:
        st.caption("Sem dados para exibir o ranking nesta semana.")

# ==========================================
# MÓDULO 2: 📦 GERENCIAR ESTOQUE
# ==========================================
elif area_selecionada == "📦 Gerenciar Estoque":
    st.markdown("# 📦 Controle de Inventário de Frutas")
    st.write(f"Capacidade física atual em depósito: **{estoque_atual} cocos**")
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 📥 Entrada de Lote")
        qtd_nova = st.number_input("Quantidade de cocos recebidos:", min_value=1, step=1, value=50)
        if st.button("Salvar Nova Carga"):
            atualizar_dados_estoque(estoque_atual + qtd_nova)
            st.success(f"Entrada confirmada! +{qtd_nova} unidades inseridas de forma definitiva.")
            st.rerun()
            
    with c2:
        st.markdown("### 🚨 Ajustes Extraordinários")
        st.caption("Ação crítica para sincronizar a contagem após auditoria de balanço.")
        if st.button("Zerar Contagem Manual"):
            atualizar_dados_estoque(0)
            st.warning("Estoque ajustado para zero no banco de dados.")
            st.rerun()

# ==========================================
# MÓDULO 3: 💸 REALIZAR VENDA (PDV)
# ==========================================
elif area_selecionada == "💸 Realizar Venda":
    st.markdown("# 💸 Terminal de Vendas (PDV)")
    st.markdown("---")
    
    if estoque_atual <= 0:
        st.error("Alerta do Sistema: Terminal bloqueado por falta de insumos em estoque.")
    else:
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            atendente = st.text_input("Nome do Atendente:", placeholder="Digite quem está vendendo...").strip()
            produto_sel = st.selectbox("Selecione o Item:", list(PRODUTOS.keys()))
        with col_v2:
            cocos_necessarios = PRODUTOS[produto_sel]["cocos"]
            limite_maximo = int(estoque_atual / cocos_necessarios)
            
            if limite_maximo < 1:
                st.error("Insumos insuficientes em estoque para preparar esta embalagem!")
                qtd_venda = 0
            else:
                qtd_venda = st.number_input("Quantidade Vendida:", min_value=1, max_value=limite_maximo, value=1, step=1)
                
        if qtd_venda > 0:
            valor_final = qtd_venda * PRODUTOS[produto_sel]["preco"]
            custo_venda = (qtd_venda * cocos_necessarios) * custo_unitario
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
                
                num_semana = momento_atual.strftime("%U")
                ano_atual = momento_atual.strftime("%Y")
                texto_semana = f"Semana {num_semana} ({ano_atual})"
                
                # Descontar do estoque e salvar nova linha no SQLite de forma definitiva
                atualizar_dados_estoque(estoque_atual - (qtd_venda * cocos_necessarios))
                salvar_nova_venda(data_hora_texto, dia_pt, texto_semana, atendente, produto_sel, (qtd_venda * cocos_necessarios), valor_final, lucro_venda)
                
                st.success("Venda registrada automaticamente no banco de dados!")
                st.rerun()

# ==========================================
# MÓDULO 4: 📜 HISTÓRICO DE VENDAS E EXCLUSÃO
# ==========================================
elif area_selecionada == "📜 Histórico de Vendas":
    st.markdown("# 📜 Relatório de Auditoria de Caixa")
    st.markdown("Verifique os registros cronológicos estáveis ou execute exclusões.")
    st.markdown("---")
    
    if not lista_vendas_atual:
        st.info("Nenhuma movimentação arquivada no banco de dados.")
    else:
        col_tabela, col_estorno = st.columns([3, 1])
        
        with col_tabela:
            df_historico = pd.DataFrame(lista_vendas_atual)
            df_historico = df_historico[["id", "data_hora", "semana_ano", "atendente", "produto", "qtd_cocos", "total"]]
            df_historico.columns = ["ID", "Data/Hora", "Semana Operacional", "Atendente", "Produto", "Cocos Usados", "Valor Total (R$)"]
            
            st.dataframe(df_historico.sort_values(by="ID", ascending=False), use_container_width=True, hide_index=True)
            
        with col_estorno:
            st.markdown("### 🚨 Painel de Estorno")
            
            lista_ids = [v["id"] for v in lista_vendas_atual]
            id_selecionado = st.selectbox("Selecione o ID:", lista_ids)
            confirmar = st.checkbox("Confirmar cancelamento.")
            
            if st.button("Remover Registro", disabled=not confirmar):
                venda_para_remover = next((v for v in lista_vendas_atual if v["id"] == id_selecionado), None)
                
                if venda_para_remover:
                    # Devolve os cocos ao estoque e deleta a linha no banco de dados SQLite
                    atualizar_dados_estoque(estoque_atual + venda_para_remover["qtd_cocos"])
                    remover_venda_db(id_selecionado)
                    st.success(f"Lançamento #{id_selecionado} removido e estornado!")
                    st.rerun()
