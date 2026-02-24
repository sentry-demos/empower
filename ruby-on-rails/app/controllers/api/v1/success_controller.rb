# require "pg"

class Api::V1::SuccessController < ApplicationController

  # -- below was for testing a client issue, remove after confirmation client resolved issue --
  # class Box
  #   # constructor method
  #   def initialize(w,h)
  #      @width, @height = w, h
  #   end

  #   # accessor methods
  #   def printWidth
  #      @width
  #   end
 
  #   def printHeight
  #      @height
  #   end
  # end

  def index
    Sentry.logger.info("Success endpoint accessed")
    render json: {"message": "success from ruby-on-rails"}, status: 200
    # -- below was for testing a client issue, remove after confirmation client resolved issue --
    # # results = []
    # testval_nil = nil # results in messages sent, but no tag created

    # testval_obj = Box.new(10,10) # works as expected, tag is created and holds
    # testval_obj_accessor = testval_obj.printWidth() # works as expected
    # testval_arr = ["1", "2", "3"] # works as expected, tag created (shows value as invalid with message "expected a primitive value")
    # testval_arr_empty = [] # works as expected, tag created (shows value as invalid with message "expected a primitive value")
    # testval_b = false # works as expected, tag created
    # testval_i = 42 # works as expected, tag created
    # testval_s = "string" # works as expected, tag created
    # testval = testval_nil
    # Sentry.with_scope do |scope|
    #   scope.set_tags(test_tag: testval)
    #   Sentry.capture_message("test with_scope") 
    # end
  end
end