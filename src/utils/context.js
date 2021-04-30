import React from 'react';

const Context = React.createContext({
  products: [],
  cart: { items: [] },
});

export default Context;
