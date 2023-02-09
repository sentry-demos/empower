# require "pg"

class Api::V1::ProductsController < ApplicationController
  def index
    # results = []
    #logger.debug("debug::" + "messageNEW2")
    
    #logger.debug("debug::" + pr.to_yaml)
    
    # products2 = products.all()
    #logger.debug("debug::" + products.to_yaml)
    products = Products.select("id, title, description, descriptionfull, price, img, imgcropped, Null as pg_sleep, Null as reviews")
    #products = Products.all.includes(:review).where('products.id = ?', 'productid').references(:review)
    #products = Reviews.select('*').joins(:products)
    reviews = Reviews.select("id, productid, rating, customerid, description, created, Null as pg_sleep")

    #products = Products.joins(:review).select("products.*,reviews.*")
    #products = reviews.column_names
    #products = Products.select('*').joins(:review)
    #products = Products.select('*').joins(:review).where("products.id = reviews.productid")
    #products = Reviews.all()

    
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

  def default
    begin
        # TODO: capture route attempted to include in the exception
        Sentry.capture_message "message: bad route response"
        render json: {"message": "bad route response"}, status: :ok
    end
  end

  def show
  end

  def handled
        begin
            '2' + 3
        rescue Exception => exception
            Sentry.capture_exception(exception)
            render json: { "ERROR": exception.message  }, status: :ok
        end
  end

  def unhandled
      1 / 0
  end
end
