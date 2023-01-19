Rails.application.routes.draw do

  get '/products', to: 'api/v1/products#index'

  get '/unhandled', to: 'api/v1/products#unhandled'

  get '/handled', to: 'api/v1/products#handled'
  # namespace :api do
  #   namespace :v1 do
  #     resources :products, only: [:index, :show, :create]
  #   end
  # end
  # For details on the DSL available within this file, see http://guides.rubyonrails.org/routing.html
end
