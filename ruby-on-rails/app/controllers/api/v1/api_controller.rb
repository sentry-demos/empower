# require "pg"

class Api::V1::ApiController < ApplicationController
  def index
    # results = []

    render json: {"message": "api response"}, status: 200

  end
end