# Local Knowledge assistant

<p align="center">
  <img src="screenshot.png" alt="lka screenshot"/>
</p>

## Features

- Provides an easy way to deploy a chatbot for chatting with your own data
- Let you configure and/or translate UI messages and llm prompt

## Installation

### Linux

```bash
git clone https://github.com/isingasimplesong/local-knowledge-assistant.git
cd local-knowledge-assistant
# put your data in data/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export GROQ_API_KEY=<YOUR_API_KEY>
streamlit run main.py
```

### Mac

> [!warning]
> Untested. Please profide feedback if you try

Linux instructions should work

### Windows

Use `powershell`

> [!warning]
> Untested. Please profide feedback if you try

```powershell
git clone https://github.com/isingasimplesong/local-knowledge-assistant.git
cd local-knowledge-assistant
# Put your data in the data/ directory
python -m venv venv
.\venv\Scripts\Activate  # Note: Use `deactivate` to exit the environment when done
pip install -r requirements.txt
$env:GROQ_API_KEY="<YOUR_API_KEY>"  # This will only last for this session; consider adding it to your profile
streamlit run main.py

```

## Configuration

- Get a [groq API key here](https://console.groq.com/) to get the assistant running *as is*
- Or adjust the script and run it with OpenAI, a local llama model, or anything else
  - When running it with OpenAI API, you can completly comment the embedding
    model configuration, it will default to OpenAI's embedding model
- you can change or translate the prompt sent to the model in `template.txt`,
- you can change or translate UI messages in `messages.json`,
- you can configure the Chatbot UI in `ui.json`
- **The first run is expected to be slow :** The embedding model need to index
  all of your data

## Roadmap

- Provide a simpler way to change llm & embedding models
- Provide a docker image for easy deployment
