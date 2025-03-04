# councillm

Query multiple LLMs simultaneously with the same prompts.

councillm is a FastHTML application that lets you pose the same question to several different Large Language Models at once, allowing you to easily see how different models respond to identical prompts.

It optionally can log the responses to a local SQLite database (due to using Simon Willison's excellent 'llm' module), so that you can search them later.

## What does it do?

- Send a single prompt to multiple LLMs simultaneously
- Shows you all responses headed by the LLM model name for easy comparison
- Allows you to Include (or Exclude) each model each time you prompt
- Adds newer responses above older ones
- Allows you to copy a response as rich text, or download as markdown text
- Allows you to download a conversation with any of those LLMs as markdown text

There is also a marimo notebook that you can run locally to have logged chats with individual LLMs, or to search the data logged to the database.

## Screenshots

### The Council:
![CounciLLM interface showing multiple LLM responses in parallel](screenshots/CounciLLM.png)

### Marimo Notebook:
![Marimo notebook interface for chatting with individual LLMs](screenshots/multichat.png)

## Quick start

Assuming you are starting in the folder where you downloaded councillm, you can start the app this way:

(Or if on Windows, `start_app.bat`)

Then visit http://localhost:5001 in your browser.

Both start_app scripts allow you to input some options if you want to adjust these defaults:


If you want to start the marimo notebook:
(Or if on Windows, `start_mo.bat`)

Marimo will also start a browser window with the notebook open.


## Configure your models

councillm needs API keys for the models you want to query.

EITHER set them as environment variables, like so in bash:


OR set them via the `llm` command line:
`uvx llm keys set openai`
(when prompted, enter your OpenAI API key)
`uvx llm keys set anthropic`
(similar, but for Anthropic)
... and so on

## Development

This project was built with [nbdev](https://nbdev.fast.ai/). To contribute, please remember to set up your local git using `nbdev_install_hooks` and to edit the code in the notebook rather than the code in the councillm folder.

## License

Apache2


