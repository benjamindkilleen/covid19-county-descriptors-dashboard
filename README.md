# COVID-19 County-level Descriptors Dashboard

## Installation

The packages in `requirements.txt` are currently incomplete, but in princple, run
```sh
pip install -r requirements.txt
```
and if you're an extremely nice person, let me know how it goes!

Then soft-link the data folder from [U.S. County-level Summaries](https://github.com/JieYingWu/COVID-19_US_County-level_Summaries). From root:
```sh
ln -s PATH/TO/COVID-19_US_County-level_Summaries ./data
```

## Usage

Run
```sh
python3 main.py
```

You should see something like:
```
selected 3052 / 3220 counties for embedding
FOR FAST DEBUGGING ONLY
embedding...
FOR FAST DEBUGGING ONLY
clustering...
Running on http://127.0.0.1:8050/
Debugger PIN: 687-457-501
 * Serving Flask app "main" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on
```

You can disregard the DEBUG warnings for now. Then visit http://127.0.0.1:8050/ (or the address
listed in the output) in a browser. In debug mode, making changes to the source will re-run the
server from scratch and prompt a reload, which is nice. Thanks Dash.
