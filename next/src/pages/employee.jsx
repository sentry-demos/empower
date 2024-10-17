import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import Link from 'next/link';
import '../styles/employee.css';
import * as Sentry from '@sentry/nextjs';

function Employee() {
  const [employee, setEmployee] = useState();
  const { id } = useParams();

  useEffect(() => {
    const fetchData = async () => {
      const promise = await import(`../components/employees/${id}`);
      setEmployee(promise.default);
    };

    fetchData();
  }, [employee, id]);

  return employee ? (
    <div className="employee-page">
      <div className="employee-image">
        <img src={employee.img} alt={employee.name} />
      </div>
      <div className="employee-info">
        <Link href="/about">Back</Link>
        <h1>{employee.name}</h1>
        <p>{employee.bio}</p>
      </div>
    </div>
  ) : (
    <p>Loading…</p>
  );
}

export default Sentry.withProfiler(Employee, { name: 'Employee' });
