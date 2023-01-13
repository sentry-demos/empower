Sentry.init do |config|
  config.dsn = ENV['RUBYONRAILS_APP_DSN']
  config.breadcrumbs_logger = [:active_support_logger, :http_logger]

  config.release = ENV['RELEASE']
  config.environment = ENV['RAILS_ENV'] || "development"

  config.traces_sample_rate = 1.0
end
