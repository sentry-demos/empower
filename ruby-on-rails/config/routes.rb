Rails.application.routes.draw do

  get '/products', to: 'api/v1/products#index'

  get '/unhandled', to: 'api/v1/products#unhandled'

  get '/handled', to: 'api/v1/products#handled'

  get '/products-join', to: 'api/v1/productsjoin#index'

  get '/api', to: 'api/v1/api#index'

  get '/connect', to: 'api/v1/connect#index'

  get '/organization', to: 'api/v1/organization#index'

  get '/success', to: 'api/v1/success#index'

  get '/checkout', to: 'api/v1/checkout#index'

  root to: "api/v1/main#index"

  get '/*all', to: 'api/v1/products#default'

  # namespace :api do
  #   namespace :v1 do
  #     resources :products, only: [:index, :show, :create]
  #   end
  # end
  # For details on the DSL available within this file, see http://guides.rubyonrails.org/routing.html
end
