from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms_sqlalchemy.fields import QuerySelectField

from models import EmployeeOrder, Client, ClientOrder, create_session
from flask_login import current_user


def get_clients():
    session = create_session()
    id_orders = session.query(EmployeeOrder.id_order).where(EmployeeOrder.id_employee == current_user.id).all()
    id_orders = list(map(lambda x: x[0], id_orders))
    print(id_orders)
    clients = []
    for id_order in id_orders:
        client = session.query(ClientOrder).where(ClientOrder.id_order == id_order).first()
        client = session.query(Client).where(Client.id == client.id_client).first()
        clients.append(client)
    session.close()
    return clients


class ChangeClientFormFirst(FlaskForm):

    client_list = QuerySelectField("Заказ",
                                   query_factory=get_clients,
                                   get_pk=lambda client: client.id,
                                   get_label=lambda client: client.full_name)
    submit = SubmitField("Изменить")