require 'sentry-ruby'

Sentry.init do |config|
  config.dsn = 'https://7bb0e18f77744dc69322e84f72e9769e@o87286.ingest.sentry.io/6227418'
  config.traces_sample_rate = 1.0
  config.traces_sampler = lambda do |sampling_context|
    # sampling_context[:transaction_context] contains the information about the transaction
    # sampling_context[:parent_sampled] contains the transaction's parent's sample decision

    print "\n"
    print sampling_context # can see a trace_id exists
    print "\n"
    
    # I tried `1.0``
    # I tried `return true``
    true # return value can be a boolean or a float between 0.0 and 1.0
  end

  # this doesn't make debugger statements appear.
  config.debug = true
end

# This works, gets captured
Sentry.capture_message 'ruby message'

require "sinatra"
require "sinatra/cors"
set :allow_origin, "*"
set :allow_methods, "GET,HEAD,POST"
set :allow_headers, "content-type,if-modified-since,accept,access-control-request-headers,access-control-request-method,origin,sec-fetch-mode,user-agent,customerType,email,Referer,se,sec-ch-ua,sec-ch-ua-mobile,sec-ch-ua-platform,sentry-trace"

use Sentry::Rack::CaptureExceptions

get "/" do
  "Sentry Ruby Service still says Hello - turn me into a microservice that powers Invoicing, Trucking, or DriverFind"
end

get "/api" do
  # transaction = Sentry.start_transaction(op: "api")
  
  # # not sure if it's required to have a span
  # span = transaction.start_child(op: "op_name", description: "description")
  # span.finish

  # # this didn't make things work either
  # # transaction.with_child_span(op: "process_items", description: "process order's items") do |span|
  # #   span.set_data(:key, "value")
  # # end

  # transaction.finish
  "ruby /api OK"
end

get "/connect" do
  # transaction = Sentry.start_transaction(op: "/connect")
  # transaction.finish
  "ruby /connect OK"
end

get "/organization" do
  # transaction = Sentry.start_transaction(op: "/organization")
  # transaction.finish
  "ruby /organization OK"
end

get "/success" do
  # transaction = Sentry.start_transaction(op: "/success")
  # transaction.finish
  "ruby /success OK"
end