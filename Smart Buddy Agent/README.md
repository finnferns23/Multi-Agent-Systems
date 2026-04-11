# Smart Study Buddy

Smart Study Buddy is an AI-powered multi-tool assistant designed to help users study and solve problems efficiently. It leverages **LangChain**, **OpenAI GPT models**, and **Tavily search** to provide intelligent answers, perform calculations, and fetch relevant information from the web.

---

## Features

- **Intelligent Q&A:** Uses GPT-4o-mini to respond to user queries.
- **Web Search Tool:** Fetches real-time search results using Tavily.
- **Calculator Tool:** Performs basic arithmetic operations (add, subtract, multiply, divide).
- **Memory & Graph State:** Maintains a conversation history for context-aware responses.
- **Dynamic Tool Selection:** Decides when to answer directly or call an external tool.

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/finnferns23/Smart-Study-Buddy.git
cd Smart-Study-Buddy
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory:

```bash
OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key
```

---

## Usage

Run the agent with a simple script:

```bash
python main.py
```

Example questions:

- `What will be the result of multiplying 345 by 5?`
- `Who is the current President of India?`

The agent will intelligently decide whether to answer directly or call the appropriate tool.

---

## File Structure

```
.
├── main.py                 # Core agent script
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── .env                    # Environment variables (API keys)
└── tools/                  # Optional folder for custom tools
```

---

## Dependencies

- Python 3.10+
- [LangChain](https://www.langchain.com)
- [OpenAI](https://platform.openai.com)
- [Tavily](https://tavily.ai)
- Logging, typing, dotenv

---

## Contributing

1. Fork the repository.
2. Create a new branch for your feature/fix.
3. Submit a pull request.

---

## License

MIT License © 2025
