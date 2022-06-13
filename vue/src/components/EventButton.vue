<template>
  <div>
   <button class="event-button" @click="onClick()">{{ title }}</button>  
  </div>
</template>

<script>
export default {
  name: "EventButton",
  props: {
    title: String,
    onClick: Function
  }
};
</script>

<style scoped>
.event-button {
  height: 60px;
  width: 600px;
  background-color: white;
  transition: 0.4s;
  color: black;
  margin-top: 0.6rem;
  font-size: 1.2rem;
  border-color: hsla(160, 100%, 37%, 1);
}

.event-button:hover {
  background-color: hsla(160, 100%, 37%, 1);
  color: white;
}
</style>
