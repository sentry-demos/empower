Sentry.init do |config|
  config.dsn = ENV['RUBYONRAILS_DSN']
  config.breadcrumbs_logger = [:active_support_logger, :http_logger]

  config.include_local_variables = true

  config.release = ENV['RUBYONRAILS_RELEASE']
  config.environment = ENV['RUBYONRAILS_ENVIRONMENT']

  config.traces_sample_rate = 1.0
  config.profiles_sample_rate = 1.0
  config.profiler_class = Sentry::Vernier::Profiler

  config.enable_logs = true

  #config.before_send = lambda do |event, hint|
    # nothing yet
  #end

end
