FROM ruby:3.1-slim-bookworm

WORKDIR /src

COPY Gemfile Gemfile.lock .
RUN bundle install

COPY . .

CMD ["ruby", "main.rb", "-o", "0.0.0.0"]
