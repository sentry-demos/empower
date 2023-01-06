# require "pg"

class Api::V1::ProductsController < ApplicationController
  def index
    results = []
    conn = PG::Connection.new( "postgresql://#{ENV['USERNAME']}:#{ENV['PASSWORD']}@#{ENV['PG_HOST']}:5432/#{ENV['DATABASE']}" )
    # ^ TODO: google cloud sql format

    # print Rails.const_defined? 'Console' # false when rails s, false when rackup
    # print Rails.const_defined? 'Server' # true when rails s, false when rackup

    results = conn.exec("SELECT *, pg_sleep(1) FROM products")

    render json: results, status: 200
  end

  def show
  end

  def handled
        begin
            '2' + 3
        rescue Exception => exception
            Sentry.capture_exception(exception)
            render json: { "ERROR": exception.message  }, status: :ok
        end
    end

    def unhandled
      1 / 0
    end
end
