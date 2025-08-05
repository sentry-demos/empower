# require "pg"

class Api::V1::ReviewsController < ApplicationController
  def index
    Sentry.logger.info("Starting reviews index request")
    Sentry.logger.trace("Starting reviews database connection")
    reviews = Reviews.all()
    Sentry.logger.trace("Completed reviews query, found %{count} reviews", count: reviews.length)
    Sentry.logger.info("Reviews index completed successfully")
    render json: reviews, status: 200
  end
end