# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/app.ipynb.

# %% auto 0
__all__ = ['thread_local', 'MODELS', 'app', 'rt', 'tcs', 'ThreadConversation', 'lcs', 'get_llm_db', 'LoggedChat',
           'model_selector', 'update_model', 'toggle_model', 'toggle_logging', 'prompt_form', 'input_section',
           'display_system_prompt', 'display_user_prompt', 'download_response', 'model_header', 'message_response',
           'index']

# %% ../nbs/app.ipynb 1
from fasthtml.common import *
from monsterui.all import *
from fasthtml.jupyter import *
from fastcore.utils import *
import os
import sqlite_utils
import llm 
import os
import threading
from datetime import datetime, timedelta, timezone
from multiprocessing.pool import ThreadPool
import argparse

if not in_notebook():
    parser = argparse.ArgumentParser(description='CounciLLM - Query multiple LLMs simultaneously')
    parser.add_argument('-n', type=int, default=6, help='Number of models to query')
    parser.add_argument('--no-logging', action='store_true', help='Start with logging toggled off')
    args = parser.parse_args()
    
    # Update constants based on command line arguments
    N_MODELS = args.n
    START_WITH_LOGGING = not args.no_logging
else:
    N_MODELS = 6
    START_WITH_LOGGING = True
    
thread_local = threading.local()

MODELS = {'gpt-4o': 'gpt 4o', 'gemini-2.0-flash-thinking-exp-01-21': 'Gemini 2.0 Thinking',
          'claude-3.7-sonnet': 'Claude 3.7 Sonnet', 'deepseek-chat': 'DeepSeek Chat', 'groq-llama-3.3-70b': 'LLama 3.3 70b', 
          'claude-3.5-haiku': 'Claude 3.5 Haiku', 'deepseek-reasoner': 'Deepseek Reasoner', 'claude-3.5-sonnet': 'Claude 3.5 Sonnet', 
          'gemini-2.0-flash-exp': 'Gemini 2.0 Flash', 'gemini-2.0-pro-exp-02-05': 'Gemini 2.0 Pro', 
          'groq/deepseek-r1-distill-llama-70b': 'Groq DeepSeek LLama', 'groq-mixtral': 'Mixtral', 
          '4o-mini': 'GPT 4o-mini', 'deepseek-coder': 'Deepseek Coder'
         }

app,rt,tcs,ThreadConversation = fast_app(
    'data/threads.db',
    hdrs=Theme.blue.headers(),
    id=int, name=str, tid=int, cid=str, mn=str, mid=str, rid=str, when=datetime, pk='id',
    live=True
)

# %% ../nbs/app.ipynb 3
def get_llm_db():
    if os.environ.get("LLM_USER_PATH") is not None:
        if not hasattr(thread_local, "db"):
            thread_local.db = sqlite_utils.Database(Path(os.environ["LLM_USER_PATH"]) / "logs.db")
    else:
        if not hasattr(thread_local, "db"):
            thread_local.db =  sqlite_utils.Database(llm.user_dir() / "logs.db")
    return thread_local.db

# %% ../nbs/app.ipynb 4
class LoggedChat(BasicRepr):
    def __init__(self, tid:int, mn:str, include=True, may_log=True, p:str=None, sp:str=None, m=None, c=None): 
        store_attr()
        self.m = llm.get_model(self.mn)
        self.c = self.m.conversation()

    def prompt(self, tid, mid, p, sp=None):
        global tcs, l
        self.p = p
        self.sp = sp
        r = self.c.prompt(p, system=sp)
        if isinstance(r, Exception):
            return r
        if self.may_log:
            db = get_llm_db()
            try:
                r.log_to_db(db)
                rid = first(db.execute("SELECT MAX(id) FROM responses WHERE conversation_id=?", self.c.id))[0]
                tcs.insert(tid=tid, cid=self.c.id, mn=self.mn, mid=mid, rid=rid, when=datetime.now().isoformat())
            except Exception as e:
                return e
        else:
            # need to iterate the response so that it gets added to conversation
            for _ in r:
                pass
        return r

# %% ../nbs/app.ipynb 5
lcs = [LoggedChat(tid=1, mn=k, include=True, may_log=START_WITH_LOGGING) for i, k in enumerate(MODELS) if i < N_MODELS]

