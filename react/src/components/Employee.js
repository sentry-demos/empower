import React, { Component } from 'react';
import { Link } from 'react-router-dom';
import './employee.css';
import * as Sentry from '@sentry/react';

class Employee extends Component {
  constructor() {
    super();
    this.state = {
      employee: null,
    };
  }

  async shouldComponentUpdate() {
    console.log("> Employee shouldComponentUpdate")
  }

  async componentDidMount() {
    const { match } = this.props;
    if (match.params.id) {
      const data = await import(`./employees/${match.params.id}`);
      this.setState({ employee: data.default });
    }
  }
  render() {
    const { employee } = this.state;
    return employee ? (
      <div className="employee-page">
        <div className="employee-image">
          <img src={employee.img} alt={employee.name} />
        </div>
        <div className="employee-info">
          <Link to="/about">Back</Link>
          <h1>{employee.name}</h1>
          <p>{employee.bio}</p>
        </div>
      </div>
    ) : (
      <p>Loading…</p>
    );
  }
}

export default Sentry.withProfiler(Employee, { name: "Employee"})