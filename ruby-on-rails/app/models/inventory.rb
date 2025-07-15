class Inventory < ActiveRecord::Base
    self.table_name = "inventory"
    belongs_to :product
    # may reuse below for a more elegant query
    #scope :for_product, ->(product) {where(product_id: product)}
    
    after_initialize :log_inventory_access
    
    def check_stock_level
        if self.respond_to?(:quantity) && self.quantity && self.quantity < 10
            Sentry.logger.warn("Low inventory level for product %{product_id}: %{quantity} remaining", 
                              product_id: self.product_id, quantity: self.quantity)
        end
    end
    
    private
    
    def log_inventory_access
        if new_record?
            Sentry.logger.debug("New inventory record created for product %{product_id}", 
                               product_id: self.product_id)
        else
            Sentry.logger.trace("Inventory record accessed for product %{product_id}", 
                               product_id: self.product_id)
        end
    end
end
