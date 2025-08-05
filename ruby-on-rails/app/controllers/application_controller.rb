class ApplicationController < ActionController::API
  def set_Sentry_tags
    Sentry.logger.trace("Starting Sentry tag processing for request %{url}", url: request.original_url)
    
    #TODO: read both request headers and parameters more efficiently
    request.headers.each do |key, value|
      if key.to_s.downcase == "http_se"
        Sentry.logger.debug("Setting SE tag from header: %{value}", value: value)
        Sentry.set_tags('se': value)
        # not tested yet
        if value.to_s.downcase.start_with?('prod-tda-')
          # Sentry.event.fingerprint = [value, ENV["RELEASE"]]
        else
          # Sentry.event.fingerprint = [value]
        end
      elsif key.to_s.downcase == "http_customertype"
        Sentry.logger.debug("Setting customerType tag from header: %{value}", value: value)
        Sentry.set_tags('customerType': value)
      elsif key.to_s.downcase == "http_email"
        Sentry.logger.debug("Setting email tag from header: %{value}", value: value)
        Sentry.set_tags('email': value)
      end
    end

    params.each do |key, value|
      if key.to_s.downcase == "se"
        Sentry.logger.debug("Setting SE tag from params: %{value}", value: value)
        Sentry.set_tags('se': value)
        # not tested yet
        if value.to_s.downcase.start_with?('prod-tda-')
          # Sentry.event.fingerprint = [value, ENV["RELEASE"]]
        else
          # Sentry.event.fingerprint = [value]
        end
      elsif key.to_s.downcase == "customertype"
        Sentry.logger.debug("Setting customerType tag from params: %{value}", value: value)
        Sentry.set_tags('customerType': value)
      elsif key.to_s.downcase == "email"
        Sentry.logger.debug("Setting email tag from params: %{value}", value: value)
        Sentry.set_tags('email': value)
      end
    end
    
    Sentry.logger.info("Completed Sentry tag processing")
  end
end
