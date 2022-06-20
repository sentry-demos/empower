<template>
      <div>
        <ul className="products-list">
          <li v-for="product in products" :key=product.id>
            <div>
                <img :src="product.img" :alt="'product'" />
                <div>
                  <h2>{{product.title}}</h2>
                  <p :className="'product-description'">
                    {{product.description}}
                  </p>
                </div>
              <!-- <button @click="onClick()"> -->
              <button @click="addToCartPrice(product.price)">
                Add to cart — {{product.price}}.00
              </button>
            </div>
          </li>
        </ul>
      </div>
</template>

<script>
import {useCounterStore} from '../stores/counter'

  export default { 
    // props: ['products']
    props: {
      products: Array,
      onClick: Function
      },
    methods: {
      addToCartPrice: function(price) {
        const store = useCounterStore()
        store.increment(price)
        console.log(store.counter)
    }
    }
  };
</script>

<style scoped>
.products-list {
  list-style: none;
  padding: 0 0 0;
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
}

.products-list li {
  flex-basis: 100%;
  margin-bottom: 2rem;
}

@media screen and (min-width: 600px) {
  .products-list li {
    flex-basis: calc(50% - 1rem);
  }
}

.products-list li > div {
  padding: 1.5rem;
  border-radius: 0.25rem;
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.07), 0 6px 20px 0 rgba(0, 0, 0, 0.05);
}

.products-list li img {
  width: 100%;
}

.products-list li a {
  text-decoration: none;
}

.loader-container {
  text-align: center;
}

button {
  font-family: 'Poppins', sans-serif;
}

button,
a.btn,
input[type='submit'] {
  -webkit-appearance: none;
  display: inline-block;
  background-color: #002626;
  color: #fff;
  padding: 0.75rem 1rem;
  line-height: 1.5;
  border-radius: 0.25em;
  border: none;
  text-decoration: none;
  font-size: 1rem;
  margin: 0.5rem 0;
}

button:hover,
a.btn:hover,
input[type='submit']:hover {
  cursor: pointer;
  background-color: #dddc4e;
  color: #002626;
}
button:active,
a.btn:active,
input[type='submit']:active {
  background-color: #f6cfb2;
}

</style>