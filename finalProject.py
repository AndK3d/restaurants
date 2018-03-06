from flask import Flask, render_template, url_for, request, redirect, jsonify, flash

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Making an API Endpoint (GET request)
@app.route('/restaurants/JSON')
def restaurantsListJSON():
    restaurants = session.query(Restaurant).all()
    return jsonify(restaurantsList=[i.serialize for i in restaurants])


@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def showMenuJSON(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id).all()
    return jsonify(MenuItems=[i.serialize for i in items])


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menuItem_Id>/JSON')
def MenuItemJSON(restaurant_id, menuItem_Id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    item = session.query(MenuItem).filter_by(id = menuItem_Id).all()
    return jsonify(MenuItem=[i.serialize for i in item])


# Page 1: Create route for All Restaurants List function here
@app.route('/')
@app.route('/restaurants/')
def restaurantsList():

    restaurants = session.query(Restaurant)

    return render_template('restaurants.html', restaurants = restaurants)


# Page 2: Create route for "New Restaurant Page" function here
@app.route('/restaurant/new', methods = ['GET', 'POST'])
def newRestaurant():

    if request.method == 'POST':
        newRestaurant = Restaurant(name=request.form['name'])
        session.add(newRestaurant)
        session.commit()

        # flash message
        flash("restaurant successfully created!")
        return redirect(url_for('restaurantsList'))

    if request.method == 'GET':
        return render_template('newRestaurant.html')


# Page 3: Create route for "Edit Restaurant Page" function here
@app.route('/restaurant/<int:restaurant_id>/edit', methods = ['GET', 'POST'])
def editRestaurant(restaurant_id):
    editedRestaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedRestaurant.name = request.form['name']
            session.add(editedRestaurant)
            session.commit()

            # flash message
            flash("restaurant successfully edited!")
            return redirect(url_for('restaurantsList'))

    if request.method == 'GET':
        return render_template('editRestaurant.html', restaurant_id=restaurant_id, restaurant_name=editedRestaurant.name)


# Page 4: Create route for "Delete Restaurant Page" function here
@app.route('/restaurant/<int:restaurant_id>/delete', methods = ['GET', 'POST'])
def deleteRestaurant(restaurant_id):

    if request.method == 'POST':
        deletedRestaurant = session.query(Restaurant).filter_by(id=restaurant_id).delete(synchronize_session ='fetch')
        session.commit()

        # flash message
        flash("restaurant successfully deleted!")
        return redirect(url_for('restaurantsList'))

    if request.method == 'GET':
        deletedRestaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
        return render_template('deleteRestaurant.html', restaurant=restaurant_id, restaurant_name=deletedRestaurant.name)

    return

# Page 5: Create route for "Restaurant Menu Page" function here
@app.route('/restaurant/<int:restaurant_id>/')
@app.route('/restaurant/<int:restaurant_id>/menu')
def showMenu(restaurant_id):

    menuItems = session.query(MenuItem).filter_by(restaurant_id=restaurant_id)
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()

    if request.method == 'GET':
        return render_template('menu.html', restaurant_id=restaurant.id, restaurant_name = restaurant.name,
                               items = menuItems)


# Page 6: Create route for "Add a Menu Item Page" function here
@app.route('/restaurant/<int:restaurant_id>/menu/new', methods = ['GET', 'POST'])
def addMenuItem(restaurant_id):

    if request.method == 'POST':

        newMenuItem = MenuItem(name=request.form['name'],
                               description=request.form['description'],
                               price = request.form['price'],
                               course = request.form['course'],
                               restaurant_id=restaurant_id)
        session.add(newMenuItem)
        session.commit()

        # flash message
        flash("new menu item successfully created!")
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))

    if request.method == 'GET':
        return render_template('newmenuitem.html', restaurant_id=restaurant_id)


# Page 7: Create route for "Edit a Menu Item Page" function here
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menuItem_id>/edit', methods = ['GET', 'POST'])
def editMenuItem(restaurant_id, menuItem_id):

    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    menuItem = session.query(MenuItem).filter_by(id=menuItem_id).one()

    print(menuItem)

    if request.method == 'POST':
        if request.form['name']:
            menuItem.name = request.form['name']

        if request.form['description']:
            menuItem.description = request.form['description']

        if request.form['price']:
            menuItem.price = request.form['price']

        if request.form['course']:
            menuItem.course = request.form['course']

        session.add(menuItem)
        session.commit()

        # flash message
        flash("menu item successfully edited!")
        return redirect(url_for('showMenu', restaurant_id=restaurant.id))

    if request.method == 'GET':
        return render_template('editmenuitem.html', restaurant=restaurant, menuItem=menuItem)


# Page 8: Create route for "Delete a Menu Item Page" function here
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menuItem_id>/delete', methods = ['GET', 'POST'])
def deleteMenuItem(restaurant_id, menuItem_id):

    deletedMenuItem = session.query(MenuItem).filter_by(id=menuItem_id).one()

    if request.method == 'POST':
        result = session.query(MenuItem).filter_by(id=menuItem_id).delete(synchronize_session='fetch')
        session.commit()

        # flash message
        flash("menu item successfully deleted!")
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))

    if request.method == 'GET':
        return render_template('deletemenuitem.html', restaurant=restaurant_id, item=deletedMenuItem)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
