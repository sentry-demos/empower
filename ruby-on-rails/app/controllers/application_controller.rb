class ApplicationController < ActionController::API
    def set_Sentry_tags
        params.each do |key, value|
          if key == "se"
            Sentry.set_tags('se': value)
            # not tested yet
            if value == "tda"
                # Sentry.event.fingerprint = [value, ENV["RELEASE"]]
            else
                # Sentry.event.fingerprint = [value]
            end
          elsif key == "customerType"
            Sentry.set_tags('customerType': value)
          elsif key == "email"
            Sentry.set_tags('email': value)
          end
        end
    end
end
