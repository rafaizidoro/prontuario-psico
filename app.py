import streamlit as st
import google.generativeai as genai
from datetime import datetime

# Configuração da página - Deve ser a primeira coisa no Streamlit
st.set_page_config(page_title="Assistente de Prontuário", layout="centered")

st.title("📝 Assistente de Prontuário Clínico")

# --- GERENCIAMENTO SEGURO DA API KEY ---
try:
    gemini_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-3.1-flash-lite')
    api_pronta = True
except Exception as e:
    st.error("Erro na configuração da API Key. Verifique as configurações de Secrets.")
    api_pronta = False

# --- LÓGICA DA APLICAÇÃO ---
if api_pronta:
    # Interface principal
    paciente_ref = st.text_input("Nome / Iniciais / Referência do Paciente", placeholder="Ex: F.B./Paciente A")
    placeholder_notas = (
    "1. Como o(a) paciente chegou e qual foi a demanda central trazida hoje?\n"
    "2. Quais técnicas, manejos ou intervenções você utilizou para abordar essa demanda?\n"
    "3. Quais padrões foram observados ou combinados ficaram para as próximas sessões?"
    )
    anotacoes = st.text_area(
    "Digite as notas da sessão aqui:", 
    height=250, 
    placeholder=placeholder_notas
    )

    if st.button("Gerar Prontuário Estruturado"):
        if anotacoes:
            with st.spinner("O Gemini está analisando e estruturando o prontuário..."):
                try:
                    # Captura a data atual formatada (DD/MM/AAAA)
                    data_atual = datetime.now().strftime("%d/%m/%Y")
                    
                    # Se o profissional não preencher o nome, define como "Não informado"
                    nome_cliente = paciente_ref.strip() if paciente_ref else "Não informado"

                    prompt_completo = f"""
                    Atue como um Assistente de Escrita Clínica para Psicólogos. Sua tarefa é converter as notas de sessão fornecidas pelo profissional em um prontuário técnico, ético e extremamente enxuto, seguindo rigorosamente a estrutura abaixo.
                    
                    Você DEVE obrigatoriamente iniciar o seu output com o cabeçalho exatamente no formato abaixo, preenchendo os campos 'Cliente' e 'Data' com as informações fornecidas, e mantendo os colchetes '[completar]' nos outros campos para preenchimento posterior pelo psicólogo.
                    
                    Cabeçalho Obrigatório:
                    ANOTAÇÕES CLÍNICAS DE ATENDIMENTO
                    Cliente: {nome_cliente}
                    Data: {data_atual}
                    Horário: [completar]
                    Sessão nº: [completar]
                    Modalidade: [completar: presencial, online, etc.]
                    
                    Diretrizes de Escrita:
                    - Tom Profissional: Use uma linguagem técnica (ex: em vez de "fugir", use "esquiva").
                    - Neutralidade: Não invente diagnósticos ou sentimentos que não foram descritos.
                    - Concisão: Mantenha cada parágrafo curto. Se uma informação não estiver nas notas, use termos genéricos como "não reportado" ou apenas foque no que existe.
                    - Flexibilidade de Gênero: Adapte o gênero (o/a cliente) conforme as notas, ou use termos neutros como "Paciente".
                    
                    Estrutura do Restante do Output (pule uma linha após o cabeçalho):
                    
                    Desenvolvimento da Sessão:
                    [Descreva o estado inicial/postura se houver na nota, ou inicie diretamente com o tema trazido. Relate o conteúdo central trabalhado de forma resumida e clinicamente relevante].
                    
                    Manejo e Intervenções:
                    [Descreva a postura técnica adotada (escuta, acolhimento, análise funcional) e quais intervenções foram realizadas com base no relato].
                    
                    Pontos Relevantes para a Continuidade:
                    [Registre padrões observados, dificuldades ou combinados para o futuro].
                    
                    Notas para processar: {anotacoes}
                    """
                    
                    response = model.generate_content(prompt_completo)
                    
                    st.success("Prontuário Gerado com Sucesso!")
                    st.markdown("---")
                    st.markdown(response.text)
                    st.markdown("---")
                    
                    # Nome do arquivo amigável para download
                    nome_arquivo = nome_cliente.replace(" ", "_")
                    
                    st.download_button(
                        label="📥 Baixar Prontuário (TXT)",
                        data=response.text,
                        file_name=f"prontuario_{nome_arquivo}_{data_atual.replace('/', '-')}.txt",
                        mime="text/plain"
                    )
                except Exception as e:
                    st.error(f"Erro ao processar a requisição: {e}")
        else:
            st.warning("⚠️ Por favor, insira as anotações da sessão antes de gerar.")