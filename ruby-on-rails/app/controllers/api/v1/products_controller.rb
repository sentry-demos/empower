# require "pg"

class Api::V1::ProductsController < ApplicationController
  def index
    # results = []

    products = Products.all

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
