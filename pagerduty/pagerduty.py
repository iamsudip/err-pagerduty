from errbot import BotPlugin, botcmd
from config import PAGERDUTY_TOKEN, PAGERDUTY_ADMIN_EMAIL

from pygerduty.common import NotFound

import pygerduty.v2


class pagerduty(BotPlugin):
    """
    This is a very basic plugin to try out your new installation and get you started.
    Feel free to tweak me to experiment with Errbot.
    You can find me in your init directory in the subdirectory plugins.
    """
    # Cached instace of pygerduty client,
    # It gets created when any first time any bot command gets created
    _pd_client = None
    PAGERDUTY_TOKEN = PAGERDUTY_TOKEN
    PAGERDUTY_ADMIN_EMAIL = PAGERDUTY_ADMIN_EMAIL

    @classmethod
    def _get_pd_client(cls):
        if not cls._pd_client:
            cls._pd_client = pygerduty.v2.PagerDuty(cls.PAGERDUTY_TOKEN)
        return cls._pd_client

    @classmethod
    def _get_scheduled_users_for_team(cls, team_name):
        """
        Utility method to get on call users for given team name

        Args:
            team_name: string

        Returns:
            dict
        """
        pager = cls._get_pd_client()
        schedules = [_ for _ in pager.schedules.list()]
        oncall_to_schedule_map = {}
        # If a team is responsible for multiple on calls
        for schedule in schedules:
            schedule_teams = schedule.teams
            # Team is always one, but the type is list, so it's better to iterate
            for schedule_team in schedule_teams:
                if schedule_team.summary == team_name:
                    oncall_to_schedule_map[schedule] = schedule.schedule_users
        return oncall_to_schedule_map

    @botcmd(split_args_with=None)
    def pd_list_oncall(self, msg, args):
        """
        Bot command to list oncall users for a given team name
        """
        if not args:
            yield 'Please mention at least one team name!'
        for team_name in args:
            all_schedule_for_team = self._get_scheduled_users_for_team(team_name)
            for schedule, users in all_schedule_for_team.items():
                yield 'Current on call reps for schedule {0} for team {1}'.format(schedule.name, team_name)
                yield ', '.join([_.summary for _ in users])

    @classmethod
    def _get_team(cls, team_name):
        """
        Utility method to get pygerduty team object given a name

        Args:
            team_name: string

        Returns:
            pygerduty object if found else None
        """
        pager = cls._get_pd_client()
        teams = [_ for _ in pager.teams.list()]
        for team in teams:
            if team.name == team_name:
                return team

    @classmethod
    def _get_users(cls):
        """
        Utility method to get all pygerduty users
        """
        pager = cls._get_pd_client()
        users = [_ for _ in pager.users.list()]
        return users

    @classmethod
    def _get_users_for_team(cls, team_name):
        """
        Utility method to get all users for a given team

        Args:
            team_name: string

        Returns:
            list
        """
        users = cls._get_users()
        team_users = []
        for user in users:
            user_teams = user.teams
            for user_team in user_teams:
                if user_team.summary == team_name:
                    team_users.append(user)
        return team_users

    @classmethod
    def _get_human_readable_contact_methods_for_user(cls, user):
        """
        Utility method to make pygerduty contacts human readable for channel representation
        """
        contact_methods = []
        pager_c_methods = [_ for _ in user.contact_methods.list()]
        for c_method in pager_c_methods:
            contact = '{contact} {type}: {detail}'.format(
                contact=c_method.summary,
                type=c_method.type.split('_')[0],
                detail=c_method.address
            )
            contact_methods.append(contact)
        return contact_methods

    @botcmd(split_args_with=None)
    def pd_list(self, msg, args):
        """
        Bot command to list users of given team name
        """
        if not args:
            yield 'Please mention at least one team name!'
        for team_name in args:
            yield 'List of members in team: {0}'.format(team_name)
            users = self._get_users_for_team(team_name)
            for user in users:
                yield 'Contact info for member: {0}'.format(user.summary)
                contact_methods = self._get_human_readable_contact_methods_for_user(user)
                for contact in contact_methods:
                    yield contact
            if not users:
                yield 'No member found for team: {0}'.format(team_name)

    @classmethod
    def _get_incidents(cls, status):
        """
        Utility method to find incidents by given status
        """
        pager = cls._get_pd_client()
        # Tried with pager.incidents.list(status='open'), it still returns all, so filtering manually
        incidents = [_ for _ in pager.incidents.list() if _.status == status]
        return incidents

    @classmethod
    def _get_human_readable_incidents(cls, incidents):
        """
        Utility method to make Pygerduty incidents to make human readable
        """
        incident_msgs = []
        msg_format = 'Incident ID: {inc_id}, Subject: {subject}, Time: {time}, assignee: {assignee}'
        for inc in incidents:
            assignee = inc.assignments[0].assignee.summary
            incident_msgs.append(msg_format.format(inc_id=inc.id, subject=inc.summary, time=inc.created_at, assignee=assignee))
        return incident_msgs

    @botcmd(split_args_with=None)
    def pd_list_incidents(self, msg, args):
        """
        Bot command to list open/triggered, acknowledged incidents
        """
        if not args:
            yield 'Please mention at least one incident status!'
        for status in args:
            valid_statuses = ['open', 'triggered', 'acknowledged']
            if status not in valid_statuses:
                yield '{0} is not valid. Please use valid statuses only: {1}'.format(status, ', '.join(valid_statuses))
                continue
            # in version 2 API open status is not there, open means triggered
            if status == 'open':
                status = 'triggered'
            yield 'Listing all {status} incidents...'.format(status=status)
            incidents = self._get_incidents(status)
            hr_incidents = self._get_human_readable_incidents(incidents)
            for incident in hr_incidents:
                yield incident
            yield 'Listing complete.'

    @classmethod
    def _get_incident(cls, inc_id):
        """
        Utility method to get incident

        Args:
            inc_id: pagerduty incident ID

        Returns:
            Pygerduty object of incident if found else None
        """
        pager = cls._get_pd_client()
        try:
            return pager.incidents.show(entity_id=inc_id)
        except NotFound:
            return None

    @classmethod
    def _ack_incident(cls, inc_id, user_email=None):
        """
        Utility method to acknowledge incident

        Args:
            inc_id: alphanumeric incident ID
            user_email: pager duty user email

        Returns:
            None
        """
        pager = cls._get_pd_client()
        if not user_email:
            user_email = cls.PAGERDUTY_ADMIN_EMAIL
        pager.incidents.update(user_email, {'id': inc_id, 'status': 'acknowledged', 'type': 'incident_reference'})

    @botcmd(split_args_with=None)
    def pd_ack(self, msg, args):
        """
        Bot command to acknowledge incident
        """
        if not args:
            yield 'Please mention at least one incident ID!'
        for incident_id in args:
            incident = self._get_incident(incident_id)
            if not incident:
                yield 'Please mention corrent incident ID.'
                continue
            yield 'Acknowledging incident {inc_id}...'.format(inc_id=incident_id)
            self._ack_incident(incident_id)
            yield 'Acknowledged Incident: {inc_id}'.format(inc_id= incident_id)
