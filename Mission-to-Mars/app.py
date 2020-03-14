from flask import Flask, render_template, redirect, url_for
from flask_pymongo import PyMongo
import scrape_mars

# Create an instance of Flask
app = Flask(__name__)

# Use PyMongo to establish Mongo connection
mongo = PyMongo(app, uri="mongodb://localhost:27017/mars_db")


# Route to render index.html template using data from Mongo
@app.route("/")
def home():

    # Find one record of data from the mongo database, making sure it's the latest that was tossed in
    mars_master_info = mongo.db.mars_master_info.find_one(sort=[("collection_timestamp", -1)])

    # Return template and data
    return render_template( "index.html", mars_data=mars_master_info )


# Route that will trigger the scrape function
@app.route("/scrape")
def scrape():

    # Run the scrape function
    new_mars_data = scrape_mars.scrape()

    print(new_mars_data)

    # Update the Mongo database using update and upsert=True
    mongo.db.mars_master_info.update({}, new_mars_data, upsert=True)

    # Redirect back to home page
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
 