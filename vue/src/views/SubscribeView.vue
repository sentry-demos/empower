<template>
  <div class="subscribe">
    <div id="app">
    <h1 class="subscribe-header">Sign up for plant tech news</h1>
    <div class="email-div">
        <p class="subscribe-error-message">{{emailError}}</p>
        <input class="subscribe-email-input" placeholder="Enter your email address" v-model="userEmail"/>
        <button class="subscribe-button" v-on:click="submitEmail">Submit</button>
    </div>
    </div>
  </div>
</template>

<script>
import EventButton from "../components/EventButton.vue";
import * as Sentry from "@sentry/vue";
import isEmail from 'validator/lib/isEmail';

// Generating Type error
let num = 11;
try {
    num.toUpperCase()
} catch (err) {
    console.error(err)
    Sentry.captureException(err)
}

// Generating Syntax error
try {
    eval("foo bar");
} catch (err) {
    console.error(err)
    Sentry.captureException(err)
}

export default {
  name: "app",
  components: {
    EventButton
  },
  data: function() {
    return { 
      userEmail: "",
      emailError: '',
    };
  },

  methods: {
    submitEmail: function() {
      Sentry.configureScope(scope => {
        scope.setUser({ email: this.userEmail });
      });
        try {
        if (isEmail(this.userEmail) === true) {
            throw new Error('Invalid Email Format');
        }
        } catch (err){
            Sentry.captureException(err);
            console.log(err)
            this.emailError = 'Email format is invalid'
        }
        this.userEmail = ''
        setTimeout(() => {
            this.emailError = ''
        }, 3000)
    },
  },
}

</script>

<style>
@media (min-width: 1px) {
  .subscribe {
    min-height: 50vh;
    display: flex;
    align-items: center;
  }
  .email-div {
      margin-top: 2rem;
  }
  .subscribe-error-message {
      color: red;
  }
  .subscribe-button {
  font-family: 'Poppins', sans-serif;
  width: 100%;
    }

    .subscribe-button {
    -webkit-appearance: none;
    display: inline-block;
    background-color: #002626;
    color: #fff;
    padding: 0.75rem 1rem;
    line-height: 1.5;
    border-radius: 0.25em;
    border: none;
    text-decoration: none;
    font-size: 1rem;
    margin: 0.5rem 0;
    }

    .subscribe-button:hover {
    cursor: pointer;
    background-color: #dddc4e;
    color: #002626;
    }
   .subscribe-button:active {
    background-color: #f6cfb2;
    }

    .subscribe-email-input {
    padding: 0.5rem;
    display: block;
    width: 100%;
    box-sizing: border-box;
    }

    .subscribe-email-input {
    display: block;
    margin: 0.5rem auto 1rem;
    line-height: 1.5;
    font-size: 1.25rem;
    border: 1px solid;
    border-radius: 0.25em;
    }
}
</style>