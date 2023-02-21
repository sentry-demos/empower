class ApplicationController < ActionController::API
  def set_Sentry_tags
    #TODO: read both request headers and parameters more efficiently

    request.headers.each do |key, value|
      if key.to_s.downcase == "se"
        Sentry.set_tags('se': value)
        # not tested yet
        if value.to_s.downcase == "tda"
          # Sentry.event.fingerprint = [value, ENV["RELEASE"]]
        else
          # Sentry.event.fingerprint = [value]
        end
      elsif key.to_s.downcase == "customerType"
        Sentry.set_tags('customerType': value)
      elsif key.to_s.downcase == "email"
        Sentry.set_tags('email': value)
      end
    end

    params.each do |key, value|
      if key.to_s.downcase == "se"
        Sentry.set_tags('se': value)
        # not tested yet
        if value.to_s.downcase == "tda"
          # Sentry.event.fingerprint = [value, ENV["RELEASE"]]
        else
          # Sentry.event.fingerprint = [value]
        end
      elsif key.to_s.downcase == "customerType"
        Sentry.set_tags('customerType': value)
      elsif key.to_s.downcase == "email"
        Sentry.set_tags('email': value)
      end
    end
  end
end
