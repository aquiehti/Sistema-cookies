import streamlit as st
import pandas as pd

# Configuração da página com layout mobile-friendly
st.set_page_config(
    page_title="CookieGestão App",
    page_icon="🍪",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CSS CUSTOMIZADO PARA DAR CARA DE APLICATIVO MOBILE ---
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        background-color: #ff6b6b;
        color: white;
        font-weight: bold;
        height: 48px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #ff5252;
        color: white;
    }
    div.stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# --- ESTADO INICIAL DA APLICAÇÃO ---
if "insumos" not in st.session_state:
    st.session_state.insumos = pd.DataFrame([
        {"Ingrediente": "Farinha de Trigo", "Unidade": "g", "Qtd Embalagem": 1000.0, "Preço Última Compra (R$)": 5.50},
        {"Ingrediente": "Manteiga sem Sal", "Unidade": "g", "Qtd Embalagem": 500.0, "Preço Última Compra (R$)": 24.00},
        {"Ingrediente": "Açúcar Mascavo", "Unidade": "g", "Qtd Embalagem": 500.0, "Preço Última Compra (R$)": 6.50},
        {"Ingrediente": "Gotas de Chocolate", "Unidade": "g", "Qtd Embalagem": 1000.0, "Preço Última Compra (R$)": 48.00},
        {"Ingrediente": "Ovos", "Unidade": "un", "Qtd Embalagem": 12.0, "Preço Última Compra (R$)": 12.00},
    ])

if "receitas" not in st.session_state:
    st.session_state.receitas = pd.DataFrame([
        {"Sabor": "Tradicional", "Ingrediente": "Farinha de Trigo", "Qtd Usada": 250.0},
        {"Sabor": "Tradicional", "Ingrediente": "Manteiga sem Sal", "Qtd Usada": 150.0},
        {"Sabor": "Tradicional", "Ingrediente": "Açúcar Mascavo", "Qtd Usada": 100.0},
        {"Sabor": "Tradicional", "Ingrediente": "Gotas de Chocolate", "Qtd Usada": 200.0},
        {"Sabor": "Tradicional", "Ingrediente": "Ovos", "Qtd Usada": 1.0},
    ])

if "precos_praticados" not in st.session_state:
    st.session_state.precos_praticados = {
        "Tradicional": 5.50
    }

if "rendimentos" not in st.session_state:
    st.session_state.rendimentos = {
        "Tradicional": 12
    }

st.title("🍪 CookieGestão App")
st.markdown("---")

# Navegação em Abas Estilo App Mobile
aba1, aba2, aba3, aba4 = st.tabs(["📦 Insumos", "📖 Receitas", "💰 Precificação", "📄 Orçamento"])

# --- ABA 1: ESTOQUE DE INSUMOS & ÚLTIMA COMPRA ---
with aba1:
    st.subheader("📦 Seus Insumos e Última Compra")
    st.markdown("Atualize o preço pago na última ida ao mercado. O custo dos cookies será recalculado automaticamente!")
    
    with st.form("form_insumo", clear_on_submit=True):
        st.markdown("#### Adicionar / Atualizar Insumo")
        nome_ing = st.text_input("Nome do Ingrediente (ex: Farinha, Chocolate, Embalagem)")
        unidade_ing = st.selectbox("Unidade de Medida", ["g", "ml", "un"])
        qtd_emb = st.number_input("Quantidade na Embalagem (ex: 1000 para 1kg, 12 para ovos)", min_value=0.01, value=1000.0)
        preco_compra = st.number_input("Preço Pago na Última Compra (R$)", min_value=0.01, value=10.0)
        
        btn_salvar_ing = st.form_submit_button("Salvar no Estoque")
        if btn_salvar_ing and nome_ing:
            df_ins = st.session_state.insumos
            if nome_ing in df_ins["Ingrediente"].values:
                df_ins.loc[df_ins["Ingrediente"] == nome_ing, ["Unidade", "Qtd Embalagem", "Preço Última Compra (R$)"]] = [unidade_ing, qtd_emb, preco_compra]
                st.success(f"Insumo '{nome_ing}' atualizado com sucesso!")
            else:
                novo_reg = pd.DataFrame([{"Ingrediente": nome_ing, "Unidade": unidade_ing, "Qtd Embalagem": qtd_emb, "Preço Última Compra (R$)": preco_compra}])
                st.session_state.insumos = pd.concat([df_ins, novo_reg], ignore_index=True)
                st.success(f"Insumo '{nome_ing}' adicionado com sucesso!")

    st.markdown("### 📋 Estoque Atual")
    for _, row in st.session_state.insumos.iterrows():
        custo_unit_base = row["Preço Última Compra (R$)"] / row["Qtd Embalagem"] if row["Qtd Embalagem"] > 0 else 0
        with st.container():
            st.markdown(f"""
            **{row['Ingrediente']}** ({row['Unidade']})  
            *Embalagem:* {row['Qtd Embalagem']} {row['Unidade']} | *Última Compra:* R$ {row['Preço Última Compra (R$)']:.2f}  
            ⚡ *Custo por {row['Unidade']}:* R$ {custo_unit_base:.4f}
            """)
            st.divider()

