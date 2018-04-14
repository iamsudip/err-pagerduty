# err-pagerduty

**Setup**

Create a virtual environment for convenience: `$ virtualenv virt -p python3`

Install errbot: `$ pip install errbot==5.2.0`

After errbot is installed create an empty directory, inside the empty directory, run: `$ errbot --init`

The above command shall create few files, directories as `plugins`, `data`, `config.py`

In `config.py` set backend as required, for slack set it as `BACKEND = 'Slack'`, We need few more config as well:

`PAGERDUTY_TOKEN = 'pagerduty-token'`, `BOT_PREFIX = '%'`, `PAGERDUTY_ADMIN_EMAIL = 'email@domain.com'`, `BOT_IDENTITY = {'token': 'slack-token'}`

Now, clone this repo inside plugins directory: `cd plugins && git clone https://github.com/iamsudip/err-pagerduty .`

You are good to go...

**Run**

To run the bot, please come to the project root directory where config.py exists, run `$ errbot`. It should initialize the bot and connect to slack.

** Features **

* %pd list oncall <team_name_1> <team_name_2>

Ex: %pd list oncall devops

Above command should list current primary and secondary oncall of team

* %pd list <team_name_1> <team_name_2>

Ex: %pd list devops

Should list all members of the team and list contact information

* %pd list incidents <status(open/triggered/acknowledged)>

Ex: %pd list incidents open

Should list all open incidents with id, subject, date/time and assignee

* %pd ack <incident_id_1> <incident_id_2>

Ex: %pd list ABCDEF

Should acknowledge incident 
