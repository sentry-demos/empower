import Link from 'next/link';

import slugify from '@/src/utils/slugify';
import { getAbout } from '@/lib/data';

import Jane from '@/public/employees/jane';
import Lily from '@/public/employees/lily';
import Keith from '@/public/employees/keith';
import Mason from '@/public/employees/mason';
import Emma from '@/public/employees/emma';
import Noah from '@/public/employees/noah';


const employees = [Jane, Lily, Keith, Mason, Emma, Noah];

export default function About() {
  // API calls to flask from server component to show more spans
  getAbout('flask');

  return (
    <div className="about-page">
      <div>
        <div className="about-info">
          <h1>About us</h1>
          <p>
            Empower Plant is an IoT company determined to keep house plants
            happy. After reading Michael Pollan’s 2013 New Yorker article (“The
            Intelligent Plant”), the wife-and-wife founding team invested their
            life savings in measuring and improving the emotional state of their
            leafy housemates. Seven years later, the company’s grown from its
            humble roots in the couples’ backyard greenhouse (converted from a
            garage) into a Series C-funded San Francisco startup and the world’s
            most accurate plant mood measurer (“a must-have for any responsible
            plant parent,” according to Plant Parenthood Magazine). Their
            original state-of-the-art product is a technological marvel built
            with a plant-first mindset, and they now offer a range of
            plant-centric options.
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
                <Link href={`/employee/${slugify(employee.url)}`}>
                  <img src={employee.img.src} alt={`${employee.name}`} />
                  <h5 className="employee-name" name={employee.name}>
                    {employee.name}
                  </h5>
                </Link>
              </li>
            );
          })}
        </ul>
      </div>
    </div>
  );
}

// export default Sentry.withProfiler(About, { name: 'About' });
