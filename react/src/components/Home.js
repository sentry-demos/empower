import { Component } from 'react';
import Context from '../utils/context';
import * as Sentry from '@sentry/react';
import plantsBackground from '../assets/plants-background-img.jpg';
import Button from './ButtonLink';
import { crasher } from '../utils/errors';

const divStyle = {
    backgroundImage: 'url(' + plantsBackground + ')',
};


class Home extends Component {
    static contextType = Context;

    async shouldComponentUpdate() {
      console.log("> Home shouldComponentUpdate")
    }
  
    async componentDidMount() {
      // Crasher will parse the query params
      // setTimeout to make sure it's not executed in pageload stacktrace that results in source map
      // processing failures
      setTimeout(crasher, 1); 

      let se, customerType, email
      Sentry.withScope(function(scope) {
        [ se, customerType ] = [scope._tags.se, scope._tags.customerType ]
        email = scope._user.email
      });
      try {       
        // This should be the only http request for home page, for health check purposes
        await fetch(this.props.backend + "/success", {
          method: "GET",
          headers: { se, customerType, email, "Content-Type": "application/json" }
        })
      } catch(err) {
        Sentry.captureException(err);
      }
    }
  
    render() {
      return (
        <div className="hero">
          <div className="hero-bg-img" style={divStyle}></div>
          <div className="hero-content">
            <h1>Empower your plants</h1>
            <p>Keep your houseplants happy.</p>
            <Button to="/products">Browse products</Button>
          </div>
        </div>
      );
    }
    
  }
  
  export default Home;