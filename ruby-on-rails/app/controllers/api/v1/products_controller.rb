class Api::V1::ProductsController < ApplicationController
  def index
    # get Sentry tags in application_controller.rb
    set_Sentry_tags

    transaction = Sentry.get_current_scope.get_transaction || Sentry.start_transaction(name: "custom transaction")

    span_products_db = transaction.start_child(op: "custom.products_db_call")
    sleep 0.5
    products = Products.select("id, title, description, descriptionfull, price, img, imgcropped, Null as pg_sleep, Null as reviews")
    sleep 0.5
    span_products_db.finish

    span_reviews_db = transaction.start_child(op: "custom.reviews_db_call")
    sleep 0.5
    reviews = Reviews.select("id, productid, rating, customerid, description, created, Null as pg_sleep")
    sleep 0.5
    span_reviews_db.finish

    span_response = transaction.start_child(op: "custom.construct_response_object")
    products.each do |prod|  
      prod["pg_sleep"] = ""
      reviews_arr = []
      reviews.each do |review|
        if prod.id == review.productid
          reviews_arr.push(*review)
        end
      prod["reviews"] = reviews_arr
      end
    end
    span_response.finish

    render json: products, status: 200
  end

  # sent here if unexpected route was enterered
  def default 
    # get Sentry tags in application_controller.rb
    set_Sentry_tags

    begin
      unless request.original_url.include?("favicon.ico")
        Sentry.capture_message "message: bad route response --> " + request.original_url
      end
      render json: {"message": "bad route response"}, status: :ok
    end
  end

  def show
  end

  def handled
    # get Sentry tags in application_controller.rb
    set_Sentry_tags

    begin
      '2' + 3
    rescue Exception => exception
      Sentry.capture_exception(exception)
      render json: { "ERROR": exception.message  }, status: :ok
    end
  end

  def unhandled
    # get Sentry tags in application_controller.rb
    set_Sentry_tags

    1 / 0
  end
end
