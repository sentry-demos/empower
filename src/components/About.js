import { Component } from 'react';
import { Link } from 'react-router-dom';
import slugify from '../utils/slugify';
import * as Sentry from '@sentry/react';
import './about.css';

import Jane from './employees/jane';
import Lily from './employees/lily';
import Keith from './employees/keith';
import Mason from './employees/mason';
import Emma from './employees/emma';
import Noah from './employees/noah';

const employees = [Jane, Lily, Keith, Mason, Emma, Noah];

class About extends Component {
  render() {
    return (
      <div className="about-page">
        <div>
          <div className="about-info">
            <h1>About us</h1>
            <p>
              Empower Plant is an IoT company determined to keep house plants
              happy. After reading Michael Pollan’s 2013 New Yorker article
              (“The Intelligent Plant”), the wife-and-wife founding team
              invested their life savings in measuring and improving the
              emotional state of their leafy housemates. Seven years later, the
              company’s grown from its humble roots in the couples’ backyard
              greenhouse (converted from a garage) into a Series C-funded San
              Francisco startup and the world’s most accurate plant mood
              measurer (“a must-have for any responsible plant parent,”
              according to Plant Parenthood Magazine). Their original
              state-of-the-art product is a technological marvel built with a
              plant-first mindset, and they now offer a range of plant-centric
              options.
            </p>
            <p>
              Today, the company employs 170 people (and 852 plants) in San
              Francisco, New York City, Denver, and Kiev.
            </p>
          </div>
        </div>
        <div>
          <ul className="employee-list">
            {employees.map((employee) => {
              return (
                <li key={employee.name}>
                  <Link to={`/employee/${slugify(employee.url)}`}>
                    <img src={employee.img} alt={`${employee.name}`} />
                    <h5>{employee.name}</h5>
                  </Link>
                </li>
              );
            })}
          </ul>
        </div>
      </div>
    );
  }
}

// export default About;
export default Sentry.withProfiler(About, { name: "About"})
