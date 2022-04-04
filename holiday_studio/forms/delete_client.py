from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms_sqlalchemy.fields import QuerySelectField

from models import EmployeeOrder, create_session, ClientOrder, Client
from flask_login import current_user


def get_clients():

    session = create_session()

    id_orders = session.query(EmployeeOrder.id_order).where(EmployeeOrder.id_employee == current_user.id).all()
    id_orders = list(map(lambda x: x[0], id_orders))
    clients = set()

    for id_order in id_orders:
        print(id_order)
        id_client = session.query(ClientOrder.id_client).where(ClientOrder.id_order == id_order[0]).first()
        print(id_client)
        client = session.query(Client).where(Client.id == id_client).first()
        clients.add(client)

    session.close()

    return list(clients)


class DeleteClientForm(FlaskForm):

    client_list = QuerySelectField("Заказ",
                                  query_factory=get_clients,
                                  get_pk=lambda client: client.id,
                                  get_label=lambda client: client.full_name)
    submit = SubmitField("Удалить")