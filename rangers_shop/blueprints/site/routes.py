from flask import Blueprint, flash, redirect, render_template 


# internal imports
from rangers_shop.models import Product, Customer, Order, db
from rangers_shop.forms import ProductForm
from flask import request

#need to instantiate our Blueprint class
site = Blueprint('site', __name__, template_folder='site_templates' )


#use site object to create our routes
@site.route('/')
def shop():

    # Query database for products

    products = Product.query.all() #select all from products/ SELECT * from Products

    allcustomers = Customer.query.all()
    allorders = Order.query.all()

    # making dict for shop stats/info

    shop_stats = {
        'products' : len(products),
        'sales' : sum([order.order_total for order in allorders]),
        'customers': len(allcustomers)
    }

                          #html page   #variables
    return render_template('shop.html', shop = products, stats = shop_stats) #looking inside our template_folder (site_templates) to find our shop.html fil

@site.route('/shop/create', methods=['GET', 'POST'])
def create():

    createform = ProductForm()

    if request.method == 'POST' and createform.validate_on_submit():

        name = createform.name.data
        image= createform.image.data
        description = createform.price.data
        price = createform.quantity.data
        quantity = createform.quantity.data


        product = Product(name,price, quantity,image,description)

        db.session.add(product)
        db.session.commit()

        flash(f"You have successfully added {name} to the shop.", category='success')
        return redirect('/')
    elif request.method == 'POST':
        flash("We were unable to process your request.", category='warning')
        return redirect('/')
    
    return render_template('create.html', form=createform)

@site.route('/shop/update/<id>', methods = ['GET','POST']) #pass parameter to our routes
def update(id):

    # Grabbing product with id
    product = Product.query.get(id)
    updateform = ProductForm()

    if request.method=='POST':
        product.name = updateform.name.data
        product.image = updateform.image.data
        product.description = updateform.description.data
        product.price = updateform.price.data
        product.quantity = updateform.quantity.data

        db.session.commit()

        flash(f"You have successfully updated product {product.name}", category='success')
        return redirect('/')
    elif request.method == 'POST':
        flash("We were unable to process your request.", category='warning')
        return redirect('/')
    
    return render_template('update.html', form=updateform, product=product)

@site.route('/shop.delete/<id>')
def delete(id):

    product = Product.query.get(id)

    db.session.delete(product)

    db.session.commit()

    return redirect('/')
