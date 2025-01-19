# LLM Chess Battle

A Python application that lets Language Learning Models (LLMs) play chess against each other.

## Setup

1. Clone the repository:

```bash
git clone https://github.com/abinthomasonline/llm-chess.git
cd llm-chess
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
```


3. Install dependencies:

```bash
pip install -r requirements.txt
```


4. Create a `.env` file in the root directory and add your API keys:

```
OPENAI_API_KEY=your-openai-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here
```

## Running the Application

Start the Streamlit application:

```bash
streamlit run src/ui/app.py
```

## License

MIT License
