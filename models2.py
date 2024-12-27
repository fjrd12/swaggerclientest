""""
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

checkpoint = "distilbert-base-uncased-finetuned-sst-2-english"
tokenizer = AutoTokenizer.from_pretrained(checkpoint)
model = AutoModelForSequenceClassification.from_pretrained(checkpoint)
sequences = ["I've been waiting for a HuggingFace course my whole life.", "So have I!"]

tokens = tokenizer(sequences, padding=True, truncation=True, return_tensors="pt")
output = model(**tokens)

print(output.logits)
print(tokens)

from datasets import load_dataset

raw_datasets = load_dataset("glue", "mrpc")
print(raw_datasets["train"][87])

"""
from langchain_community.document_loaders import TextLoader # Text loader
from langchain.text_splitter import CharacterTextSplitter # Text splitter
from langchain_community.embeddings import OllamaEmbeddings # Ollama embeddings
import weaviate # Vector database
from weaviate.embedded import EmbeddedOptions # Vector embedding options
from langchain.prompts import ChatPromptTemplate # Chat prompt template
from langchain_community.chat_models import ChatOllama # ChatOllma chat model
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser # Output parser
from langchain_community.vectorstores import Weaviate # Vector database
import requests

# downloading file
url = "https://arxiv.org/pdf/2307.06435"
res = requests.get(url)
with open("2307.06435.pdf", "w") as f:
    f.write("local.txt")

# loading file
loader = TextLoader('./local.txt')
documents = loader.load()

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
chunks = text_splitter.split_documents(documents)

client = weaviate.Client(
    embedded_options=EmbeddedOptions()
)

vectorstore = Weaviate.from_documents(
    client=client,
    documents=chunks,
    embedding=OllamaEmbeddings(model="llama3"),
    by_text=False
)

# retriever
retriever = vectorstore.as_retriever()

# LLM prompt template
template = """Hello I am a Dish Network Wireless automation assistant! How i can help you?. 
   Question: {question} 
   Context: {context} 
   Answer:
   """
prompt = ChatPromptTemplate.from_template(template)

llm = ChatOllama(model="llama3", temperature=0.2)
rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()} # context window
        | prompt
        | llm
        | StrOutputParser()
)
# begin to query and get feedback from specific knowledge 
query = "What did this paper mainly talk?"
print(rag_chain.invoke(query))