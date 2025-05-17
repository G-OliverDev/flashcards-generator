import os
import warnings
from google import genai
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types

os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY"
warnings.filterwarnings("ignore")

def call_agent(agent: Agent, message_text: str) -> str:
    session_service = InMemorySessionService()
    session = session_service.create_session(app_name=agent.name, user_id="user1", session_id="session1")
    runner = Runner(agent=agent, app_name=agent.name, session_service=session_service)
    content = types.Content(role="user", parts=[types.Part(text=message_text)])

    final_response = ""
    for event in runner.run(user_id="user1", session_id="session1", new_message=content):
        if event.is_final_response() and event.content is not None:
          for part in event.content.parts:
            if part.text is not None:
              final_response += part.text
              final_response += "\n"
    return final_response

def agente_pesquisador(frase, palavra):
    pesquisador = Agent(
        name="agente_pesquisador",
        model="gemini-2.0-flash",
        tools=[google_search],
        instruction="""
        Você é um assistente de pesquisa de palavras e expressões em inglês. A sua tarefa é pesquisar
        a definição da palavra ou expressão usando a ferramenta de busca do Google (google_search).
        Se a palavra ou expressão em questão possuir múltiplas definições, escolha a definição que mais se
        adequa ao contexto da frase.
        Sua pesquisa deve incluir a tradução da palavra ou expressão em português, sua definição em inglês, assim como outras frases de exemplo com essa palavra ou expressão dentro do mesmo contexto da frase original.
        """,
        description="Agente que busca significados de palavras ou expressões em inglês no Google"
    )
    
    entrada_do_agente_pesquisador = f"Frase: {frase}\nPalavra: {palavra}"
    pesquisa = call_agent(pesquisador, entrada_do_agente_pesquisador)
    
    return pesquisa

def agente_professor(frase, palavra, pesquisa):
    professor = Agent(
        name="agente_professor",
        model="gemini-2.0-flash",
        tools=[google_search],
        instruction="""
        Você é um professor de inglês. A sua tarefa é elaborar um flashcard com base na pesquisa realizada,
        de acordo com o formato a seguir. Vou te dar um exemplo para você entender qual o formato que eu quero:
        - "FRENTE DO CARTÃO" (contendo a frase em inglês e a palavra ou expressão em destaque)
        - "VERSO DO CARTÃO" (contendo a palavra ou expressão, sua definição em inglês, sua tradução em português e 
        três exemplos adicionais)
        
        #####
        
        Frase: Our camping trip was spoilt by bad weather.
        Palavra: spoilt
        
        FRENTE DO CARTÃO:
        
        Our camping trip was <b>spoilt</b> by bad weather.
        
        ------
        
        VERSO DO CARTÃO:
        
        <b>spoilt</b><br><br>
        <b>Definition:</b> to change something good into something bad, unpleasant, etc.<br><br>
        <b>Translation:</b> arruinado, estragado, prejudicado<br><br>
        <b>Additional examples:</b><br> 
        The bad weather spoilt our picnic. (O mau tempo estragou nosso piquenique.)<br>
        The oil spill has spoilt the whole beautiful coastline. (O vazamento de óleo estragou toda a bela costa.)<br>
        Don't let one mistake spoil your day. (Não deixe que um erro estrague o seu dia.)<br>
        
        #####
        
        Fique à vontade para reescrever a definição da palavra em inglês de maneira mais simples, direcionada a
        estudantes de inglês. Utilize exemplos curtos que não são muito complicados.
        """,
    )
    
    entrada_do_agente_professor = f"Frase: {frase}\nPalavra: {palavra}\nPesquisa: {pesquisa}"
    flashcard = call_agent(professor, entrada_do_agente_professor)
    
    return flashcard

def gerar_flashcard(texto, nome_arquivo):
    try:
        os.makedirs("flashcards", exist_ok=True)
        caminho_arquivo = os.path.join("flashcards", nome_arquivo)
        
        with open(caminho_arquivo, 'w', encoding='utf-8') as arquivo:
            arquivo.write(texto)
        print(f"\nFlashcard {nome_arquivo} gerado com sucesso!\n")
    except Exception as e:
        print(f"Ocorreu um erro ao criar o arquivo: {e}")
    

print("--------------- GERADOR DE FLASHCARDS ---------------")
print("Bem-vindo ao gerador de flashcards.\nDigite uma frase em inglês e uma palavra ou expressão dessa frase a qual deseja gerar um flashcard.")
print("-----------------------------------------------------\n")
while True:
    frase = input("Frase: ")
    palavra = input("Palavra: ")
    
    pesquisa = agente_pesquisador(frase, palavra)
    flashcard = agente_professor(frase, palavra, pesquisa)
    
    nome_arquivo = palavra.replace(' ', '-') + ".md"
    gerar_flashcard(flashcard, nome_arquivo)
    
    print("Deseja criar mais flashcards? Digite 'SAIR' para encerrar o programa ou aperte ENTER para continuar.")
    resposta = input()
    if (resposta.upper() == 'SAIR'):
        break
