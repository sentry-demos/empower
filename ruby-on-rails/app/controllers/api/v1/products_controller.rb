# require "pg"

class Api::V1::ProductsController < ApplicationController
  def index
    # get Sentry tags in application_controller.rb
    set_Sentry_tags

    # TODO: may want to introduce extra db calls here
    # call to products db. may span around this?
    products = Products.select("id, title, description, descriptionfull, price, img, imgcropped, Null as pg_sleep, Null as reviews")
    # call to reviews db. may span around this?
    reviews = Reviews.select("id, productid, rating, customerid, description, created, Null as pg_sleep")
    
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

    render json: products, status: 200
  end

  # sent here if unexpected route was enterered
  def default 
    # get Sentry tags in application_controller.rb
    set_Sentry_tags

    begin
      # TODO: capture route attempted to include in the exception
      Sentry.capture_message "message: bad route response"
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
