# require "pg"

class Api::V1::CheckoutController < ApplicationController
  def index
    # results = []

    render json: {"message": "checkout response"}, status: 200

  end
end