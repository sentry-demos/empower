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
  
    private
  
  end