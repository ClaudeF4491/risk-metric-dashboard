# Plotly Dash Dashboard for Bitcoin Raven Risk Metric

This code is a wrapper around the Bitcoin Raven Risk Metric to deploy a Heroku-hosted
Dash webpage to display what's normally in the notebook.

Bitcoin Raven's original source code, videos, and Telegram are found here:
https://www.youtube.com/channel/UCrlkqSLmHL8ZPVpOxj7La4Q/about

Please visit there for all the great work around the metric itself, as for
notebook file updates.

## References
* All things Bitcoin Raven Risk Metric are linked in [here](https://www.youtube.com/channel/UCrlkqSLmHL8ZPVpOxj7La4Q/about)
* Dash deployment inspired by their docs [here](https://dash.plotly.com/deployment#heroku-for-sharing-public-dash-apps-for-free)
* Background thread cache refreshing inspired by [here](https://stackoverflow.com/questions/14384739/how-can-i-add-a-background-thread-to-flask)
* Plotly Dash Global Caching inspired by [this code](https://github.com/plotly/dash-recipes/blob/master/dash-global-cache.py) and the [memoization tutorial](https://dash.plotly.com/performance#memoization)

## Notes about Dashboard

* This is EXPERIMENTAL and a work-in-progress (side-project)
* This is hosting a snapshot of the notebook
  * At time of writing, the notebooks are updated nearly daily, so this may not reflect the latest revision
  * The revision is listed at the top of the webpage when hosted, and at the top of the code module

## Setup

### Get Quandl API Key
If you do not have a Quandl account, you'll need to create one and generate an API key.
1. To get an API key, please sign up for a free [Quandl account](https://www.quandl.com/account)
2. You can find your API key on your account [settings page](https://www.quandl.com/account/api).
3. Copy that API key and save somewhere for now

### Run Locally

1. Create and activate virual environment:
    ```
    python3 -m venv ./venv
    source ./venv/bin/python
    ```
2. Install requirements: `pip install --update pip wheel && pip install -r requirements.txt`
3. Set the `API_KEY_QUANDL` environment variable to the key from above: `export API_KEY_QUANDL=<api_key>`
4. Run: `python3 ./app.py`
5. Open webpage: `http://localhost:8050`

### Deploy

Create a Heroku account and login. You can log in the CLI with `heroku login -i`.

#### Deploy from this Github

1. Click this button below to deploy directly from this github repository: [![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy?template=https://github.com/ClaudeF4491/risk-metric-dashboard/tree/master)
2. Provide it a unique project name. This will be in your URL
3.

#### Deploy from your codebase

Follow [these directions](https://dash.plotly.com/deployment#heroku-for-sharing-public-dash-apps-for-free) instead.
If you ran `git clone` on this repo, you may need to delete the `.git` directory first for Heroku to create it's own git
directory.

## Updating notebook code

See the header of the `btc.py` module for directions on how to copy/paste the latest code in.

## TODO

This is a first-cut early experiment. So lots of TODOs, in no particular order.
- [ ] Integrate and cache the other Bitcoin Raven Risk metrics (ETH, SOL)
- [ ] Add a drop-down to switch between different metrics
- [ ] Add checkboxes to switch on and off the different components that are averaged in the final calculation
- [ ] Expose a Flask endpoint that returns the latest risk metric (and timestamp)
- [ ] Consider other ways to more cleanly integrate with the notebook code. It's currently copy/paste with several manual edits.