# require "pg"

class Api::V1::ConnectController < ApplicationController
  def index
    # results = []

    render json: {"message": "rails /connect"}, status: 200

  end
end