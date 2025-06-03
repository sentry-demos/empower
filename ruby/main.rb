require 'sentry-ruby'
require 'dotenv'

Dotenv.load('gloud-ignore-workaround.env')

Sentry.init do |config|
  config.dsn = ENV['RUBY_DSN']
  config.release = "22.8.2"
  config.traces_sample_rate = 1.0
  config.traces_sampler = lambda do |sampling_context|

    request_method = sampling_context[:env]["REQUEST_METHOD"]
    if request_method == "OPTIONS"
      return 0.0
    end

    transaction_context = sampling_context[:transaction_context]
    transaction_name = transaction_context[:name]
    if transaction_name == "/favicon.ico"
      return 0.0
    end
    
    true
  end
end

# This must be imported after sentry-ruby for transactions to work
require "sinatra"
require "sinatra/cors"

set :allow_origin, "*"
set :allow_methods, "GET,HEAD,POST"
set :allow_headers, "content-type,if-modified-since,accept,access-control-request-headers,access-control-request-method,origin,sec-fetch-mode,user-agent,customerType,email,Referer,se,sec-ch-ua,sec-ch-ua-mobile,sec-ch-ua-platform,sentry-trace"

# This is for Auto Instrumenting the transaction
use Sentry::Rack::CaptureExceptions

before do
  se = request.env["HTTP_SE"]
  if !se.nil?
    Sentry.set_tags("se": se)
  end

  customerType = request.env["HTTP_CUSTOMERTYPE"]
  if !customerType.nil?
    Sentry.set_tags("customerType": customerType)
  end

  email = request.env["HTTP_EMAIL"]
  if !email.nil?
    Sentry.set_user(email: email)
  end
end

get "/" do
  "Sentry Ruby Service says Hello - turn me into a microservice that powers Invoicing, Trucking, or DriverFind"
end

get "/api" do
  "ruby /api"
end

get "/connect" do
  "ruby /connect"
end

get "/organization" do
  "ruby /organization"
end

get "/success" do
  "ruby /success"
end
