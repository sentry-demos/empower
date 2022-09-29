import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import './employee.css';
import * as Sentry from '@sentry/react';

function Employee() {
  const [employee, setEmployee] = useState();
  const { id } = useParams();

  useEffect(() => {
    const fetchData = async () => {
      const promise = await import(`./employees/${id}`);
      setEmployee(promise.default);
    };
    
    fetchData()
  }, [employee, id]);

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

export default Sentry.withProfiler(Employee, { name: "Employee"})
