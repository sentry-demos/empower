# require "pg"

class Api::V1::ApiController < ApplicationController
  def index
    # results = []

    render json: {"message": "ruby-on-rails /api"}, status: 200

  end
end