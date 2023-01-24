# require "pg"

class Api::V1::ProductsjoinController < ApplicationController
  def index
    # results = []

    render json: {"message": "products-join response"}, status: 200

  end
end