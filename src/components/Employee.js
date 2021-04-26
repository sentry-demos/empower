import React, { useEffect, useState } from 'react';
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
    <div>
      <div>
        <img src={employee.img} alt={employee.name} />
      </div>
      <div>
        <h1>{employee.name}</h1>
        <p>{employee.blurb}</p>
      </div>
    </div>
  ) : (
    <p>Loading…</p>
  );
};

export default Product;
