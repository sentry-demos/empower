<template>
<div class="loading-container">
<div v-if="loading" class="lds-ellipsis"><div></div><div></div><div></div><div></div></div>
</div>
<div v-if="!loading">
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
            <li v-for="employee in employees" :key="employee.name">
              <img v-bind:src="employee.img"/>
              <h5 className="employee-name" name={{employee.name}}>{{employee.name}}</h5>
            </li>
          </ul>
        </div>
      </div>
        <div className="testimonial-section">
          <h1>What Our Customers Say About Us</h1>
          <ul className="testimonial-list">
            <li v-for="renderedTestimonial in renderedTestimonials" :key="renderedTestimonial.name">
                <div>
                  <div className="testimonial-blob">
                  {{'"'}}{{renderedTestimonial.testimonial}}{{'"'}}
                  </div>
                  <div>
                  {{"-"}} {{renderedTestimonial.name}}
                  </div>
                </div>
            </li>
          </ul>
        </div>
      </div>
</template>

<script>
import * as Sentry from "@sentry/vue";
import Jane from '../components/employees/jane';
import Lily from '../components/employees/lily';
import Keith from '../components/employees/keith';
import Mason from '../components/employees/mason';
import Emma from '../components/employees/emma';
import Noah from '../components/employees/noah';

// importing massive json dumps so slow down performance
import testimonials from '../components/testimonials/testimonials.json'
import testimonials2 from '../components/testimonials/testimonials2.json'

const employees = [Jane, Lily, Keith, Mason, Emma, Noah];
const renderedTestimonials = [];

export default {
  data: function() {
    return { 
      employees: employees,
      renderedTestimonials: renderedTestimonials,
      loading: true 
    };
  },
  beforeCreate() {
    try {
    // Do this or the trace won't include the backend transaction
    const transaction = Sentry.getCurrentHub().getScope().getTransaction();
    let span = {};
    if (transaction) {
      span = transaction.startChild({
        op: "task",
        description: "load_testimonials",
    })}
    // performing unnecessary operations to further slow down performance
    const testimonialArray = []

    testimonials.forEach(eachTestimonial => {
      testimonialArray.push(eachTestimonial)
    })

    testimonials2.forEach(eachTestimonial => {
      testimonialArray.push(eachTestimonial)
    })

    // registering and rendering only the first five items of the entire dump
    for (let i=0; i<=4; i++) {
      renderedTestimonials.push(testimonialArray[i])
    }
    console.log('new',renderedTestimonials)

    setTimeout(() => {
      this.loading = false
      span.finish();
      transaction.finish();
    }, 5000)

    } catch (ex) {
      console.log(ex);
    }
    // finally {
    // span.finish();
    // transaction.finish();
    // }
  },
}

</script>

<style>
@media (min-width: 1px) {
  .about {
    min-height: 100vh;
    display: flex;
    align-items: center;
  }
  .about-page {
  text-align: left;
  margin: 0 auto;
  padding-top: 2rem;
  display: flex;
  flex-direction: column;
  margin-top: 3rem
}

.about-page > div {
  flex: 1;
}

.about-info {
  max-width: 45rem;
  margin: 0 auto;
  padding: 0 1rem 1rem;
}

.testimonial-section {
  text-align: center;
  margin: 0 auto;
  padding-top: 2rem;
  display: flex;
  flex-direction: column;
}

.testimonial-blob {
font-weight: bold;
}

@media screen and (min-width: 1200px) {
  .about-page {
    flex-direction: row;
  }

  .about-info {
    padding: 0 2rem 0 0;
  }
}

ul.employee-list {
  list-style: none;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  max-width: 500px;
  margin: 0 auto;
}

ul.employee-list li {
  flex: 0 0 50%;
  padding: 0 1rem;
  box-sizing: border-box;
  text-align: center;
}

ul.employee-list li a {
  text-decoration: none;
}

ul.employee-list li a:hover {
  opacity: 0.8;
}

ul.employee-list li h5 {
  margin: 0 0 2rem;
}

ul.employee-list li img {
  width: 100%;
  border-radius: 50%;
}

ul.testimonial-list {
  list-style: none;
  margin-top: 1rem;
}

ul.testimonial-list li {
  padding-bottom: 2rem;
  box-sizing: border-box;
  text-align: center;
}

ul.testimonial-list li a {
  text-decoration: none;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
}

.lds-ellipsis {
  display: inline-block;
  position: relative;
  width: 80px;
  height: 80px;
  }
  .lds-ellipsis div {
    position: absolute;
    top: 33px;
    width: 13px;
    height: 13px;
    border-radius: 50%;
    background: #dfc;
    animation-timing-function: cubic-bezier(0, 1, 1, 0);
  }
  .lds-ellipsis div:nth-child(1) {
    left: 8px;
    animation: lds-ellipsis1 0.6s infinite;
  }
  .lds-ellipsis div:nth-child(2) {
    left: 8px;
    animation: lds-ellipsis2 0.6s infinite;
  }
  .lds-ellipsis div:nth-child(3) {
    left: 32px;
    animation: lds-ellipsis2 0.6s infinite;
  }
  .lds-ellipsis div:nth-child(4) {
    left: 56px;
    animation: lds-ellipsis3 0.6s infinite;
  }
  @keyframes lds-ellipsis1 {
    0% {
      transform: scale(0);
    }
    100% {
      transform: scale(1);
    }
  }
  @keyframes lds-ellipsis3 {
    0% {
      transform: scale(1);
    }
    100% {
      transform: scale(0);
    }
  }
  @keyframes lds-ellipsis2 {
    0% {
      transform: translate(0, 0);
    }
    100% {
      transform: translate(24px, 0);
    }
  }
}
</style>
