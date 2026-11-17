import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gestão de Cookies", page_icon="🍪", layout="centered")

# --- ESTADO DA APLICAÇÃO (DADOS INICIAIS) ---
if "insumos" not in st.session_state:
    st.session_state.insumos = pd.DataFrame([
        {"Ingrediente": "Farinha de Trigo", "Unidade": "g", "Qtd Embalagem": 1000, "Preço Pago (R$)": 5.50},
        {"Ingrediente": "Manteiga sem Sal", "Unidade": "g", "Qtd Embalagem": 500, "Preço Pago (R$)": 24.00},
        {"Ingrediente": "Açúcar Mascavo", "Unidade": "g", "Qtd Embalagem": 500, "Preço Pago (R$)": 6.50},
        {"Ingrediente": "Gotas de Chocolate", "Unidade": "g", "Qtd Embalagem": 1000, "Preço Pago (R$)": 48.00},
        {"Ingrediente": "Ovos", "Unidade": "un", "Qtd Embalagem": 12, "Preço Pago (R$)": 12.00},
    ])

if "receitas" not in st.session_state:
    st.session_state.receitas = pd.DataFrame([
        {"Sabor": "Tradicional", "Ingrediente": "Farinha de Trigo", "Qtd Usada": 250},
        {"Sabor": "Tradicional", "Ingrediente": "Manteiga sem Sal", "Qtd Usada": 150},
        {"Sabor": "Tradicional", "Ingrediente": "Açúcar Mascavo", "Qtd Usada": 100},
        {"Sabor": "Tradicional", "Ingrediente": "Gotas de Chocolate", "Qtd Usada": 200},
        {"Sabor": "Tradicional", "Ingrediente": "Ovos", "Qtd Usada": 1},
    ])

if "precos_praticados" not in st.session_state:
    # Preço customizado que ela decide cobrar
    st.session_state.precos_praticados = {
        "Tradicional": 5.50
    }

st.title("🍪 Gestão & Orçamentos - Cookies")

# Abas do App no Celular
aba1, aba2, aba3, aba4 = st.tabs(["🛒 Insumos", "📖 Receitas", "💰 Precificação", "📄 Orçamento"])

# --- ABA 1: INSUMOS ---
with aba1:
    st.subheader("Gerenciar Insumos")
    
    # Adicionar novo insumo
    with st.form("form_novo_insumo"):
        novo_ing = st.text_input("Nome do Ingrediente")
        uni_ing = st.selectbox("Unidade Base", ["g", "ml", "un"])
        qtd_emb = st.number_input("Qtd da Embalagem (ex: 1000g, 12un)", min_value=0.1, value=1000.0)
        preco_pago = st.number_input("Preço Pago na Embalagem (R$)", min_value=0.01, value=10.0)
        
        btn_add_insumo = st.form_submit_button("Adicionar Insumo")
        if btn_add_insumo and novo_ing:
            novo_df = pd.DataFrame([{"Ingrediente": novo_ing, "Unidade": uni_ing, "Qtd Embalagem": qtd_emb, "Preço Pago (R$)": preco_pago}])
            st.session_state.insumos = pd.concat([st.session_state.insumos, novo_df], ignore_index=True)
            st.success(f"Insumo '{novo_ing}' adicionado com sucesso!")

    st.write("### Lista de Insumos Cadastrados")
    st.dataframe(st.session_state.insumos, use_container_width=True)

# --- ABA 2: RECEITAS (FICHA TÉCNICA) ---
with aba2:
    st.subheader("Ficha Técnica das Receitas")
    
    with st.form("form_nova_receita"):
        sabor_receita = st.text_input("Nome do Sabor do Cookie (ex: Red Velvet)")
        ing_disponiveis = st.session_state.insumos["Ingrediente"].tolist()
        ing_escolhido = st.selectbox("Ingrediente", ing_disponiveis)
        qtd_usada = st.number_input("Quantidade usada na receita", min_value=0.01, value=50.0)
        rendimento_lote = st.number_input("Rendimento da receita (Quantos cookies rende?)", min_value=1, value=12)
        
        btn_add_rec = st.form_submit_button("Adicionar Item à Receita")
        if btn_add_rec and sabor_receita:
            nova_rec = pd.DataFrame([{"Sabor": sabor_receita, "Ingrediente": ing_escolhido, "Qtd Usada": qtd_usada}])
            st.session_state.receitas = pd.concat([st.session_state.receitas, nova_rec], ignore_index=True)
            st.success(f"Ingrediente adicionado à receita de {sabor_receita}!")

    st.write("### Itens Cadastrados nas Receitas")
    st.dataframe(st.session_state.receitas, use_container_width=True)

