Sentry.init do |config|
  config.dsn = ENV['RUBYONRAILS_APP_DSN']
  config.breadcrumbs_logger = [:active_support_logger, :http_logger]

  #config.include_local_variables = true

  config.release = ENV['RELEASE']
  config.environment = ENV['RUBYONRAILS_RAILS_ENV'] || "development"

  config.traces_sample_rate = 1.0
  config.profiles_sample_rate = 1.0
  config.profiler_class = Sentry::Vernier::Profiler

  # Enable comprehensive logging
  config.enable_logs = true

  # Configure logger for better debugging (adjust level as needed)
  # config.sdk_logger = Rails.logger
  # config.sdk_logger.level = ::Logger::INFO # Change to DEBUG for more verbose logging

  # Optional: Enable debug mode for development
  if Rails.env.development?
    config.debug = true
  end
end
