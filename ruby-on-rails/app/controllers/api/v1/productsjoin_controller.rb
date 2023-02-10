# require "pg"

class Api::V1::ProductsjoinController < ApplicationController
  def index
    # used to test reviews db calls, may reuse for more elegant product call
    reviews = Reviews.all()
    render json: reviews, status: 200
    #render json: {"message": "products-join response"}, status: 200

  end
end