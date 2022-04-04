from .create_order import CreateOrderForm
from wtforms import SubmitField
from models import Client, create_session


def get_all_clients():
    session = create_session()
    clients = session.query(Client).all()
    return clients


class ChangeOrderFormSecond(CreateOrderForm):
    submit = SubmitField("Сохранить изменения")