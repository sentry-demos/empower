# require "pg"

class Api::V1::ReviewsController < ApplicationController
  def index
    reviews = Reviews.all()
    render json: reviews, status: 200
  end
end