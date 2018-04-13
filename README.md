# err-pagerduty

*Setup*

Create a virtual environment for convenience: `$ virtualenv virt -p python3`

Install errbot: `$ pip install errbot==5.2.0`

After errbot is installed create an empty directory, inside the empty directory, run: `$ errbot --init`

The above command shall create few files, directories as `plugins`, `data`, `config.py`

In `config.py` set backend as required, for slack set it as `BACKEND = 'Slack'`, We need few more config as well:

`PAGERDUTY_TOKEN = 'pagerduty-token'`, `BOT_PREFIX = '%'`, `PAGERDUTY_ADMIN_EMAIL = 'email@domain.com'`, `BOT_IDENTITY = {'token': 'slack-token'}`

Now, clone this repo inside plugins directory: `cd plugins && git clone https://github.com/iamsudip/err-pagerduty .`

You are good to go...

*Run*

To run the bot, please come to the project root directory where config.py exists, run `$ errbot`. It should initialize the bot and connect to slack.