# --- ABA 2: RECEITAS DINÂMICAS ---
with aba2:
    st.subheader("📖 Ficha Técnica de Receitas")
    st.markdown("Monte a receita selecionando os insumos cadastrados no seu estoque.")
    
    with st.form("form_receita", clear_on_submit=True):
        sabor_nome = st.text_input("Nome do Sabor do Cookie (ex: Ninho com Nutella)")
        ing_disponiveis = st.session_state.insumos["Ingrediente"].tolist()
        
        if not ing_disponiveis:
            st.warning("Cadastre insumos na aba anterior primeiro!")
        else:
            ing_sel = st.selectbox("Selecionar Ingrediente do Estoque", ing_disponiveis)
            qtd_usada_rec = st.number_input("Quantidade usada na fornada", min_value=0.01, value=50.0)
            rendimento_fornada = st.number_input("Quantos cookies essa fornada rende?", min_value=1, value=12)
            
            btn_add_receita = st.form_submit_button("Adicionar à Receita")
            if btn_add_receita and sabor_nome:
                st.session_state.rendimentos[sabor_nome] = rendimento_fornada
                nova_linha = pd.DataFrame([{"Sabor": sabor_nome, "Ingrediente": ing_sel, "Qtd Usada": qtd_usada_rec}])
                st.session_state.receitas = pd.concat([st.session_state.receitas, nova_linha], ignore_index=True)
                st.success(f"Ingrediente adicionado ao cookie {sabor_nome}!")

    st.markdown("### 🍳 Receitas Cadastradas")
    sabores_cadastrados = st.session_state.receitas["Sabor"].unique()
    for sabor in sabores_cadastrados:
        with st.expander(f"🍪 Sabor: {sabor} (Rendimento: {st.session_state.rendimentos.get(sabor, 12)} un)"):
            itens_sabor = st.session_state.receitas[st.session_state.receitas["Sabor"] == sabor]
            st.dataframe(itens_sabor, use_container_width=True)
            
            if st.button(f"Excluir receita '{sabor}'", key=f"del_rec_{sabor}"):
                st.session_state.receitas = st.session_state.receitas[st.session_state.receitas["Sabor"] != sabor]
                st.rerun()

