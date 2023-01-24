# require "pg"

class Api::V1::ConnectController < ApplicationController
  def index
    # results = []

    render json: {"message": "connect response"}, status: 200

  end
end