# --- ABA 3: PRECIFICAÇÃO & ARREDONDAMENTO ---
with aba3:
    st.subheader("Painel de Custos e Preço Praticado")
    
    # Calcular custos por sabor
    sabores = st.session_state.receitas["Sabor"].unique()
    dados_precificacao = []
    
    for sabor in sabores:
        itens_sab = st.session_state.receitas[st.session_state.receitas["Sabor"] == sabor]
        custo_total = 0
        for _, row in itens_sab.iterrows():
            ing_info = st.session_state.insumos[st.session_state.insumos["Ingrediente"] == row["Ingrediente"]]
            if not ing_info.empty:
                custo_unit_base = ing_info.iloc[0]["Preço Pago (R$)"] / ing_info.iloc[0]["Qtd Embalagem"]
                custo_total += custo_unit_base * row["Qtd Usada"]
        
        rendimento = 12 # Padrão simplificado por lote
        custo_unitario = custo_total / rendimento if rendimento > 0 else 0
        sugerido = custo_unitario * 2.85 # Markup padrão de 185% (65% margem)
        
        # Recupera preço praticado ou define o sugerido arredondado
        if sabor not in st.session_state.precos_praticados:
            st.session_state.precos_praticados[sabor] = round(sugerido, 2)
            
        dados_precificacao.append({
            "Sabor": sabor,
            "Custo Unitário (R$)": round(custo_unitario, 2),
            "Preço Sugerido (R$)": round(sugerido, 2)
        })
    
    df_prec = pd.DataFrame(dados_precificacao)
    
    # Exibe tabela iterativa para ela alterar o preço praticado
    st.write("Defina abaixo o **Preço Praticado** (arredondado para mais ou para menos):")
    
    novos_precos = {}
    for idx, row in df_prec.iterrows():
        sabor = row["Sabor"]
        col1, col2, col3 = st.columns(3)
        col1.write(f"**{sabor}**")
        col2.write(f"Custo: R$ {row['Custo Unitário (R$)']:.2f} | Sugerido: R$ {row['Preço Sugerido (R$)']:.2f}")
        
        # Campo editável para o preço praticado
        preco_atual = st.session_state.precos_praticados.get(sabor, row["Preço Sugerido (R$)"])
        praticado = col3.number_input(f"Preço Venda ({sabor})", min_value=0.01, value=float(preco_atual), key=f"preco_{sabor}")
        
        st.session_state.precos_praticados[sabor] = praticado
        
        # Calcula lucro e margem em tempo real com o preço praticado escolhido
        lucro = praticado - row["Custo Unitário (R$)"]
        margem = (lucro / praticado) * 100 if praticado > 0 else 0
        st.info(f"Lucro por unidade: **R$ {lucro:.2f}** ({margem:.1f}% de margem)")
        st.divider()

# --- ABA 4: ORÇAMENTO ---
with aba4:
    st.subheader("Gerador de Orçamento Rápido")
    cliente = st.text_input("Nome do Cliente", value="Cliente Exemplo")
    
    sabor_escolhido = st.selectbox("Escolha o Sabor", list(st.session_state.precos_praticados.keys()))
    qtd_pedida = st.number_input("Quantidade de Cookies", min_value=1, value=10)
    
    preco_venda_unit = st.session_state.precos_praticados.get(sabor_escolhido, 5.00)
    subtotal = qtd_pedida * preco_venda_unit
    
    st.markdown("---")
    st.markdown(f"### Resumo da Proposta")
    st.write(f"**Cliente:** {cliente}")
    st.write(f"**Item:** {qtd_pedida}x Cookies de {sabor_escolhido}")
    st.write(f"**Preço Unitário Praticado:** R$ {preco_venda_unit:.2f}")
    st.markdown(f"### **TOTAL DO ORÇAMENTO: R$ {subtotal:.2f}**")
    
    if st.button("Gerar Mensagem Pronta para o WhatsApp"):
        msg = f"Olá {cliente}! Segue o orçamento dos seus cookies artesanais: *{qtd_pedida}x Cookies de {sabor_escolhido}* por apenas *R$ {subtotal:.2f}* (R$ {preco_venda_unit:.2f} cada). Podemos confirmar?"
        st.code(msg)
        st.success("Copie a mensagem acima e cole direto no WhatsApp da cliente!")
