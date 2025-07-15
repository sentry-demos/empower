# require "pg"

class Api::V1::ProductsjoinController < ApplicationController
  def index
    # get Sentry tags in application_controller.rb
    set_Sentry_tags

    Sentry.logger.info("Starting products join operation")

    transaction = Sentry.get_current_scope.get_transaction || Sentry.start_transaction(name: "custom transaction")

    #span_products_db = transaction.start_child(op: "custom.products_db_call")
    Sentry.logger.trace("Starting database connection %{database}", database: "products")
    sleep 0.25
    products = Products.select("id, title, description, descriptionfull, price, img, imgcropped, Null as pg_sleep, Null as reviews")
    sleep 0.25
    #span_products_db.finish
    
    Sentry.logger.debug("Retrieved %{count} products for join operation", count: products.length)
    
    # n+1 to db if done this way
    # products.each do |prod_slow|
    #   span_products_slow_db = transaction.start_child(op: "custom.reviews_slow_db_call")
    #   prod_slow["pg_sleep"] = ""
    #   prod_slow["reviews"] = []
    #   prod_slow["reviews"] = Reviews.select("id, productid, rating, customerid, description, created, Null as pg_sleep").where("productid="+prod_slow.id.to_s)
    #   span_products_slow_db.finish
    # end

    # fewer db calls this way - done in products controller
    #span_reviews_db = transaction.start_child(op: "custom.reviews_db_call")
    Sentry.logger.trace("Starting database connection %{database}", database: "reviews")
    sleep 0.25
    reviews = Reviews.select("id, productid, rating, customerid, description, created, Null as pg_sleep")
    sleep 0.25
    #span_reviews_db.finish

    Sentry.logger.debug("Retrieved %{count} reviews for join operation", count: reviews.length)

    #span_response = transaction.start_child(op: "custom.construct_response_object")
    Sentry.logger.trace("Constructing joined response object")
    products = products.map do |prod|
      prod_attrs = prod.attributes
      prod_attrs["pg_sleep"] = ""
      reviews_arr = []
      reviews.each do |review|
        if prod.id == review.productid
          reviews_arr.push(review.as_json)
        end
      end
      prod_attrs["reviews"] = reviews_arr
      prod_attrs
    end
    #span_response.finish

    Sentry.logger.info("Products join operation completed successfully")
    render json: products, status: 200
  end
end