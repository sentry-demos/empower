import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'react-router-dom';

function Employee() {
  const [employee, setEmployee] = useState();
  // TODO this wont work with next routing
  // const { id } = useParams();

  // useEffect(() => {
  //   const fetchData = async () => {
  //     const promise = await import(`@/src/components/employees/${id}`);
  //     setEmployee(promise.default);
  //   };

  //   fetchData();
  // }, [employee, id]);

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

export default Employee;
