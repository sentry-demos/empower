Sentry.init do |config|
  config.dsn = ENV['RUBYONRAILS_APP_DSN']
  config.breadcrumbs_logger = [:active_support_logger, :http_logger]

  config.release = ENV['RELEASE']
  config.environment = ENV['RUBYONRAILS_RAILS_ENV'] || "development"

  config.traces_sample_rate = 1.0
  params = CGI.parse(uri.query)
  if(params['se'].first != nil)
    config.set_tags('se': params['se'].first)
  end
end