def model_selector(tid=1):
    model_controls = []
    
    for i, model in enumerate([lc.mn for lc in lcs], start=1):
        # Create a column for each model with dropdown and switch
        model_column = Div(
            # Model dropdown
            Select(
                *[Option(MODELS[m], value=m, selected=(m==model)) for m in MODELS],
                id=f'model_{i}',
                name="model",
                cls="w-full mb-2",
                **{
                    "hx-post": f"/update_model/{tid}/{i}",
                    "hx-trigger": f"click from:#model_{i} .uk-drop-close",
                    "hx-target": f"#model_feedback_{i}",
                    "hx-swap": "innerHTML",
                    "hx-include": f"#model_{i},#may_log"
                }
            ),
            Div(id=f"model_feedback_{i}", cls="text-xs mb-2"),  # Feedback area
            DivRAligned(
                LabelSwitch(
                    label="Include", 
                    id=f'switch_{i}',
                    checked=lcs[i-1].include,
                    cls="mt-2",
                    **{
                        "hx-post": f"/toggle_model/{i}",
                        "hx-trigger": "change",
                        "hx-target": f"#switch_feedback_{i}",
                        "hx-swap": "innerHTML",
                        "hx-include": f"#switch_{i}"
                    }
                ),
                A(UkIcon("download"),
                       alt="Download recent for this model",
                       href=f"/download/{tid}/ALL/{i-1}",
                       cls="uk-button uk-button-link"),                  
            ),
            Div(id=f"switch_feedback_{i}", cls="text-xs"),  # Switch feedback area
            
            cls="px-2 text-center"
        )
        model_controls.append(model_column)
    
    return Div(
        *model_controls,
        cls="flex justify-between mb-4"
    )
    
@rt("/update_model/{tid}/{idx}")
async def update_model(tid:int, idx: int, model: str, request: Request):
    global lcs
    print(model)
    form_data = await request.form()
    lcs[idx-1] = LoggedChat(tid=tid, mn=model, include=lcs[idx-1].include, may_log=(form_data.get(f"may_log") == "on"))
    # Return visual feedback
    return Div(
        MODELS[model], 
        cls="text-success text-xs mt-1 transition-opacity duration-1000 opacity-100",
        _="on load wait 1s then add .opacity-0"
    )

@rt("/toggle_model/{idx}")
async def toggle_model(idx: int, request: Request):
    global lcs
    form_data = await request.form()
    lcs[idx-1].include = (form_data.get(f"switch_{idx}") == "on")
    status = "enabled" if lcs[idx-1].include else "disabled"
    # Return visual feedback
    return Div(
        f"Model {status}", 
        cls=f"text-{'success' if lcs[idx-1].include else 'warning'} text-xs mt-1 transition-opacity duration-1000 opacity-100",
        _="on load wait 1s then add .opacity-0"
    )
    
@rt("/toggle_logging")
async def toggle_logging(request: Request):
    global lcs
    form_data = await request.form()
    for lc in lcs:
        lc.may_log = (form_data.get(f"may_log") == "on")
    status = "enabled" if (form_data.get(f"may_log") == "on") else "disabled"
    # Return visual feedback
    return Div(
        f"Logging {status}", 
        cls=f"text-success text-xs mt-1 transition-opacity duration-1000 opacity-100",
        _="on load wait 1s then add .opacity-0"
    )

def prompt_form(thread_id=1, message_id=1):
    return Div(
        Form(
            TextArea(
                placeholder="Enter your prompt here...",
                cls="w-full h-40",
                id="main_prompt",
                name="main_prompt"
            ),
            Button(
                "Submit",
                cls="btn btn-primary mt-2",
                id="submit_button",
                **{
                    "hx-post": f"/responses/{thread_id}/{message_id}",
                    "hx-target": "#responses_container",
                    "hx-swap": "afterbegin",
                    "hx-include": "#system_prompt,#main_prompt",
                    "hx-swap-oob": "true",
                    "hx-disabled-elt": "this"
                }
            ),
            Script("""
                me().on("keydown", ev => {
                    if (ev.ctrlKey && ev.key === "Enter") {
                        halt(ev);
                        any("#submit_button").send("click");
                    }
                })
            """),
            id="prompt_form",
            cls="mb-4",
            hx_swap_oob="true",            
            _="on htmx:afterSwap remove me",
        )
    )

def input_section(thread_id=1, message_id=1):
    selector = model_selector(thread_id)
    system_prompt = Div(
        Details(
            Summary("System Prompt"),
            TextArea(
                placeholder="Enter system prompt here...",
                cls="w-full h-32",
                id="system_prompt",
                name="system_prompt"
            ),
            cls="mb-4"
        )
    )
    may_log = (
                LabelSwitch(
                    label="Log Responses", 
                    id=f'may_log',
                    checked=START_WITH_LOGGING,
                    cls="mt-2",
                    **{
                        "hx-post": f"/toggle_logging",
                        "hx-trigger": "change",
                        "hx-target": f"#logging_feedback",
                        "hx-swap": "innerHTML",
                        "hx-include": f"#may_log"
                    }
                ),
                Div(id=f"logging_feedback", cls="text-xs"),  # Switch feedback area
            )
    prompt_area = prompt_form(thread_id, message_id)

    return selector, Hr(), system_prompt, Hr(), prompt_area, *may_log

