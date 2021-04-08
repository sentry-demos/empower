import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import About from './components/About';
import Checkout from './components/Checkout';
import Cra from './components/Cra';
import Product from './components/Product';
import Products from './components/Products';

import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link,
} from "react-router-dom";

// from Creat New React App
// ReactDOM.render(
//   <React.StrictMode>
//     <AppOld />
//   </React.StrictMode>,
//   document.getElementById('root')
// );

// React-router in use here https://reactrouter.com/web/guides/quick-start
ReactDOM.render(
  <React.StrictMode>
    <Router>
      <div>
        {'<Navbar Start>'}
        <nav>
          <ul>
            <li>
              <Link to="/about">About</Link>
            </li>
            <li>
              <Link to="/checkout">Checkout</Link>
            </li>
            <li>
              <Link to="/cra">CreateReactApp Starter Page</Link>
            </li>
            <li>
              <Link to="/product/1">Product/:id</Link>
            </li>
            <li>
              <Link to="/products">Products</Link>
            </li>
            <li>
              <Link to="/">Home</Link>
            </li>
          </ul>
        {'<Navbar End>'}
        </nav>

        {'<React-Router\'s Switch components appear below:>'}
        <Switch>
          <Route path="/about">
            <About />
          </Route>
          <Route path="/checkout">
            <Checkout />
          </Route>
          <Route path="/cra">
            <Cra />
          </Route>
          <Route path="/product/:id" component={Product}>
          </Route>
          <Route path="/products">
            <Products />
          </Route>
          <Route exact path="/">
            <Home />
          </Route>
        </Switch>
      </div>
    </Router>
  </React.StrictMode>,
  document.getElementById('root')
)

function Home() {
  return <h2>Home</h2>;
}

// If you don't want a navbar, then you can remove it altogether, it would look like this:
/*
ReactDOM.render(
  <React.StrictMode>
    <Router>
        <Switch>
          <Route path="/about">
            <About />
          </Route>
          <Route path="/checkout">
            <Checkout />
          </Route>
          <Route path="/">
            <Home />
          </Route>
        </Switch>
    </Router>
  </React.StrictMode>,
  document.getElementById('root')
)
*/
