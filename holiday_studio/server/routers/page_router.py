import sqlalchemy
from flask import Blueprint, request, render_template, redirect
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.exc import IntegrityError

from forms.create_client import CreateClientForm
from forms.create_order import CreateOrderForm
from forms.delete_order import DeleteOrderForm
from forms.change_order_first import ChangeOrderFormFirst
from forms.change_order_second import ChangeOrderFormSecond
from forms.delete_client import DeleteClientForm
from forms.delete_order import DeleteOrder
from forms.change_client_first import ChangeClientFormFirst
from forms.change_client_second import ChangeClientFormSecond
from forms.login import LoginForm
from models import AlchemyEncoder, Employee, Client, EmployeeOrder, ClientOrder
from models import Order, create_session
import json
from flask_login import current_user

router = Blueprint("",
                   __name__,
                   template_folder="/server/templates")


@router.route("/login", methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        session = create_session()
        employee = session.query(Employee).\
            filter(Employee.email == login_form.email.data).first()
        if employee and employee.check_password(login_form.password.data):
            login_user(employee)
            session.close()
            return redirect("/")
        else:
            session.close()
            return redirect("/login")
    return render_template("login.html", title="Авторизация", form=login_form)


@router.route("/create_client", methods=["GET", "POST"])
@login_required
def create_client():
    create_client_form = CreateClientForm()
    if create_client_form.validate_on_submit():
        session = create_session()
        client = Client(full_name=create_client_form.full_name.data,
                        age=create_client_form.age.data,
                        phone=create_client_form.phone.data,
                        email=create_client_form.email.data)
        session.add(client)
        try:
            session.commit()
            session.close()
            return redirect("/")
        except IntegrityError:
            create_client_form.email.errors.append("Email уже используется")
            session.close()
            return render_template("create_client.html", title="Создание клиента", form=create_client_form)

    return render_template("create_client.html", title="Создание клиента", form=create_client_form)


@router.route("/create_order", methods=["GET", "POST"])
@login_required
def create_order():
    create_order_form = CreateOrderForm()
    if create_order_form.validate_on_submit():
        client = create_order_form.client_list.data
        print(client)
        session = create_session()
        order = Order(price=create_order_form.price.data,
                      title=create_order_form.price.data,
                      describtion=create_order_form.describtion.data)
        # чтобы получить order_id сначала добавим в базу
        session.add(order)
        session.commit()

        # связываем M:M
        employee_order = EmployeeOrder(id_employee=current_user.id,
                                       id_order=order.id)
        client_order = ClientOrder(id_client=client.id,
                                   id_order=order.id)

        session.add(client_order)
        session.add(employee_order)
        session.commit()
        session.close()
        return redirect("/")
    return render_template("create_order.html", title="Создание заказа", form=create_order_form)


@router.route("/get_all_orders", methods=["GET", "POST"])
@login_required
def get_all_orders():

    session = create_session()

    id_orders = session.query(EmployeeOrder.id_order).where(EmployeeOrder.id_employee == current_user.id).all()
    id_orders = list(map(lambda x: x[0], id_orders))
    orders_clients = dict()

    for id_order in id_orders:
        order = session.query(Order).where(Order.id == id_order).first()
        id_clients = session.query(ClientOrder.id_client).where(ClientOrder.id_order == id_order).all()
        id_clients = list(map(lambda x: x[0], id_clients))
        client = []
        for id_client in id_clients:
            client.append(session.query(Client.full_name).where(Client.id == id_client).first()[0])
        orders_clients[order] = " ".join(client)

    return render_template("get_all_orders.html", orders_customers=orders_clients)


@router.route("/delete_order", methods=["GET", "POST"])
@login_required
def delete_order():

    form = DeleteOrder()
    session = create_session()
    if form.validate_on_submit():
        order = form.order_list.data
        session.delete(order)
        session.commit()

        empl_order = session.query(EmployeeOrder).where(EmployeeOrder.id_order == order.id).all()
        for note in empl_order:
            session.delete(note)
            session.commit()

        cli_order = session.query(ClientOrder).where(ClientOrder.id_order == order.id)
        for note in cli_order:
            session.delete(note)
            session.commit()

        session.close()
        return redirect("/")

    return render_template("delete_order.html", form=form)


@router.route("/change_order_choice", methods=["GET", "POST"])
@login_required
def change_order_choice():

    change_order_form = ChangeOrderFormFirst()
    if change_order_form.validate_on_submit():
        changed_order = change_order_form.order_list.data
        return redirect(f"/change_order_info/{changed_order.id}")

    return render_template("change_order_first.html", form=change_order_form)


@router.route("/change_order_info/<id_order>", methods=["GET", "POST"])
@login_required
def change_order(id_order):

    change_order_form = ChangeOrderFormSecond()
    session = create_session()
    order = session.query(Order).where(Order.id == id_order).first()
    if change_order_form.validate_on_submit():
        order.title = change_order_form.title.data
        order.price = change_order_form.price.data
        order.describtion = change_order_form.describtion.data
        session.commit()

        client = change_order_form.client_list.data
        client_order = session.query(ClientOrder).where(ClientOrder.id_order == id_order).first()
        session.delete(client_order)
        new_client_order = ClientOrder(id_client=client.id, id_order=id_order)

        session.add(new_client_order)
        session.commit()
        session.close()
        return redirect("/")

    return render_template("change_order_second.html", form=change_order_form, order=order)


@router.route("/get_all_clients", methods=["GET", "POST"])
@login_required
def get_all_clients():

    session = create_session()

    id_orders = session.query(EmployeeOrder.id_order).where(EmployeeOrder.id_employee == current_user.id).all()
    id_orders = list(map(lambda x: x[0], id_orders))
    clients = set()

    for id_order in id_orders:
        id_client = session.query(ClientOrder.id_client).where(ClientOrder.id_order == id_order).first()[0]
        client = session.query(Client).where(Client.id == id_client).first()
        clients.add(client)

    session.close()

    return render_template("get_all_clients.html", clients=list(clients))


@router.route("/delete_client", methods=["GET", "POST"])
@login_required
def delete_client():

    form = DeleteClientForm()
    session = create_session()
    if form.validate_on_submit():
        client = form.client_list.data
        session.delete(client)
        session.commit()

        client_order = session.query(ClientOrder).where(ClientOrder.id_client == client.id).all()
        print(client_order)
        for note in client_order:
            session.delete(note)
            session.commit()

        session.close()
        return redirect("/")

    return render_template("delete_client.html", form=form)



@router.route("/change_client_choice", methods=["GET", "POST"])
@login_required
def change_client_choice():

    change_client_form = ChangeClientFormFirst()
    if change_client_form.validate_on_submit():
        client = change_client_form.client_list.data
        return redirect(f"/change_client_info/{client.id}")

    return render_template("change_client_first.html", form=change_client_form)


@router.route("/change_client_info/<id_client>", methods=["GET", "POST"])
@login_required
def change_client_info(id_client):

    change_client_form = ChangeClientFormSecond()
    session = create_session()
    client = session.query(Client).where(Client.id == id_client).first()
    if change_client_form.validate_on_submit():
        client.full_name = change_client_form.full_name.data
        client.phone = change_client_form.phone.data
        client.email = change_client_form.email.data
        client.age = change_client_form.age.data
        session.commit()
        session.close()
        return redirect("/")

    return render_template("change_client_second.html", form=change_client_form, client=client)

@router.route("/logout")
def logout():
    logout_user()
    return redirect("/")
