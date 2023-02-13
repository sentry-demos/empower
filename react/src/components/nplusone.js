import { Component } from 'react';
import Context from '../utils/context';
import { Link } from 'react-router-dom';
import * as Sentry from '@sentry/react';
import { connect } from 'react-redux';

class Nplusone extends Component {
    render() {
        return (
          <h2>API N+1</h2>
        );
    }
}

    export default Nplusone;