# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "duckdb",
#     "llm==0.22",
#     "llm-anthropic",
#     "llm-gemini",
#     "llm-groq",
#     "marimo",
#     "numpy",
#     "openpyxl",
#     "pandas==2.2.3",
#     "pyarrow",
#     "sqlglot==26.6.0",
#     "sqlite-utils==3.38",
# ]
# ///

import marimo

__generated_with = "0.11.13"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import llm
    return llm, mo


@app.cell
def _():
    # llm.get_models()
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(llm, mo):
    import os
    import sqlite_utils
    from pathlib import Path

    def get_llm_db():
        if os.environ.get("LLM_USER_PATH") is not None:
            return sqlite_utils.Database(Path(os.environ["LLM_USER_PATH"]) / "logs.db")
        else:
            return sqlite_utils.Database(llm.user_dir() / "logs.db")

    def logged_chat(model, system_prompt=None):
        m = llm.get_model(model)
        c = m.conversation()

        def chat_with_logging(messages):
            response = c.prompt(messages[-1].content, system=system_prompt)
            response.log_to_db(get_llm_db())
            return str(response)

        chat = mo.ui.chat(chat_with_logging)
        return chat

    mo.md(f"""## GPT 4o
    {logged_chat("gpt-4o")}
    """)
    return Path, get_llm_db, logged_chat, os, sqlite_utils


@app.cell
def _(logged_chat):
    x = logged_chat("gemini-2.0-flash-exp")
    dir(x)
    return (x,)


@app.cell
def _(x):
    x
    return


@app.cell
def _(x):
    help(x._send_prompt) #({'role': 'user', 'content': 'Please explain the send_message method?', 'attachments': None})
    return


@app.cell
def _(x):
    x.send_message({'content': 'Can you help me learn Spanish?'}, None)
    return


@app.cell
def _(x):
    x.value
    return


@app.cell
def _(x):
    help(x.send_message)
    return


@app.cell
def _(x):
    x.value
    return


@app.cell(hide_code=True)
def _(logged_chat, mo):
    mo.md(f"""## Claude Sonnet 3.5
    {logged_chat('anthropic/claude-3-5-sonnet-latest')}
    """)
    return


@app.cell(hide_code=True)
def _(logged_chat, mo):
    mo.md(f"""## Claude Sonnet 3.7
    {logged_chat('claude-3.7-sonnet')}
    """)
    return


@app.cell(hide_code=True)
def _(logged_chat, mo):
    mo.md(f"""## Google Gemini 2.0 flash
    {logged_chat("gemini-2.0-flash-exp")}
    """)
    return


@app.cell(hide_code=True)
def _(logged_chat, mo):
    mo.md(f"""## LLama 70b
    {logged_chat("groq-llama-3.3-70b")}
    """)
    return


@app.cell
def _(logged_chat, mo):
    mo.md(f"""## ChatGPT 4o-mini
    {logged_chat("4o-mini")}
    """)
    return


@app.cell(hide_code=True)
def _(logged_chat, mo):
    mo.md(f"""## DeepSeek R1 with LLama 70b
    {logged_chat("groq/deepseek-r1-distill-llama-70b")}
    """)
    return


@app.cell(hide_code=True)
def _(logged_chat, mo):
    mo.md(f"""## Gemini 2.0 thinking
    {logged_chat("gemini-2.0-flash-thinking-exp-01-21")}
    """)
    return


@app.cell
def _():
    # llm.get_models()
    return


@app.cell(hide_code=True)
def _(logged_chat, mo):
    mo.md(f"""## Mixtral (on groq)
    {logged_chat("groq-mixtral")}
    """)
    return


@app.cell(hide_code=True)
def _(logged_chat, mo):
    mo.md(f"""## Claude Haiku 3.5
    {logged_chat("anthropic/claude-3-5-haiku-latest")}
    """)
    return


@app.cell(hide_code=True)
def _(logged_chat, mo):
    mo.md(f"""## Deepseek Reasoner
    {logged_chat("deepseek-reasoner")}
    """)
    return


@app.cell(hide_code=True)
def _(logged_chat, mo):
    mo.md(f"""## Deepseek Chat
    {logged_chat("deepseek-chat")}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    search_text = mo.ui.text(label="Prompt or response:", placeholder="Search prompts or responses", full_width=True)
    mo.md(f"""## Search conversations
    {search_text}
    """)
    return (search_text,)


@app.cell(hide_code=True)
def _(mo, search_result):
    mo.md(f"""### latest search result
    {next(iter(search_result['response'])).replace('<think>', '### thinking >').replace('</think>', '### < thinking')}""")
    return


@app.cell(hide_code=True)
def _(llm, mo, os, search_text):
    def get_llm_db_location():
        if os.environ.get("LLM_USER_PATH") is not None:
            return os.environ["LLM_USER_PATH"] / "logs.db"
        else:
            return llm.user_dir() / "logs.db"

    query = f"""
    SELECT prompt, response, system, model 
    FROM sqlite_scan('{get_llm_db_location()}', 'responses')
    WHERE prompt LIKE '%{search_text.value}%'
    OR response LIKE '%{search_text.value}%'
    OR system LIKE '%{search_text.value}%'
    ORDER BY datetime_utc DESC
    """
    # print(query)
    search_result = mo.sql(query)
    mo.md(f"""## Full search results
    {mo.ui.table(search_result)}
    """)
    return get_llm_db_location, query, search_result


if __name__ == "__main__":
    app.run()
