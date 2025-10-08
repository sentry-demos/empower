class Inventory < ActiveRecord::Base
    Sentry.logger.trace("Inventory model loaded with product association")
    self.table_name = "inventory"
    belongs_to :product
    # may reuse below for a more elegant query
    #scope :for_product, ->(product) {where(product_id: product)}
end
