class Api::V1::ProductsController < ApplicationController
  def index
    # get Sentry tags in application_controller.rb
    set_Sentry_tags

    Sentry.logger.info("Fetching products list")

    transaction = Sentry.get_current_scope.get_transaction || Sentry.start_transaction(name: "custom transaction")

    span_products_db = transaction.start_child(op: "custom.products_db_call")
    Sentry.logger.trace("Starting database connection %{database}", database: "products")
    sleep 0.25
    products = Products.select("id, title, description, descriptionfull, price, img, imgcropped, Null as pg_sleep, Null as reviews")
    sleep 0.25
    span_products_db.finish
    
    Sentry.logger.debug("Retrieved %{count} products from database", count: products.length)
    
    # n+1 to db if done this way
    products = products.map do |prod|
      span_products_slow_db = transaction.start_child(op: "custom.reviews_slow_db_call")
      Sentry.logger.trace("Fetching reviews for product %{product_id}", product_id: prod.id)
      prod_attrs = prod.attributes
      prod_attrs["pg_sleep"] = ""
      prod_attrs["reviews"] = []
      prod_attrs["reviews"] = Reviews.select("id, productid, rating, customerid, description, created, Null as pg_sleep").where("productid="+prod.id.to_s).as_json
      span_products_slow_db.finish
      
      Sentry.logger.debug("Found %{review_count} reviews for product %{product_id}", 
                         review_count: prod_attrs["reviews"].length, product_id: prod.id)
      prod_attrs
    end

    # fewer db calls this way -- done in products-join
    # span_reviews_db = transaction.start_child(op: "custom.reviews_db_call")
    # sleep 0.25
    # reviews = Reviews.select("id, productid, rating, customerid, description, created, Null as pg_sleep")
    # sleep 0.25
    # span_reviews_db.finish

    # span_response = transaction.start_child(op: "custom.construct_response_object")
    # products.each do |prod|  
    #   prod["pg_sleep"] = ""
    #   reviews_arr = []
    #   reviews.each do |review|
    #     if prod.id == review.productid
    #       reviews_arr.push(*review)
    #     end
    #   prod["reviews"] = reviews_arr
    #   end
    # end
    # span_response.finish

    Sentry.logger.info("Products list successfully retrieved and formatted")
    render json: products, status: 200
  end

  # sent here if unexpected route was enterered
  def default 
    # get Sentry tags in application_controller.rb
    set_Sentry_tags

    Sentry.logger.warn("Unexpected route accessed in products controller")
    
    products = Products.select("id, title, description, descriptionfull, price, img, imgcropped, Null as pg_sleep, Null as reviews")
    render json: products, status: 200
  end

  def show
    # get Sentry tags in application_controller.rb
    set_Sentry_tags

    Sentry.logger.info("Fetching individual product details")

    transaction = Sentry.get_current_scope.get_transaction || Sentry.start_transaction(name: "custom transaction")

    span_products_db = transaction.start_child(op: "custom.products_db_call")
    product = Products.find(params[:id])
    span_products_db.finish

    Sentry.logger.debug("Retrieved product %{product_id}: %{title}", 
                       product_id: product.id, title: product.title)

    render json: product, status: 200
  end

  def handled
    # get Sentry tags in application_controller.rb
    set_Sentry_tags

    begin
      '2' + 3
    rescue Exception => exception
      Sentry.capture_exception(exception)
      render json: { "ERROR": exception.message }, status: :ok
    end
  end

  def unhandled
    # get Sentry tags in application_controller.rb
    set_Sentry_tags

    1 / 0
  end
end
