# require "pg"

class Api::V1::OrganizationController < ApplicationController
  def index
    # results = []

    render json: {"message": "rails /organization"}, status: 200

  end
end