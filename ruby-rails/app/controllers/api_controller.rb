class ApiController < ApplicationController

    def api
        print "loading...."
        render json: { "/api": "OK"  }, status: :ok
    end

    def connect
        print "loading...."
        render json: { "/connect": "OK"  }, status: :ok
    end

    def organization
        print "loading...."
        render json: { "/organization": "OK"  }, status: :ok
    end

    def success
        print "loading...."
        render json: { "/success": "OK"  }, status: :ok
    end

    # https://cloud.google.com/ruby/rails/appengine
    # https://cloud.google.com/appengine/docs/flexible/ruby/runtime
    # https://cloud.google.com/appengine/docs/standard/ruby/config/appref runtime ruby27 is for Standard Environment
  
    private
  
  end