import { Component } from 'react';
import Context from '../utils/context';
import * as Sentry from '@sentry/react';
import plantsBackground from '../assets/plants-background-img.jpg';
import Button from './ButtonLink';

const divStyle = {
    backgroundImage: 'url(' + plantsBackground + ')',
};


class Home extends Component {
    static contextType = Context;
  
    async componentDidMount() {
      let se, customerType, email
      Sentry.withScope(function(scope) {
        [ se, customerType ] = [scope._tags.se, scope._tags.customerType ]
        email = scope._user.email
      });
      try {       
        // /success should always be called first 
        await fetch(`http://localhost:4567` + "/success", {
          method: "GET",
          headers: { se, customerType, email, "Content-Type": "application/json" }
        })

        // TODO - run these in parallel
        // https://stackoverflow.com/questions/35612428/call-async-await-functions-in-parallel
        // const finalResult = [await someResult, await anotherResult];
        // Promise.allSettled([happy('happy', 100), sad('sad', 50)]).then(console.log) // [{ "status":"fulfilled", "value":"happy" }, { "status":"rejected", "reason":"sad" }]
        await fetch(`http://localhost:4567` + "/api", {
          method: "GET",
          headers: { se, customerType, email, "Content-Type": "application/json" }
        })
        await fetch(`http://localhost:4567` + "/organization", {
          method: "GET",
          headers: { se, customerType, email, "Content-Type": "application/json" }
        })
        await fetch(`http://localhost:4567` + "/connect", {
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