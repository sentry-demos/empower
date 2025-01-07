class ProductSerializer < ActiveModel::Serializer
  attributes :id, :title, :description, :descriptionfull, :price, :img, :imgcropped, :pg_sleep, :reviews
  
  def reviews
    reviews_relation = object.reviews.select("id, productid, rating, customerid, description, created")
    reviews_relation.map do |review|
      {
        id: review.id,
        productid: review.productid,
        rating: review.rating,
        customerid: review.customerid,
        description: review.description,
        created: review.created,
        pg_sleep: nil
      }
    end
  end
end