# %% ../nbs/app.ipynb 6
def display_system_prompt(thread_id=1, message_id=1, sp=""):
    return H6("System Prompt:", cls="font-semibold mb-2"), Div(sp, id=f"system_prompt_{thread_id}_{message_id}", cls="mb-4 p-2 border rounded"),

def display_user_prompt(thread_id=1, message_id=1, p=""):
    return H6("User Prompt:", cls="font-semibold mb-2"), Div(p, id=f"user_prompt_{thread_id}_{message_id}", cls="mb-4 p-2 border rounded")

@rt("/download/{thread_id}/{message_id}/{i}/{j}")
def download_response(thread_id: int, message_id: int, i: int, j: int):
    content = f"""Prompt: {str(lcs[i].c.responses[j].prompt.prompt)}
----
Reponse:
{str(lcs[i].c.responses[j])}"""
    filename = f"response_{thread_id}_{message_id}_{lcs[i].mn}_{datetime.now():%Y%m%d_%H%M}.txt"
    headers = {
        "Content-Disposition": f"attachment; filename={filename}",
        "Content-Type": "text/plain"
    }
    return Response(content=content, headers=headers)


@rt("/download/{thread_id}/ALL/{i}")
def download_response(thread_id: int, i: int):
    content = ""
    for r in lcs[i].c.responses:
        content = content + f"""Prompt: {r.prompt.prompt}
----
Response:
{str(r)}

----
"""
    filename = f"response_{thread_id}_{lcs[i].mn}_{datetime.now():%Y%m%d_%H%M}.txt"
    headers = {
        "Content-Disposition": f"attachment; filename={filename}",
        "Content-Type": "text/plain"
    }
    return Response(content=content, headers=headers)

def model_header(name, response_id, thread_id: int, message_id: int, i: int, result, timestamp=None):
    if timestamp is None:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    copy_script = """
    async function copyFormatted(id) {
        const content = document.getElementById(id);
        try {
            await navigator.clipboard.write([
                new ClipboardItem({
                    'text/html': new Blob([content.innerHTML], {type: 'text/html'}),
                    'text/plain': new Blob([content.innerText], {type: 'text/plain'})
                })
            ]);
        } catch (err) {
            console.error('Failed to copy: ', err);
        }
    }
    """
    
    return Div(
        Script(copy_script),
        H5(
            Div(
                Div(name, cls="flex-grow text-center"),
                Button(UkIcon("clipboard"), 
                      onclick=f"copyFormatted('{response_id}')",
                      cls="float-right"),
                A(UkIcon("download"),
                       href=f"/download/{thread_id}/{message_id}/{i}/{len(lcs[i].c.responses)-1}",
                       cls="uk-button uk-button-link") if not isinstance(result, Exception) else None,
                cls="flex justify-between items-center w-full",
            ),
            title=timestamp,
            cls=TextT.center,
        ),
        Hr(),
    )

@rt("/responses/{thread_id}/{message_id}")
def message_response(thread_id:int=1, message_id:int=1, main_prompt:str="", system_prompt:str=None):
    global lcs, MODELS, N_MODELS

    def run_prompts(lc): lc.prompt(thread_id, message_id, main_prompt, system_prompt) if lc.include else None
        
    with ThreadPool(len(lcs)) as pool:
        rs = pool.map(run_prompts, lcs)

    response_div = Div(
        Details(
            Summary(f"Prompts given (Message {message_id})"),
            Div(
                *display_system_prompt(sp=system_prompt) if system_prompt is not None and system_prompt.strip() != "" else (),
                *display_user_prompt(p=main_prompt) if main_prompt is not None and main_prompt.strip() != "" else (),
                cls="bg-neutral-content space-y-2"
            ),
            cls="mb-4",
            open=True
        ),
        *[Div(
            model_header(MODELS[lc.mn], f"response_{(message_id * N_MODELS) - i}", thread_id, message_id, i, rs[i]),
            Div(render_md(str(lc.c.responses[-1])), id=f"response_{(message_id * N_MODELS) - i}", cls="mb-8") \
                if not isinstance(rs[i], Exception) else \
            Div(str(rs[i]), id=f"response_{(message_id * N_MODELS) - i}", cls="bg-warning mb-8") \
        ) for i, lc in enumerate(lcs) if lc.include],
        **{
            "hx-swap": "afterbegin",
            "hx-target": "#responses_container"
        }
    ),
    new_form = prompt_form(thread_id, message_id + 1)

    return response_div, new_form


# %% ../nbs/app.ipynb 7
@rt('/')
def index(thread_id=1, message_id=1):
    return Title("CounciLLMs"), Div(input_section(), Div(id="responses_container", cls="space-y-4"), Script("""htmx.on("htxm:afterRequest", function(evt) {
    console.log("HTMX Request completed:", evt);
));"""))

# %% ../nbs/app.ipynb 10
serve()
