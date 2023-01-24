# require "pg"

class Api::V1::SuccessController < ApplicationController
  def index
    # results = []

    render json: {"message": "success response"}, status: 200

  end
end