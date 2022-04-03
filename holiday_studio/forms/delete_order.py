from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms_sqlalchemy.fields import QuerySelectField

from models import Order, EmployeeOrder, Client, ClientOrder, create_session
from flask_login import current_user


def get_orders():
    session = create_session()
    id_orders = session.query(EmployeeOrder.id_order).where(EmployeeOrder.id_employee == current_user.id).all()
    id_orders = list(map(lambda x: x[0], id_orders))
    orders = []
    for id_order in id_orders:
        orders.append(session.query(Order).where(Order.id == id_order).first())
    session.close()
    print(orders)
    return orders


class DeleteOrder(FlaskForm):

    order_list = QuerySelectField("Заказ",
                                   query_factory=get_orders,
                                   get_pk=lambda order: order.id,
                                   get_label=lambda order: order.title)
    submit = SubmitField("Удалить")
