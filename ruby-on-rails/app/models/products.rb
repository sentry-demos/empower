class Products < ActiveRecord::Base
    has_one :inventory
end
