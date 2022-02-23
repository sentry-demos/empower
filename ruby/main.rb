# Copyright 2015 Google, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_flex_quickstart]
require "sinatra"

# https://github.com/jdesrosiers/sinatra-cors
# require "sinatra/cors"
# set :allow_origin, "http://localhost:5000"
# set :allow_methods, "GET,HEAD,POST"
# set :allow_headers, "content-type,if-modified-since"
# set :expose_headers, "location,link"


# TODO install Sentry
# TODO call these from frontend
# 0 cors problemn need sinatra/cors
# 1 bundle install, fails due to racc problem
# 2 set cors policy manually in response, also fails
require 'sentry-ruby'

Sentry.init do |config|
  config.dsn = 'https://7bb0e18f77744dc69322e84f72e9769e@o87286.ingest.sentry.io/6227418'
  config.traces_sample_rate = 1.0
  config.traces_sampler = lambda do |sampling_context|
    print "> happening..."
    # control sampling dynamically
    # sampling_context[:transaction_context] contains the information about the transaction
    # sampling_context[:parent_sampled] contains the transaction's parent's sample decision
    true # return value can be a boolean or a float between 0.0 and 1.0
  end
end

get "/" do
  "Sentry Ruby Service still says Hello - turn me into a microservice that powers Invoicing, Trucking, or DriverFind"
end
# [END gae_flex_quickstart]

# SINATRA won't have good auto-instrumentation support for Tracing

get "/api" do
  print "loading...."
  "ruby /api OK"
end

get "/connect" do
  print "loading...."
  "ruby /connect OK"
end

get "/organization" do
  print "loading...."
  "ruby /organization OK"
end

get "/success" do
  
  print "loading...."
  # doesn't work
  # headers 'Access-Control-Allow-Origin' => 'http://localhost:3000'
  # response.headers["Access-Control-Allow-Origin"] = "*"

  # doesn't work
  # content_type :json    
  # headers 'Access-Control-Allow-Origin' => '*', 
  # 'Access-Control-Allow-Methods' => ['OPTIONS', 'GET', 'POST']  
  
  "ruby /success OK"
end