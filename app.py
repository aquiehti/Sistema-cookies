import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64

# Configuração da página
st.set_page_config(
    page_title="Doces da Mel - Gestão & Orçamentos",
    page_icon="🍪",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CSS CUSTOMIZADO PARA ESTILO APP MOBILE ---
st.markdown("""
<style>
    .main {
        background-color: #fcf6f2;
    }
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        background-color: #d97706;
        color: white;
        font-weight: bold;
        height: 48px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #b45309;
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

# Função para formatar valores no padrão brasileiro (R$ X,XX)
def fmt_rs(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

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
        {"Sabor": "Cookie Tradicional", "Ingrediente": "Farinha de Trigo", "Qtd Usada": 250.0},
        {"Sabor": "Cookie Tradicional", "Ingrediente": "Manteiga sem Sal", "Qtd Usada": 150.0},
        {"Sabor": "Cookie Tradicional", "Ingrediente": "Açúcar Mascavo", "Qtd Usada": 100.0},
        {"Sabor": "Cookie Tradicional", "Ingrediente": "Gotas de Chocolate", "Qtd Usada": 200.0},
        {"Sabor": "Cookie Tradicional", "Ingrediente": "Ovos", "Qtd Usada": 1.0},
    ])

if "precos_praticados" not in st.session_state:
    st.session_state.precos_praticados = {
        "Cookie Tradicional": 5.50
    }

if "rendimentos" not in st.session_state:
    st.session_state.rendimentos = {
        "Cookie Tradicional": 12
    }

st.title("🍪 Doces da Mel")
st.markdown("##### Sistema de Custos, Precificação & Orçamentos")
st.markdown("---")

# Navegação em Abas (Insumos renomeado para Estoque)
aba1, aba2, aba3, aba4 = st.tabs(["📦 Estoque", "📖 Receitas", "💰 Precificação", "📄 Orçamento"])

# --- ABA 1: ESTOQUE & ALERTA DE ABAIXO DE 2 RECEITAS ---
with aba1:
    st.subheader("📦 Controle de Estoque")
    st.markdown("Atualize o preço pago na última compra. O sistema avisa se o ingrediente estiver acabando (menos de 2 receitas possíveis).")
    
    with st.form("form_insumo", clear_on_submit=True):
        st.markdown("#### Adicionar / Atualizar Item")
        nome_ing = st.text_input("Nome do Ingrediente (ex: Farinha, Chocolate, Embalagem)")
        unidade_ing = st.selectbox("Unidade de Medida", ["g", "ml", "un"])
        qtd_emb = st.number_input("Quantidade na Embalagem (ex: 1000 para 1kg, 12 para ovos)", min_value=0.01, value=1000.0)
        preco_compra = st.number_input("Preço Pago na Última Compra (R$)", min_value=0.01, value=10.0)
        
        btn_salvar_ing = st.form_submit_button("Salvar no Estoque")
        if btn_salvar_ing and nome_ing:
            df_ins = st.session_state.insumos
            if nome_ing in df_ins["Ingrediente"].values:
                df_ins.loc[df_ins["Ingrediente"] == nome_ing, ["Unidade", "Qtd Embalagem", "Preço Última Compra (R$)"]] = [unidade_ing, qtd_emb, preco_compra]
                st.success(f"Item '{nome_ing}' atualizado com sucesso!")
            else:
                novo_reg = pd.DataFrame([{"Ingrediente": nome_ing, "Unidade": unidade_ing, "Qtd Embalagem": qtd_emb, "Preço Última Compra (R$)": preco_compra}])
                st.session_state.insumos = pd.concat([df_ins, novo_reg], ignore_index=True)
                st.success(f"Item '{nome_ing}' adicionado ao estoque!")

    st.markdown("### 📋 Seus Itens em Estoque")
    
    # Calcular quanto cada ingrediente gasta por receita em média para estimar quantas receitas restam
    for _, row in st.session_state.insumos.iterrows():
        ing_nome = row["Ingrediente"]
        qtd_total_est = row["Qtd Embalagem"] # Simulador simplificado de saldo unitário de embalagem
        custo_unit_base = row["Preço Última Compra (R$)"] / row["Qtd Embalagem"] if row["Qtd Embalagem"] > 0 else 0
        
        # Verificar gasto médio nas receitas
        uso_nas_receitas = st.session_state.receitas[st.session_state.receitas["Ingrediente"] == ing_nome]
        
        with st.container():
            col_e1, col_e2 = st.columns([3, 1])
            
            # Alerta se estiver acabando (menos de 2 receitas)
            alerta_html = ""
            if not uso_nas_receitas.empty:
                gasto_medio = uso_nas_receitas["Qtd Usada"].mean()
                receitas_possiveis = qtd_total_est / gasto_medio if gasto_medio > 0 else 99
                if receitas_possiveis < 2:
                    alerta_html = f"<br><span style='color: red; font-weight: bold;'>⚠️ ATENÇÃO: Só tem estoque para menos de 2 receitas!</span>"
            
            col_e1.markdown(f"""
            **{ing_nome}** ({row['Unidade']})  
            *Embalagem:* {row['Qtd Embalagem']} {row['Unidade']} | *Última Compra:* {fmt_rs(row['Preço Última Compra (R$)'])}  
            ⚡ *Custo por {row['Unidade']}:* {fmt_rs(custo_unit_base)}{alerta_html}
            """, unsafe_allow_html=True)
            
            if col_e2.button("🗑️", key=f"del_ing_{ing_nome}"):
                st.session_state.insumos = st.session_state.insumos[st.session_state.insumos["Ingrediente"] != ing_nome]
                st.rerun()
            st.divider()

# --- ABA 2: RECEITAS ---
with aba2:
    st.subheader("📖 Ficha Técnica de Receitas")
    st.markdown("Monte e estruture suas receitas selecionando os itens do seu estoque.")
    
    with st.form("form_receita", clear_on_submit=True):
        sabor_nome = st.text_input("Nome do Sabor do Cookie (ex: Red Velvet)")
        ing_disponiveis = st.session_state.insumos["Ingrediente"].tolist()
        
        if not ing_disponiveis:
            st.warning("Cadastre itens no estoque primeiro!")
        else:
            ing_sel = st.selectbox("Selecionar Item do Estoque", ing_disponiveis)
            qtd_usada_rec = st.number_input("Quantidade usada na fornada", min_value=0.01, value=50.0)
            rendimento_fornada = st.number_input("Quantos cookies essa fornada rende?", min_value=1, value=12)
            
            btn_add_receita = st.form_submit_button("Adicionar à Receita")
            if btn_add_receita and sabor_nome:
                st.session_state.rendimentos[sabor_nome] = rendimento_fornada
                nova_linha = pd.DataFrame([{"Sabor": sabor_nome, "Ingrediente": ing_sel, "Qtd Usada": qtd_usada_rec}])
                st.session_state.receitas = pd.concat([st.session_state.receitas, nova_linha], ignore_index=True)
                st.success(f"Item adicionado à receita de {sabor_nome}!")

    st.markdown("### 🍳 Receitas Cadastradas")
    sabores_cadastrados = st.session_state.receitas["Sabor"].unique()
    for sabor in sabores_cadastrados:
        with st.expander(f"🍪 Sabor: {sabor} (Rendimento: {st.session_state.rendimentos.get(sabor, 12)} un)"):
            itens_sabor = st.session_state.receitas[st.session_state.receitas["Sabor"] == sabor]
            st.dataframe(itens_sabor, use_container_width=True)
            
            if st.button(f"Excluir Receita '{sabor}'", key=f"del_rec_{sabor}"):
                st.session_state.receitas = st.session_state.receitas[st.session_state.receitas["Sabor"] != sabor]
                st.rerun()

# --- ABA 3: PRECIFICAÇÃO & MARGEM (%) ---
with aba3:
    st.subheader("💰 Precificação & Margem (%)")
    st.markdown("Defina o **Preço Praticado**. Acompanhe o lucro em Reais e a porcentagem real da sua margem!")
    
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
        col_m1.metric("Custo Produção Unitário", fmt_rs(custo_unitario))
        col_m2.metric("Preço Sugerido (Sist.)", fmt_rs(sugerido_padrao))
        
        preco_atual = st.session_state.precos_praticados[sabor]
        novo_preco_praticado = st.number_input(
            f"Preço Praticado por Unidade (R$) - {sabor}", 
            min_value=0.01, 
            value=float(preco_atual), 
            step=0.10,
            key=f"preco_praticado_{sabor}"
        )
        st.session_state.precos_praticados[sabor] = novo_preco_praticado
        
        lucro_unitario = novo_preco_praticado - custo_unitario
        margem_percentual = (lucro_unitario / novo_preco_praticado) * 100 if novo_preco_praticado > 0 else 0
        
        if margem_percentual < 30:
            alerta = "⚠️ Margem Baixa"
        elif margem_percentual < 50:
            alerta = "✅ Boa Margem"
        else:
            alerta = "🔥 Excelente Margem"
            
        st.markdown(f"""
        * **Lucro por Unidade:** {fmt_rs(lucro_unitario)}
        * **Margem de Lucro Real:** **{margem_percentual:.1f}%** ({alerta})
        """)
        st.divider()

# --- ABA 4: ORÇAMENTO & PDF ---
with aba4:
    st.subheader("📄 Gerador de Orçamento em PDF")
    st.markdown("Monte o pedido e gere um PDF profissional para enviar no WhatsApp da cliente!")
    
    cliente_nome = st.text_input("Nome da Cliente", value="Maria da Silva")
    
    sabores_disponiveis = list(st.session_state.precos_praticados.keys())
    if not sabores_disponiveis:
        st.warning("Cadastre receitas e preços primeiro!")
    else:
        sabor_orc = st.selectbox("Sabor do Cookie", sabores_disponiveis, key="orc_sabor")
        qtd_orc = st.number_input("Quantidade de Cookies", min_value=1, value=10, key="orc_qtd")
        
        preco_unit_venda = st.session_state.precos_praticados.get(sabor_orc, 5.00)
        subtotal_orc = qtd_orc * preco_unit_venda
        
        st.markdown("---")
        st.markdown("### 🛒 Resumo da Proposta")
        st.markdown(f"""
        * **Cliente:** {cliente_nome}
        * **Item:** {int(qtd_orc)}x Cookies de {sabor_orc}
        * **Valor Unitário:** {fmt_rs(preco_unit_venda)}
        * ### **TOTAL DO PEDIDO: {fmt_rs(subtotal_orc)}**
        """)
        
        def gerar_pdf_orcamento(cliente, sabor, qtd, preco_unit, total):
            pdf = FPDF(unit="mm", format="A5")
            pdf.add_page()
            
            pdf.set_font("helvetica", "B", 16)
            pdf.set_text_color(180, 83, 9)
            pdf.cell(0, 10, "DOCES DA MEL", 0, 1, "C")
            
            pdf.set_font("helvetica", "", 10)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 6, "Cookies Artesanais Fresquinhos", 0, 1, "C")
            pdf.ln(5)
            
            pdf.set_fill_color(252, 246, 242)
            pdf.set_font("helvetica", "B", 11)
            pdf.set_text_color(50, 50, 50)
            pdf.cell(0, 8, f" Orçamento para: {cliente}", 0, 1, "L", True)
            
            pdf.set_font("helvetica", "", 10)
            pdf.cell(0, 6, f" Validade da proposta: 7 dias", 0, 1, "L", True)
            pdf.ln(5)
            
            pdf.set_fill_color(217, 119, 6)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("helvetica", "B", 10)
            pdf.cell(80, 8, " Descrição do Item", 1, 0, "L", True)
            pdf.cell(20, 8, " Qtd", 1, 0, "C", True)
            pdf.cell(30, 8, " Total", 1, 1, "R", True)
            
            pdf.set_font("helvetica", "", 10)
            pdf.set_text_color(50, 50, 50)
            pdf.cell(80, 8, f" Cookie - {sabor}", 1, 0, "L")
            pdf.cell(20, 8, f"{qtd}", 1, 0, "C")
            pdf.cell(30, 8, f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), 1, 1, "R")
            
            pdf.ln(5)
            
            pdf.set_font("helvetica", "B", 12)
            pdf.set_text_color(180, 83, 9)
            pdf.cell(100, 10, "VALOR TOTAL:", 0, 0, "R")
            pdf.cell(30, 10, f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), 0, 1, "R")
            
            pdf.ln(10)
            pdf.set_font("helvetica", "I", 9)
            pdf.set_text_color(120, 120, 120)
            pdf.cell(0, 6, "Obrigada pela preferência! Feche seu pedido com antecedência.", 0, 1, "C")
            
            return pdf.output()

        if st.button("📥 Baixar Orçamento em PDF"):
            pdf_bytes = gerar_pdf_orcamento(cliente_nome, sabor_orc, int(qtd_orc), preco_unit_venda, subtotal_orc)
            b64 = base64.b64encode(pdf_bytes).decode('utf-8')
            href = f'<a href="data:application/pdf;base64,{b64}" download="Orcamento_Doces_da_Mel.pdf" target="_blank" style="display: inline-block; padding: 12px 20px; background-color: #22c55e; color: white; text-align: center; border-radius: 12px; text-decoration: none; font-weight: bold; width: 100%;">📄 Clique aqui para baixar o PDF Pronto!</a>'
            st.markdown(href, unsafe_allow_html=True)
            st.success("PDF gerado com sucesso!")
