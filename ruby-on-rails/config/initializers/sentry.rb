Sentry.init do |config|
  config.dsn = 'https://56904659106448b68eb7a2207babe1e6@o87286.ingest.sentry.io/4504456042774528'
  config.breadcrumbs_logger = [:active_support_logger, :http_logger]

  # TODO: set release which will enable sessions
  # config.release = 'abc'
  config.environment = ENV['RAILS_ENV']

  config.traces_sample_rate = 1.0
end