# --- ABA 3: PRECIFICAÇÃO & MARGEM PERCENTUAL REAL ---
with aba3:
    st.subheader("💰 Precificação & Margem de Lucro (%)")
    st.markdown("Defina seu **Preço Praticado**. O sistema calcula a margem percentual real instantaneamente!")
    
    sabores = st.session_state.receitas["Sabor"].unique()
    
    for sabor in sabores:
        itens_sab = st.session_state.receitas[st.session_state.receitas["Sabor"] == sabor]
        custo_total_lote = 0
        
        for _, row in itens_sab.iterrows():
            ing_info = st.session_state.insumos[st.session_state.insumos["Ingrediente"] == row["Ingrediente"]]
            if not ing_info.empty:
                preco_compra = ing_info.iloc[0]["Preço Última Compra (R$)"]
                qtd_emb = ing_info.iloc[0]["Qtd Embalagem"]
                custo_unit_base = preco_compra / qtd_emb if qtd_emb > 0 else 0
                custo_total_lote += custo_unit_base * row["Qtd Usada"]
        
        rendimento = st.session_state.rendimentos.get(sabor, 12)
        custo_unitario = custo_total_lote / rendimento if rendimento > 0 else 0
        sugerido_padrao = custo_unitario * 2.5
        
        if sabor not in st.session_state.precos_praticados:
            st.session_state.precos_praticados[sabor] = round(sugerido_padrao, 2)
            
        st.markdown(f"### 🍪 {sabor}")
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("Custo Produção Unitário", f"R$ {custo_unitario:.2f}")
        col_m2.metric("Preço Sugerido (Sist.)", f"R$ {sugerido_padrao:.2f}")
        
        # Campo editável para o preço praticado pela cliente
        preco_atual = st.session_state.precos_praticados[sabor]
        novo_preco_praticado = st.number_input(
            f"Preço Praticado por Unidade (R$) - {sabor}", 
            min_value=0.01, 
            value=float(preco_atual), 
            step=0.10,
            key=f"preco_praticado_{sabor}"
        )
        st.session_state.precos_praticados[sabor] = novo_preco_praticado
        
        # Lucro e Margem Percentual Real
        lucro_unitario = novo_preco_praticado - custo_unitario
        margem_percentual = (lucro_unitario / novo_preco_praticado) * 100 if novo_preco_praticado > 0 else 0
        
        if margem_percentual < 30:
            alerta = "⚠️ Margem Baixa"
        elif margem_percentual < 50:
            alerta = "✅ Boa Margem"
        else:
            alerta = "🔥 Excelente Margem"
            
        st.markdown(f"""
        * **Lucro por Unidade:** R$ {lucro_unitario:.2f}
        * **Margem de Lucro Real:** **{margem_percentual:.1f}%** ({alerta})
        """)
        st.divider()

# --- ABA 4: ORÇAMENTO ---
with aba4:
    st.subheader("📄 Gerador de Orçamento Rápido")
    cliente_nome = st.text_input("Nome da Cliente / Festa", value="Maria da Silva")
    
    sabores_disponiveis = list(st.session_state.precos_praticados.keys())
    if not sabores_disponiveis:
        st.warning("Cadastre receitas e preços primeiro!")
    else:
        sabor_orc = st.selectbox("Sabor do Cookie", sabores_disponiveis)
        qtd_orc = st.number_input("Quantidade de Cookies", min_value=1, value=10)
        
        preco_unit_venda = st.session_state.precos_praticados.get(sabor_orc, 5.00)
        subtotal_orc = qtd_orc * preco_unit_venda
        
        st.markdown("---")
        st.markdown("### 🛒 Resumo da Proposta")
        st.markdown(f"""
        * **Cliente:** {cliente_nome}
        * **Item:** {qtd_orc}x Cookies de {sabor_orc}
        * **Preço Unitário Praticado:** R$ {preco_unit_venda:.2f}
        * ### **TOTAL DO PEDIDO: R$ {subtotal_orc:.2f}**
        """)
        
        if st.button("Gerar Mensagem Pronta para WhatsApp"):
            msg_zap = f"Olá, {cliente_nome}! 🍪 Segue o orçamento dos cookies artesanais:\n\n* {qtd_orc}x Cookies de {sabor_orc}\n* Valor Unitário: R$ {preco_unit_venda:.2f}\n* *Total do Pedido: R$ {subtotal_orc:.2f}*\n\nPodemos confirmar sua encomenda?"
            st.code(msg_zap)
            st.success("Mensagem gerada com sucesso! Copie acima e mande no WhatsApp da cliente.")
