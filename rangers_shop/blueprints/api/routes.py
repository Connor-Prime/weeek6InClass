from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required
from rangers_shop.models import Customer, Product, ProdOrder, Order, db, product_schema, products_schema

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/token', methods = ['GET', 'POST'])
def token():

    data = request.json

    if data:
        client_id = data['client_id']
        access_token = create_access_token(identity=client_id)
        return {
            'status':200,
            'acess_token': access_token
        }
    else:
        return{
        'status':200,
        'message': 'Missing client id. Try again'
        }
    

@api.route('/shop')
@jwt_required()
def get_shop():
    # List of objects
    allprods = Product.query.all()

    # Change to dicts/ jsonify

    repronse = products_schema.dump(allprods)
    return jsonify(repronse)


@api.route('/order/create/<cust_id>', methods=['POST']) #
@jwt_required()
def create_order(cust_id):

    data = request.json

    customer_order = data['order']

    customer = Customer.query.filter(Customer.cust_id==cust_id).first()

    if not customer:
        customer = Customer(cust_id)
        db.session.add(customer)

    order = Order()
    db.session.add(order)

    for product in customer_order:
        prodorder=ProdOrder(product['prod_id'], product['quantity'], product['price'], order.order_id, customer.cust_id)
        db.session.add(prodorder)

        order.increment_order_total(prodorder.price)

        current_product  = Product.query.get(product['prod_id'])

        current_product.decrement_quantity(product['quantity'])
    
    db.session.commit()

    return{
        'status':200,
        'message':'New order was created'
    }

@api.route('/order/<cust_id>')
@jwt_required()
def get_orders(cust_id):
    prodorders = ProdOrder.query.filter(ProdOrder.cust_id==cust_id).all()

    data =[]

    for order in prodorders:
        product = Product.query.filter(Product.prod_id==order.prod_id).first()

        product_dict = product_schema.dump(product)

        product_dict['quantity'] = order.quantity
        product_dict['order_id'] = order.order_id
        product_dict['id'] = order.prodorder_id

        data.append(product_dict)
    
    return jsonify(data)


@api.route('/order/update/<order_id>', methods = ['PUT']) #whenever we are updating we using PUT
@jwt_required()
def update_order(order_id):

    data = request.json
    new_quantity = int(data['quantity'])
    prod_id = data['prod_id']


    prodorder = ProdOrder.query.filter(ProdOrder.order_id == order_id, ProdOrder.prod_id == prod_id).first()
    order = Order.query.get(order_id)
    product = Product.query.get(prod_id)



    prodorder.set_price(product.price, new_quantity)


    diff = abs(new_quantity - prodorder.quantity)

    if product.quantity > new_quantity:
        product.increment_quantity(diff)     #put some products back
        order.decrement_order_total(prodorder.price)
    elif prodorder.quantity < new_quantity:
        product.decrement_quantity(diff)
        order.increment_order_total(prodorder.price)

    prodorder.update_quantity(new_quantity)

    db.session.commit()


    return{
        'status':200,
        'message':'Order was updated successfully'

    }


@api.route('/order/delete/<order_id>', methods = ['DELETE'])
@jwt_required()
def delete_order(order_id):

    data = request.json
    prod_id = data['prod_id']


    prodorder = ProdOrder.query.filter(ProdOrder.order_id == order_id, ProdOrder.prod_id == prod_id).first()
    order = Order.query.get(order_id)
    product = Product.query.get(prod_id)


    order.decrement_order_total(prodorder.price)
    product.increment_quantity(prodorder.quantity)

    db.session.delete(prodorder)
    db.session.commit()

    return {
        'status' : 200,
        'message': 'Order was Deleted Successfully'
    }

