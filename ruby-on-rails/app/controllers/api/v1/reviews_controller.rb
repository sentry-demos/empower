# require "pg"

class Api::V1::ReviewsController < ApplicationController
  def index
    # results = []
    reviews = Reviews.all()
    render json: reviews, status: 200
    #render json: {"message": "products-join response"}, status: 200

  end
end