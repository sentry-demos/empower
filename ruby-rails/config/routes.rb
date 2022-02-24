Rails.application.routes.draw do
  # Define your application routes per the DSL in https://guides.rubyonrails.org/routing.html

  # Defines the root path route ("/")
  # root "articles#index"
  
  
  # resources :api

  # scope '/api' do
  #   resources :api
  # end

  # get 'api/organization'
  # get 'organization', to: 'api/organization'
  # get 'organization'
  # get 'api'
  get 'api', to: 'api#api'

  get 'connect', to: 'api#connect'

  get 'organization', to: 'api#organization'

  get 'success', to: 'api#success'
end
