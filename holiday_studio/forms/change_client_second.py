from forms.create_client import CreateClientForm
from wtforms import SubmitField


class ChangeClientFormSecond(CreateClientForm):

    submit = SubmitField("Сохранить")