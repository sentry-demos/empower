class TestController < ApplicationController

    def success
        print "Processing...."
        render json: { "/success": "OK"  }, status: :ok
    end
  
    private
  
  end