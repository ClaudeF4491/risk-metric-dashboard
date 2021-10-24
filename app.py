

import datetime
import threading
import atexit
import btc
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from flask_caching import Cache


# Time in seconds between background refresh of backend data
DATA_REFRESH_TIME = 10 * 60

# Time in seconds for how long to keep backend data cached for
# Should keep high to allow background refreshes
CACHE_TIMEOUT = 24 * 60 * 60

# lock to control access to variable
data_lock = threading.Lock()

# thread handler
compute_thread = threading.Thread()


print("Initializing cache ...")
df = btc.generate_data()
cache_time = datetime.datetime.utcnow().isoformat()
print("Cache initialized.")


# Initialize the server
external_stylesheets = [
    # Dash CSS
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    # Loading screen CSS
    'https://codepen.io/chriddyp/pen/brPBPO.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.layout = html.Div([
    html.Div([
        html.H4('BTC Risk Chart'),
        html.Div(id='live-update-text'),
        dcc.Graph(id='live-update-graph'),
    ]),
    # signal value to trigger callbacks
    dcc.Store(id='signal')
])

# Create the cache
CACHE_CONFIG = {
    # try 'filesystem' if you don't want to setup redis
    # 'CACHE_TYPE': 'redis',
    # 'CACHE_REDIS_URL': os.environ.get('REDIS_URL', 'redis://localhost:6379')
    'CACHE_TYPE': 'simple',
    # 'CACHE_DIR': "./cache",
    'CACHE_DEFAULT_TIMEOUT': CACHE_TIMEOUT
}
cache = Cache()
cache.init_app(app.server, config=CACHE_CONFIG)


# Cached compute function
@cache.memoize()
def global_store():
    print("INSIDE global_store() ...")
    df = btc.generate_data()
    cache_time = datetime.datetime.utcnow().isoformat()
    return df, cache_time


def interrupt():
    print("!!! INTERRUPT!")
    global compute_thread
    compute_thread.cancel()

def worker_execute():
    global commonDataStruct
    global compute_thread
    with data_lock:
        print("Data Lock! Updating...")
        cache.clear()
        df, cache_time = global_store()
        print("Updating and releasing")
        print(f"Latest vals: df len: {len(df)}, timestamp: {cache_time}")


    # Set the next thread to happen
    print("Set the next thread to happen")
    compute_thread = threading.Timer(DATA_REFRESH_TIME, worker_execute, ())
    compute_thread.start()

def worker_init():
    # Do initialisation stuff here
    print("Initializing thread ...")
    global compute_thread
    # Create your thread
    compute_thread = threading.Timer(DATA_REFRESH_TIME, worker_execute, ())
    print("Created thread")
    compute_thread.start()
    print("started thread")

# Initiate the worker
print("calling worker_init")
worker_init()
# When you kill Flask (SIGTERM), clear the trigger for the next thread
atexit.register(interrupt)

# Header callback
@app.callback(Output('live-update-text', 'children'), Input('signal', 'data'))
def update_header(n):
    with data_lock:
        _, cache_time = global_store()
    next_update_time = datetime.datetime.fromisoformat(cache_time) + datetime.timedelta(seconds=DATA_REFRESH_TIME)
    style = {'padding': '5px', 'fontSize': '16px'}
    return [
        html.Span(f"Notebook Code Version (Date): {btc.LAST_MODIFIED}", style=style),
        html.Br(),
        html.Span(f"New Chart Available Every: {DATA_REFRESH_TIME / 60} minutes", style=style),
        html.Br(),
        html.Span(f"Chart Last Updated: {cache_time}", style=style),
        html.Br(),
        html.Span(f"Refresh page to get latest after next update at: {next_update_time}", style=style),
    ]

# Graph callback
# TODO: Decide what to do with the signal input
@app.callback(Output('live-update-graph', 'figure'), Input('signal', 'data'))
def update_graph(value):
    # generate_figure gets data from `global_store`.
    # the data in `global_store` has already been computed
    # by the `compute_value` callback and the result is stored
    # in the global redis cached
    print("Fetching cache ...")
    with data_lock:
        df, _ = global_store()
    print("Cache fetch complete")
    return btc.generate_figure(df)


if __name__ == '__main__':
    app.run_server()