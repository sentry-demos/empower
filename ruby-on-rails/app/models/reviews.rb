class Reviews < ActiveRecord::Base
    Sentry.logger.trace("Reviews model loaded")
    # may reuse below for a more elegant query
    #self.table_name = "review"
    #belongs_to :product#, foreign_key: "productid"
end