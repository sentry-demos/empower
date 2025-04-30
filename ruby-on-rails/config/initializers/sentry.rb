Sentry.init do |config|
  config.dsn = ENV['RUBYONRAILS_DSN']
  config.breadcrumbs_logger = [:active_support_logger, :http_logger]

  #config.include_local_variables = true

  config.release = ENV['RELEASE']
  config.environment = ENV['RUBYONRAILS_RAILS_ENV'] || "development"

  config.traces_sample_rate = 1.0

  #config.before_send = lambda do |event, hint|
    # nothing yet
  #end

end
