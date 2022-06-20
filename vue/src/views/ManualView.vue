<template>
  <div class="about">
    <div id="app">
      <p id="greeting">{{greetingTxt}}</p>
      <div id="email-div">
        <input id="emailInput" v-model="userEmail" placeholder="Enter email..." type="email" />
        <button class="event-button" v-on:click="submitEmail">Submit</button>
      </div>
      <div id="event-list">
        <EventButton title="TypeError" :onClick="notAFunctionError" />
        <EventButton title="URIError" :onClick="uriError" />
        <EventButton title="SyntaxError" :onClick="syntaxError" />
        <EventButton title="RangeError" :onClick="rangeError" />
        <EventButton title="HTTP Request to Backend" :onClick="restError" />
      </div>
    </div>
  </div>
</template>

<script>
import EventButton from "../components/EventButton.vue";
import * as Sentry from "@sentry/vue";

const HELLO = "Enter User's email address: ";

//Required for distributed tracing outside of localhost
const tracingOrigins = ['localhost', 'empowerplant.io', 'run.app', 'appspot.com', /^\//];
const env = "dev";

export default {
  name: "app",
  components: {
    EventButton
  },
  data: function() {
    return { 
      greetingTxt: HELLO, 
      userEmail: "",
      products: [] 
    };
  },

  methods: {
    setEnvironment: function() {
      if (Math.floor(Math.random() * 100)%3 == 1) {
        this.env = "prod";
      } else if (Math.floor(Math.random() * 100)%3 == 0) {
        this.env = "dev";
      } else {
        this.env = "test";
      }
      console.log("Environment: " + this.env);
    },

    submitEmail: function() {
      Sentry.configureScope(scope => {
        scope.setUser({ email: this.userEmail });
      });
      var newGreeting = HELLO + " " + this.userEmail;
      this.$set(this.$data, "greetingTxt", newGreeting);
    },

    setRandomUser: function() {
      var chars = 'abcdefghijklmnopqrstuvwxyz1234567890';
      var string = '';
      for(var ii=0; ii<15; ii++){
        string += chars[Math.floor(Math.random() * chars.length)];
      }
      let randomEmail = string + "@sentry.io";
      Sentry.configureScope(scope => {
        scope.setUser({ email: randomEmail });
      });

      var newGreeting = HELLO + " " + randomEmail;
      this.$set(this.$data, "greetingTxt", newGreeting);
    },

    notAFunctionError: function() {
      console.log("notAFunctionError");
      var someArray = [{ func: function() {} }];
      someArray[1].func();
    },
    uriError: function() {
      console.log("uriError");
      decodeURIComponent("%");
    },

    syntaxError: function() {
      console.log("syntaxError");
      eval("foo bar");
    },

    rangeError: function() {
      console.log("rangeError");
      throw new RangeError("Parameter must be between 1 and 100");
    },

    restError: function() {
      const transaction = Sentry.startTransaction({ name: "manual-checkout" });
      // Do this or the trace won't include the backend transaction
      Sentry.getCurrentHub().configureScope(scope => scope.setSpan(transaction));
      //Sentry.configureScope(scope => scope.setSpan(transaction));

      console.log("restError...");
      console.log(transaction)
      const traceAndSpanID = transaction.traceId + "-" + transaction.spanId;
      // var myHeaders = new Headers();
      // myHeaders.append("Content-Type", "text/plain", );

      var raw = "{\"cart\":{\"items\":[{\"id\":4,\"title\":\"Botana Voice\",\"description\":\"Lets plants speak for themselves.\",\"descriptionfull\":\"Now we don't want him to get lonely, so we'll give him a little friend. Let your imagination just wonder around when you're doing these things. Let your imagination be your guide. Nature is so fantastic, enjoy it. Let it make you happy.\",\"price\":175,\"img\":\"https://storage.googleapis.com/application-monitoring/plant-to-text.jpg\",\"imgcropped\":\"https://storage.googleapis.com/application-monitoring/plant-to-text-cropped.jpg\",\"pg_sleep\":\"\",\"reviews\":[{\"id\":4,\"productid\":4,\"rating\":4,\"customerid\":null,\"description\":null,\"created\":\"2021-06-04 00:12:33.553939\",\"pg_sleep\":\"\"},{\"id\":5,\"productid\":4,\"rating\":3,\"customerid\":null,\"description\":null,\"created\":\"2021-06-04 00:12:45.558259\",\"pg_sleep\":\"\"},{\"id\":6,\"productid\":4,\"rating\":2,\"customerid\":null,\"description\":null,\"created\":\"2021-06-04 00:12:50.510322\",\"pg_sleep\":\"\"},{\"id\":13,\"productid\":4,\"rating\":3,\"customerid\":null,\"description\":null,\"created\":\"2021-07-01 00:12:43.312186\",\"pg_sleep\":\"\"},{\"id\":14,\"productid\":4,\"rating\":3,\"customerid\":null,\"description\":null,\"created\":\"2021-07-01 00:12:54.719873\",\"pg_sleep\":\"\"},{\"id\":15,\"productid\":4,\"rating\":3,\"customerid\":null,\"description\":null,\"created\":\"2021-07-01 00:12:57.760686\",\"pg_sleep\":\"\"},{\"id\":16,\"productid\":4,\"rating\":3,\"customerid\":null,\"description\":null,\"created\":\"2021-07-01 00:13:00.140407\",\"pg_sleep\":\"\"},{\"id\":17,\"productid\":4,\"rating\":3,\"customerid\":null,\"description\":null,\"created\":\"2021-07-01 00:13:00.971730\",\"pg_sleep\":\"\"},{\"id\":18,\"productid\":4,\"rating\":3,\"customerid\":null,\"description\":null,\"created\":\"2021-07-01 00:13:01.665798\",\"pg_sleep\":\"\"},{\"id\":19,\"productid\":4,\"rating\":3,\"customerid\":null,\"description\":null,\"created\":\"2021-07-01 00:13:02.278934\",\"pg_sleep\":\"\"}]}],\"quantities\":{\"4\":2},\"total\":350},\"form\":{\"loading\":false}}";
      
      var requestOptions = {
        method: 'POST',
        headers: {"Content-Type": "text/plain", "sentry-trace": traceAndSpanID},
        body: raw,
        redirect: 'follow'
      };

      fetch("https://application-monitoring-flask-dot-sales-engineering-sf.appspot.com/checkout", requestOptions)
        .then(function(response) {
          if (!response.ok) {
            const err = new Error(response.status + " -- " + (response.statusText || "Internal Server Error"));
            Sentry.captureException(err);
            console.error(err);
          }
          console.log("transaction.finish");
          transaction.finish();
        });      
    }
  },

  /*beforeMount() {
    console.log("beforeMount getProducts()");
    this.getProducts();
  },*/

  mounted() {
    this.setEnvironment();
    this.setRandomUser();
  }

}

</script>

<style>
@media (min-width: 1px) {
  .about {
    min-height: 100vh;
    display: flex;
    align-items: center;
  }
}
</style>