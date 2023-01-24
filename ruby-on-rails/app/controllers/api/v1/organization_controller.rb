# require "pg"

class Api::V1::OrganizationController < ApplicationController
  def index
    # results = []

    render json: {"message": "organization response"}, status: 200

  end
end