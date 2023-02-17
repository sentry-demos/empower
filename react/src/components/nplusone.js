import { Component } from 'react';
import Context from '../utils/context';
import { Link, useFetcher } from 'react-router-dom';
import * as Sentry from '@sentry/react';
import { connect } from 'react-redux';

console.log(this.props.backend);
// for loop to create 10 API calls and save them to variables.
for (let i = 0; i < 10; i++) {
  let response = fetch(this.props.backend + '/product/info?id=' + i) , {
    method: 'GET'
  })
} 

class Nplusone extends Component {
  
    render() {
        return (
          <div>
            <h1>API N+1 Performance Issue</h1>
              <h3>look at the query <a href="https://testorg-az.sentry.io/issues/?project=5808623&query=is%3Aunresolved+issue.type%3Aperformance_n_plus_one_api_calls&referrer=issue-list&statsPeriod=14d" rel="noreferrer">here</a></h3>
          </div>
        );
    }
}

export default Nplusone;