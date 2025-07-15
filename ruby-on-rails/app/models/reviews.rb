class Reviews < ActiveRecord::Base
    # may reuse below for a more elegant query
    #self.table_name = "review"
    #belongs_to :product#, foreign_key: "productid"
    
    after_initialize :log_review_access
    after_create :log_review_creation
    
    private
    
    def log_review_access
        if new_record?
            Sentry.logger.debug("New review instance created for product %{product_id}", 
                               product_id: self.productid)
        else
            Sentry.logger.trace("Review loaded: ID %{id} for product %{product_id}", 
                               id: self.id, product_id: self.productid)
        end
    end
    
    def log_review_creation
        rating = self.rating || 0
        if rating <= 2
            Sentry.logger.warn("Low rating review created: %{rating} stars for product %{product_id}", 
                              rating: rating, product_id: self.productid)
        else
            Sentry.logger.info("New review created: %{rating} stars for product %{product_id}", 
                              rating: rating, product_id: self.productid)
        end
    end
end