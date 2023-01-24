# require "pg"

class Api::V1::MainController < ApplicationController
  def index
    # results = []

    render json: {"message": "main page"}, status: 200

  end
end