import pytest

from app.slack.forms import SlackInviteForm


@pytest.mark.django_db
class TestSlackInviteForm:
    """Tests to validate that the slack invite form runs
    the appropriate validations"""

    def test_blank_data(self):
        form = SlackInviteForm({})
        assert not form.is_valid()
        assert set(form.errors.keys()) == {'email', 'accept_tos'}

    def test_allows_non_burner_domain(self):
        form = SlackInviteForm({
            'email': 'foo@bar.com',
            'accept_tos': True,
        })
        assert form.is_valid()
