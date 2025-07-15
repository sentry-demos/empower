# require "pg"

class Api::V1::ReviewsController < ApplicationController
  def index
    # get Sentry tags in application_controller.rb
    set_Sentry_tags

    Sentry.logger.info("Fetching all reviews")
    
    reviews = Reviews.all()
    
    Sentry.logger.debug("Retrieved %{count} reviews from database", count: reviews.length)
    
    render json: reviews, status: 200
  end
end