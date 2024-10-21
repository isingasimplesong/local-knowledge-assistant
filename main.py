import base64
import hashlib
import json
import os

import streamlit as st
import yaml
from llama_index.core import (
    PromptTemplate,
    Settings,
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)

DATA_DIR = "./data"
INDEX_DIR = "./storage"
TEMPLATE_FILE = "./template.txt"
MESSAGES_FILE = "./messages.json"
UI_CONFIG_FILE = "./ui.json"
CONFIG_FILE = "./config.yaml"


def load_config(config_file):
    """
    Load the configuration from a YAML file and expand environment variables.
    """
    with open(config_file, "r") as f:
        config_str = f.read()
        config_str = os.path.expandvars(config_str)
        config = yaml.safe_load(config_str)
    return config


config = load_config(CONFIG_FILE)

# Access API keys
api_keys = config.get("api_keys", {})
openai_api_key = api_keys.get("openai_api_key")
groq_api_key = api_keys.get("groq_api_key")
ollama_api_key = api_keys.get("ollama_api_key")

# Set environment variables or handle API keys as needed
if openai_api_key:
    os.environ["OPENAI_API_KEY"] = openai_api_key
if groq_api_key:
    os.environ["GROQ_API_KEY"] = groq_api_key
if ollama_api_key:
    os.environ["OLLAMA_API_KEY"] = ollama_api_key

# Embedding setup
embedding_provider = config.get("embedding_provider", "default")
if embedding_provider == "huggingface":
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding

    embedding_name = config.get("embedding_name")
    if not embedding_name:
        raise ValueError(
            "Embedding name must be specified for Hugging Face embeddings."
        )
    EMBED_MODEL = HuggingFaceEmbedding(model_name=embedding_name)
    Settings.embed_model = EMBED_MODEL
elif embedding_provider == "default":
    # Use default embedding (e.g., OpenAI)
    pass
else:
    raise ValueError(f"Unsupported embedding_provider: {embedding_provider}")

from llama_index.llms.groq import Groq
from llama_index.llms.ollama import Ollama

# LLM setup
from llama_index.llms.openai import OpenAI

llm_classes = {"openai": OpenAI, "ollama": Ollama, "groq": Groq}
llm_provider = config.get("llm_provider")
llm_class = llm_classes.get(llm_provider)

if llm_class is None:
    raise ValueError(f"Unsupported llm_provider: {llm_provider}")

llm_params = config.get("llm_parameters", {})
llm = llm_class(model=config["llm_model_name"], **llm_params)

Settings.llm = llm


def compute_data_version(data_dir):
    """Compute a hash representing the current state of data_dir."""
    hash_md5 = hashlib.md5()
    for root, _, files in os.walk(data_dir):
        for filename in sorted(files):
            filepath = os.path.join(root, filename)
            # Include file modification time and size
            file_stats = os.stat(filepath)
            hash_md5.update(str(file_stats.st_mtime).encode())
            hash_md5.update(str(file_stats.st_size).encode())
            hash_md5.update(filepath.encode())
    return hash_md5.hexdigest()


@st.cache_data
def load_index(data_version):
    if not os.path.exists(INDEX_DIR):
        documents = SimpleDirectoryReader(DATA_DIR, recursive=True).load_data()
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=INDEX_DIR)
    else:
        storage_context = StorageContext.from_defaults(persist_dir=INDEX_DIR)
        index = load_index_from_storage(storage_context)
    return index


# compute date version and load index
data_version = compute_data_version(DATA_DIR)
index = load_index(data_version)


def prepare_template(template_file):
    """
    Load the prompt template
    """
    with open(template_file, "r") as f:
        text_qa_template_str = f.read()
    qa_template = PromptTemplate(text_qa_template_str)
    return qa_template


def load_messages(messages_file):
    """
    Load UI messages
    """
    with open(messages_file, "r") as f:
        messages = json.load(f)
    return messages


def load_ui_config(ui_config_file):
    """
    Load the UI configuration from an external JSON file.
    """
    with open(ui_config_file, "r") as f:
        ui_config = json.load(f)
    return ui_config


def load_logo_as_base64(logo_path):
    """
    Load an image and convert it to a base64 string.
    """
    with open(logo_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")
    return f"data:image/png;base64,{base64_image}"


# Load UI conf, logo & messages
ui_config = load_ui_config(UI_CONFIG_FILE)
ui_messages = load_messages(MESSAGES_FILE)
logo_base64 = load_logo_as_base64(ui_config["logo_path"])

st.markdown(
    ui_config["html_template"].format(logo=logo_base64),
    unsafe_allow_html=True,
)

# Initialize session state messages if not already present
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": ui_messages["greeting"]}
    ]


def get_conversation_history():
    """
    Prepare the conversation history to provide context to the model.
    """
    history = ""
    for message in st.session_state.messages:
        role = "User" if message["role"] == "user" else "Assistant"
        history += f"{role}: {message['content']}\n"
    return history


# Capture user input and append it to session state messages
if prompt := st.chat_input(ui_messages["user_input_placeholder"]):
    st.session_state.messages.append({"role": "user", "content": prompt})

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

qa_template = prepare_template(TEMPLATE_FILE)
query_engine = index.as_query_engine(text_qa_template=qa_template, similarity_top_k=2)

# Add conversation history to context
conversation_history = get_conversation_history()
full_prompt = f"{conversation_history}User: {prompt}"

if st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner(ui_messages["wait_spinner"]):
            response = query_engine.query(full_prompt)
        st.markdown(response.response, unsafe_allow_html=True)
        st.session_state.messages.append(
            {"role": "assistant", "content": response.response}
        )
