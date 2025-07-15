class ApplicationController < ActionController::API
  def set_Sentry_tags
    Sentry.logger.debug("Setting Sentry tags from request headers and parameters")
    
    #TODO: read both request headers and parameters more efficiently
    request.headers.each do |key, value|
      if key.to_s.downcase == "http_se"
        Sentry.set_tags('se': value)
        Sentry.logger.trace("Set SE tag from header: %{value}", value: value)
        # not tested yet
        if value.to_s.downcase.start_with?('prod-tda-')
          # Sentry.event.fingerprint = [value, ENV["RELEASE"]]
        else
          # Sentry.event.fingerprint = [value]
        end
      elsif key.to_s.downcase == "http_customertype"
        Sentry.set_tags('customerType': value)
        Sentry.logger.trace("Set customerType tag from header: %{value}", value: value)
      elsif key.to_s.downcase == "http_email"
        Sentry.set_tags('email': value)
        Sentry.logger.trace("Set email tag from header: %{value}", value: value)
      end
    end

    params.each do |key, value|
      if key.to_s.downcase == "se"
        Sentry.set_tags('se': value)
        Sentry.logger.trace("Set SE tag from param: %{value}", value: value)
        # not tested yet
        if value.to_s.downcase.start_with?('prod-tda-')
          # Sentry.event.fingerprint = [value, ENV["RELEASE"]]
        else
          # Sentry.event.fingerprint = [value]
        end
      elsif key.to_s.downcase == "customertype"
        Sentry.set_tags('customerType': value)
        Sentry.logger.trace("Set customerType tag from param: %{value}", value: value)
      elsif key.to_s.downcase == "email"
        Sentry.set_tags('email': value)
        Sentry.logger.trace("Set email tag from param: %{value}", value: value)
      end
    end
    
    Sentry.logger.debug("Sentry tags setup completed")
  end
end
