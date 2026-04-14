# require "pg"

class Api::V1::OrganizationController < ApplicationController
  def index
    # results = []

    render json: {"message": "ruby-on-rails /organization"}, status: 200

  end
end