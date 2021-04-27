import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import './employee.css';

const Product = ({ match }) => {
  const [employee, setEmployee] = useState(null);

  useEffect(() => {
    (async () => {
      if (match.params.slug) {
        const data = await import(`./employees/${match.params.slug}`);
        setEmployee(data.default);
      }
    })();
  }, [match.params.slug]);

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
};

export default Product;
