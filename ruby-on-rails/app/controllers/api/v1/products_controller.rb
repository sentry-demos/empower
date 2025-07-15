class Api::V1::ProductsController < ApplicationController
  def index
    Sentry.logger.info("Starting products index request")
    
    # get Sentry tags in application_controller.rb
    set_Sentry_tags

    transaction = Sentry.get_current_scope.get_transaction || Sentry.start_transaction(name: "custom transaction")

    Sentry.logger.trace("Starting products database connection")
    span_products_db = transaction.start_child(op: "custom.products_db_call")
    sleep 0.25
    products = Products.select("id, title, description, descriptionfull, price, img, imgcropped, NULL as pg_sleep, NULL as reviews")
    sleep 0.25
    span_products_db.finish
    Sentry.logger.trace("Completed products database query, found %{count} products", count: products.count)
    
    # n+1 to db if done this way
    Sentry.logger.warn("Using N+1 query pattern for reviews - performance impact expected")
    products = products.map do |prod|
      span_products_slow_db = transaction.start_child(op: "custom.reviews_slow_db_call")
      Sentry.logger.trace("Fetching reviews for product %{product_id}", product_id: prod.id)
      prod_attrs = prod.attributes
      prod_attrs["pg_sleep"] = ""
      prod_attrs["reviews"] = []
      prod_attrs["reviews"] = Reviews.select("id, productid, rating, customerid, description, created, NULL as pg_sleep").where("productid="+prod.id.to_s).as_json
      span_products_slow_db.finish
      Sentry.logger.debug("Found %{review_count} reviews for product %{product_id}", review_count: prod_attrs["reviews"].count, product_id: prod.id)
      prod_attrs
    end

    # fewer db calls this way -- done in products-join
    # span_reviews_db = transaction.start_child(op: "custom.reviews_db_call")
    # sleep 0.25
    # reviews = Reviews.select("id, productid, rating, customerid, description, created, NULL as pg_sleep")
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

    Sentry.logger.info("Products index completed successfully, returning %{count} products", count: products.count)
    render json: products, status: 200
  end

  # sent here if unexpected route was enterered
  def default 
    Sentry.logger.warn("Bad route accessed: %{url}", url: request.original_url)
    
    # get Sentry tags in application_controller.rb
    set_Sentry_tags

    begin
      unless request.original_url.include?("favicon.ico")
        Sentry.logger.error("Unexpected route accessed: %{url}", url: request.original_url)
        Sentry.capture_message "message: bad route response --> " + request.original_url
      end
      render json: {"message": "bad route response"}, status: :ok
    end
  end

  def show
    Sentry.logger.info("Product show action called")
  end

  def handled
    Sentry.logger.info("Handled exception test endpoint called")
    
    # get Sentry tags in application_controller.rb
    set_Sentry_tags

    begin
      '2' + 3
    rescue Exception => exception
      Sentry.logger.error("Handled exception in test endpoint: %{error}", error: exception.message)
      Sentry.capture_exception(exception)
      render json: { "ERROR": exception.message }, status: :ok
    end
  end

  def unhandled
    Sentry.logger.warn("Unhandled exception test endpoint called - this will cause an error")
    
    # get Sentry tags in application_controller.rb
    set_Sentry_tags

    1 / 0
  end
end
