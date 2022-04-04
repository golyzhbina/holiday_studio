from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms_sqlalchemy.fields import QuerySelectField
from .delete_order import DeleteOrderForm
from models import Order, EmployeeOrder, create_session
from flask_login import current_user


def get_orders():
    session = create_session()
    id_orders = session.query(EmployeeOrder.id_order).where(EmployeeOrder.id_employee == current_user.id).all()
    id_orders = list(map(lambda x: x[0], id_orders))
    orders = []
    for id_order in id_orders:
        orders.append(session.query(Order).where(Order.id == id_order).first())
    session.close()
    return orders


class ChangeOrderFormFirst(DeleteOrderForm):

    submit = SubmitField("Изменить")


