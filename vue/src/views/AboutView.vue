<template>
  <div class="about-page">
    <div class="about-layout">
      <div class="about-info">
        <h1>About us</h1>
        <p>
          Empower Plant is an IoT company determined to keep house plants
          happy. After reading Michael Pollan's 2013 New Yorker article
          ("The Intelligent Plant"), the wife-and-wife founding team
          invested their life savings in measuring and improving the
          emotional state of their leafy housemates. Seven years later, the
          company's grown from its humble roots in the couples' backyard
          greenhouse (converted from a garage) into a Series C-funded San
          Francisco startup and the world's most accurate plant mood
          measurer ("a must-have for any responsible plant parent,"
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
      <div class="employee-section">
        <ul class="employee-list">
          <li v-for="employee in employees" :key="employee.name">
            <img :src="employee.img" :alt="employee.name" />
            <h5 class="employee-name">{{ employee.name }}</h5>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import Jane from '../components/employees/jane';
import Lily from '../components/employees/lily';
import Keith from '../components/employees/keith';
import Mason from '../components/employees/mason';
import Emma from '../components/employees/emma';
import Noah from '../components/employees/noah';

const employees = [Jane, Lily, Keith, Mason, Emma, Noah];

export default {
  data() {
    return {
      employees,
    };
  },
}
</script>

<style scoped>
.about-page {
  max-width: 1100px;
  margin: 0 auto;
  padding: 2.5rem 2rem;
}

.about-layout {
  display: flex;
  gap: 4rem;
  align-items: flex-start;
}

.about-info {
  flex: 1;
  min-width: 0;
}

.about-info h1 {
  font-size: 1.6rem;
  font-weight: 600;
  color: #111;
  margin-bottom: 1.25rem;
}

.about-info p {
  color: #4b5563;
  line-height: 1.75;
  margin-bottom: 1rem;
  font-size: 0.95rem;
}

.employee-section {
  flex-shrink: 0;
  width: 320px;
}

.employee-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.employee-list li {
  text-align: center;
}

.employee-list li img {
  width: 100%;
  border-radius: 50%;
  aspect-ratio: 1;
  object-fit: cover;
}

.employee-name {
  margin-top: 0.5rem;
  font-size: 0.85rem;
  font-weight: 500;
  color: #374151;
}

@media (max-width: 768px) {
  .about-layout {
    flex-direction: column;
    gap: 2rem;
  }

  .employee-section {
    width: 100%;
  }
}
</style>
