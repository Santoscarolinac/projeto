import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# ============ FUNÇÃO CET ============ #
def calcular_cet(entrada, valor_parcela, prazo):
    """
    Cálculo estimado da CET mensal com base no valor de entrada,
    parcela mensal e prazo (em meses).
    """
    total_pago = valor_parcela * prazo
    if entrada <= 0 or prazo <= 0:
        return 0
    cet_mensal = ((total_pago / entrada) ** (1 / prazo)) - 1
    return cet_mensal * 100


# ============ CONEXÃO COM FIREBASE ============ #
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_config.json")  # Certifique-se de ter esse arquivo na mesma pasta
    firebase_admin.initialize_app(cred)

db = firestore.client()


# ============ INTERFACE STREAMLIT ============ #
st.set_page_config(page_title="Calculadora CET", layout="centered")
st.title("📊 Calculadora CET (Cliente Firebase)")

# Carregar lista de clientes
clientes_ref = db.collection("clientes").limit(100)
clientes_docs = clientes_ref.stream()
clientes = [c.to_dict() for c in clientes_docs]

if not clientes:
    st.warning("Nenhum cliente encontrado no banco de dados.")
    st.stop()

# Selecionar cliente
nomes = [cliente['nome'] for cliente in clientes]
nome_selecionado = st.selectbox("Selecione um cliente:", nomes)

# Buscar cliente selecionado
cliente = next((c for c in clientes if c['nome'] == nome_selecionado), None)

if cliente:
    st.subheader("📌 Dados do cliente")
    st.write(f"**CPF:** {cliente['cpf']}")
    st.write(f"**Data de nascimento:** {cliente['data_nascimento']}")
    st.write(f"**Profissão:** {cliente['profissao']}")
    st.write(f"**Empresa:** {cliente['nome_empresa']}")
    st.write(f"**Renda mensal:** R$ {cliente['renda_mensal']:,.2f}")
    st.write(f"**Entrada:** R$ {cliente['entrada']:,.2f}")
    st.write(f"**Prazo:** {cliente['prazo']} meses")
    st.write(f"**Instituição:** {cliente['instituicao_financeira']}")
    st.write("---")

    # Simular valor da parcela
    valor_parcela = st.number_input(
        "💵 Valor da parcela mensal (ex: simulação do banco)",
        min_value=0.0, step=50.0, format="%.2f"
    )

    if st.button("Calcular CET"):
        cet = calcular_cet(cliente['entrada'], valor_parcela, cliente['prazo'])
        st.success(f"📈 CET mensal estimada: **{cet:.2f}%**")
else:
    st.error("Cliente não encontrado.")
