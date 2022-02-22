class ApiController < ApplicationController

    def organization
        print "loading...."
        render json: { "/organization": "OK"  }, status: :ok
    end
  
    private
  
  end