import { Component } from 'react';
import Context from '../utils/context';
import { Link, useFetcher } from 'react-router-dom';
import * as Sentry from '@sentry/react';
import { connect } from 'react-redux';
import { determineBackendUrl } from '../utils/backendrouter';

function componentDidMount() {
  console.log(this.props);

  let urls = async () => {
    let i=0;
    let urllist=[]
    for(i;i< this.state.data.length;i++){
        const response = await fetch(this.props.backend + '/product/0/info?id=' + i)
        console.log(this);
        console.log(this.props.backend);
        console.log(this.props.backend + '/product/0/info?id=' + i);
        const json = await response.json()
        urllist.push(json.items[0])
        console.log({urllist})
      }
   }
  
  // fetch(for (let i = 0; i < 10; i++) {
  //   let response = fetch Promise.all(this.props.backend + '/product/0/info?id=' + i);
  // }) 
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